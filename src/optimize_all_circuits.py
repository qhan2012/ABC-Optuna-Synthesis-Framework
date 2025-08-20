#!/usr/bin/env python3
"""
Comprehensive ABC optimization for ALL circuits
Handles both Verilog files (working circuits) and AIG files (sorting circuits)
"""

import optuna
import subprocess
import time
import os
import json
import re
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ABCExecutionResult:
    """Result of ABC execution"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = -1
    execution_time: float = 0.0
    output_file: str = ""
    error_type: str = ""
    error_details: str = ""
    lut_count: Optional[int] = None

class ABCRunMonitor:
    """Monitor ABC execution and validate results"""
    
    def __init__(self):
        self.success_criteria = {
            'exit_code': 0,
            'has_output': True,
            'output_size': '> 0KB',
            'luts_counted': True,
            'timeout': False
        }
    
    def monitor_execution(self, script_content: str, circuit_dir: str, output_file: str, timeout: int = 300) -> ABCExecutionResult:
        """Monitor ABC execution in real-time"""
        start_time = time.time()
        
        try:
            # Create script file
            script_file = os.path.join(circuit_dir, "optuna_script.abc")
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            # Change to circuit directory and run ABC
            original_dir = os.getcwd()
            os.chdir(circuit_dir)
            
            result = subprocess.run(
                ['/home/qiang/Applications/abc/abc-master/abc', '-f', 'optuna_script.abc'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Change back to original directory
            os.chdir(original_dir)
            
            execution_time = time.time() - start_time
            
            # Validate results
            if result.returncode == 0:
                # Check if output file was generated
                output_path = os.path.join(circuit_dir, output_file)
                if os.path.exists(output_path):
                    # Count LUTs
                    try:
                        lut_count = self.count_luts(output_path)
                        file_size = os.path.getsize(output_path)
                        
                        if lut_count > 0 and file_size > 0:
                            return ABCExecutionResult(
                                success=True,
                                stdout=result.stdout,
                                stderr=result.stderr,
                                returncode=result.returncode,
                                execution_time=execution_time,
                                output_file=output_path,
                                lut_count=lut_count
                            )
                        else:
                            return ABCExecutionResult(
                                success=False,
                                stdout=result.stdout,
                                stderr=result.stderr,
                                returncode=result.returncode,
                                execution_time=execution_time,
                                error_type="validation_failed",
                                error_details=f"LUT count: {lut_count}, File size: {file_size}"
                            )
                    except Exception as e:
                        return ABCExecutionResult(
                            success=False,
                            stdout=result.stdout,
                            stderr=result.stderr,
                            returncode=result.returncode,
                            execution_time=execution_time,
                            error_type="lut_counting_error",
                            error_details=str(e)
                        )
                else:
                    return ABCExecutionResult(
                        success=False,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        returncode=result.returncode,
                        execution_time=execution_time,
                        error_type="output_file_missing",
                        error_details=f"Expected file: {output_path}"
                    )
            else:
                return ABCExecutionResult(
                    success=False,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                    execution_time=execution_time,
                    error_type="abc_execution_failed",
                    error_details=f"ABC returned code: {result.returncode}"
                )
                
        except subprocess.TimeoutExpired:
            return ABCExecutionResult(
                success=False,
                execution_time=timeout,
                error_type="timeout",
                error_details=f"Execution timed out after {timeout} seconds"
            )
        except Exception as e:
            return ABCExecutionResult(
                success=False,
                error_type="unexpected_error",
                error_details=str(e)
            )
    
    def count_luts(self, blif_file: str) -> int:
        """Count LUTs in BLIF file"""
        try:
            result = subprocess.run(
                ['grep', '-c', '^.names', blif_file],
                capture_output=True, text=True, check=True
            )
            return int(result.stdout.strip())
        except Exception as e:
            logger.error(f"Failed to count LUTs: {e}")
            return 0
    
    def extract_max_level(self, abc_output: str) -> int:
        """Extract maximum level from ABC print_level output"""
        try:
            # Find all level lines and extract the maximum
            level_lines = [line for line in abc_output.split('\n') if 'Level =' in line]
            if not level_lines:
                return 0
            
            # Extract level numbers and find the maximum
            levels = []
            for line in level_lines:
                match = re.search(r'Level\s*=\s*(\d+)', line)
                if match:
                    levels.append(int(match.group(1)))
            
            return max(levels) if levels else 0
        except Exception as e:
            logger.error(f"Failed to extract level: {e}")
            return 0

def validate_parameters(params: Dict[str, int]) -> bool:
    """Validate parameter constraints"""
    # Basic range validation
    if not (1 <= params['balance1_l'] <= 20):
        return False
    if not (4 <= params['resub1_K'] <= 8):
        return False
    if not (1 <= params['resub1_N'] <= 3):  # ABC limit is 3
        return False
    if not (4 <= params['resub2_K'] <= 8):
        return False
    if not (1 <= params['resub2_N'] <= 3):  # ABC limit is 3
        return False
    if not (1 <= params['balance2_l'] <= 20):
        return False
    if not (4 <= params['if_K'] <= 6):  # Constrained to K=6
        return False
    
    # Logical constraints
    if params['resub1_K'] > params['if_K']:
        return False
    if params['resub2_K'] > params['if_K']:
        return False
    
    return True

def create_abc_script_verilog(verilog_file: str, params: Dict[str, int]) -> str:
    """Create ABC script for Verilog files"""
    return f"""read {verilog_file}
strash
balance -l {params['balance1_l']}
resub -K {params['resub1_K']} -N {params['resub1_N']}
resub -K {params['resub2_K']} -N {params['resub2_N']}
balance -l {params['balance2_l']}
if -K {params['if_K']}
print_level
write_blif optimized_optuna.blif"""

def create_abc_script_aig(aig_file: str, params: Dict[str, int]) -> str:
    """Create ABC script for AIG files"""
    return f"""read {aig_file}
strash
balance -l {params['balance1_l']}
resub -K {params['resub1_K']} -N {params['resub1_N']}
resub -K {params['resub2_K']} -N {params['resub2_N']}
balance -l {params['balance2_l']}
if -K {params['if_K']}
print_level
write_blif optimized_optuna.blif"""

def get_circuit_file(circuit_dir: str) -> tuple[str, str]:
    """Get the appropriate input file for a circuit (Verilog or AIG)"""
    # Check for AIG files first (for sorting circuits)
    aig_files = [f for f in os.listdir(circuit_dir) 
                 if f.endswith('.aig') and not f.startswith('._')]
    if aig_files:
        return aig_files[0], "aig"
    
    # Check for Verilog files (for working circuits)
    verilog_files = [f for f in os.listdir(circuit_dir) 
                     if f.endswith('.v') and not f.startswith('._')]
    if verilog_files:
        return verilog_files[0], "verilog"
    
    return None, None

def objective_factory(circuit_dir: str, input_file: str, file_type: str, monitor: ABCRunMonitor, baseline_level: int):
    """Create objective function for a specific circuit with level constraint"""
    def objective(trial: optuna.Trial) -> float:
        # Generate parameters
        params = {
            'balance1_l': trial.suggest_int('balance1_l', 1, 20),
            'resub1_K': trial.suggest_int('resub1_K', 4, 8),
            'resub1_N': trial.suggest_int('resub1_N', 1, 3),
            'resub2_K': trial.suggest_int('resub2_K', 4, 8),
            'resub2_N': trial.suggest_int('resub2_N', 1, 3),
            'balance2_l': trial.suggest_int('balance2_l', 1, 20),
            'if_K': trial.suggest_int('if_K', 4, 6)
        }
        
        # Validate parameters
        if not validate_parameters(params):
            return float('inf')
        
        # Create appropriate ABC script based on file type
        if file_type == "aig":
            script_content = create_abc_script_aig(input_file, params)
        else:
            script_content = create_abc_script_verilog(input_file, params)
        
        result = monitor.monitor_execution(script_content, circuit_dir, "optimized_optuna.blif")
        
        if result.success:
            # Check level constraint first (only if baseline_level > 0)
            new_level = monitor.extract_max_level(result.stdout)
            
            if baseline_level > 0 and new_level > baseline_level * 1.10:
                # Level constraint violated - reject this trial
                trial.set_user_attr('level_constraint_violated', True)
                trial.set_user_attr('new_level', new_level)
                trial.set_user_attr('baseline_level', baseline_level)
                logger.warning(f"Level constraint violated: {new_level} > {baseline_level} * 1.10 = {baseline_level * 1.10:.1f}")
                return float('inf')
            
            # Count LUTs in output file
            try:
                lut_count = monitor.count_luts(result.output_file)
                trial.set_user_attr('file_size', os.path.getsize(result.output_file))
                trial.set_user_attr('execution_time', result.execution_time)
                trial.set_user_attr('parameters', params)
                trial.set_user_attr('file_type', file_type)
                trial.set_user_attr('level_constraint_violated', False)
                trial.set_user_attr('new_level', new_level)
                trial.set_user_attr('baseline_level', baseline_level)
                return float(lut_count)
            except Exception as e:
                logger.error(f"Failed to count LUTs: {e}")
                return float('inf')
        else:
            # Log failed trial
            logger.warning(f"Trial failed: {result.error_type} - {result.error_details}")
            trial.set_user_attr('error_type', result.error_type)
            trial.set_user_attr('error_details', result.error_details)
            return float('inf')
    
    return objective

def optimize_circuit(circuit_name: str, n_trials: int = 30, timeout: int = 900):
    """Optimize a single circuit"""
    print(f"\n🚀 Starting optimization for {circuit_name}")
    print("=" * 60)
    
    circuit_dir = circuit_name
    if not os.path.exists(circuit_dir):
        print(f"❌ Circuit directory {circuit_dir} not found")
        return None
    
    # Get input file and type
    input_file, file_type = get_circuit_file(circuit_dir)
    if not input_file:
        print(f"❌ No input file found in {circuit_dir}")
        return None
    
    print(f"📁 Input file: {input_file} ({file_type.upper()})")
    
    # Create study
    study_name = f"abc_optimization_{circuit_name}"
    study = optuna.create_study(
        study_name=study_name,
        storage=f"sqlite:///optuna_{circuit_name}.db",
        load_if_exists=True,
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    # Create monitor and objective function
    monitor = ABCRunMonitor()
    
    # Get baseline level for the circuit from baseline results
    baseline_level = 0
    baseline_file = 'baseline_results_all_circuits.json'
    if os.path.exists(baseline_file):
        try:
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
            
            # Find the circuit in baseline results
            for circuit_result in baseline_data.get('circuit_results', []):
                if circuit_result['circuit'] == circuit_name and circuit_result['success']:
                    baseline_level = circuit_result.get('baseline_level', 0)
                    print(f"📊 Baseline level for {circuit_name}: {baseline_level}")
                    break
        except Exception as e:
            logger.warning(f"Failed to load baseline level for {circuit_name}: {e}")
            baseline_level = 0
    else:
        logger.warning(f"Baseline results file not found: {baseline_file}")
        baseline_level = 0
    
    if baseline_level == 0:
        print(f"⚠️  Warning: No baseline level found for {circuit_name}. Level constraint will be disabled.")
    
    objective = objective_factory(circuit_dir, input_file, file_type, monitor, baseline_level)
    
    # Run optimization
    print(f"🔧 Running {n_trials} trials...")
    study.optimize(objective, n_trials=n_trials, timeout=timeout)
    
    # Get best result
    if study.best_trial:
        best_params = study.best_trial.user_attrs.get('parameters', {})
        best_luts = study.best_trial.value
        best_file_size = study.best_trial.user_attrs.get('file_size', 0)
        file_type_used = study.best_trial.user_attrs.get('file_type', 'unknown')
        best_level = study.best_trial.user_attrs.get('new_level', 0)
        baseline_level_used = study.best_trial.user_attrs.get('baseline_level', 0)
        
        print(f"🏆 Best result for {circuit_name}:")
        print(f"   LUTs: {best_luts}")
        print(f"   Level: {best_level}")
        if baseline_level_used > 0:
            print(f"   Baseline Level: {baseline_level_used}")
            print(f"   Level Constraint: <= {baseline_level_used * 1.10:.1f} (110% of baseline)")
        print(f"   File size: {best_file_size / 1024:.1f} KB")
        print(f"   File type: {file_type_used.upper()}")
        print(f"   Parameters: {best_params}")
        
        # Save best parameters
        best_params_file = os.path.join(circuit_dir, f"best_parameters_{circuit_name}.json")
        with open(best_params_file, 'w') as f:
            json.dump({
                'circuit': circuit_name,
                'best_luts': best_luts,
                'best_level': best_level,
                'baseline_level': baseline_level_used,
                'level_constraint': f"<= {baseline_level_used * 1.10:.1f} (110% of baseline)" if baseline_level_used > 0 else "None",
                'best_file_size': best_file_size,
                'file_type': file_type_used,
                'parameters': best_params,
                'n_trials': len(study.trials),
                'optimization_time': datetime.now().isoformat()
            }, f, indent=2)
        
        # Create best ABC script
        if file_type_used == "aig":
            best_script = create_abc_script_aig(input_file, best_params)
        else:
            best_script = create_abc_script_verilog(input_file, best_params)
        
        best_script_file = os.path.join(circuit_dir, f"best_script_{circuit_name}.abc")
        with open(best_script_file, 'w') as f:
            f.write(best_script)
        
        print(f"💾 Best parameters saved to: {best_params_file}")
        print(f"💾 Best script saved to: {best_script_file}")
        
        return {
            'circuit': circuit_name,
            'best_luts': best_luts,
            'best_level': best_level,
            'baseline_level': baseline_level_used,
            'level_constraint_applied': baseline_level_used > 0,
            'level_constraint_limit': baseline_level_used * 1.10 if baseline_level_used > 0 else 0,
            'best_file_size': best_file_size,
            'file_type': file_type_used,
            'best_params': best_params,
            'n_trials': len(study.trials)
        }
    else:
        print(f"❌ No successful trials for {circuit_name}")
        return None

def main():
    """Main optimization function"""
    print("🚀 ABC OPTIMIZATION FOR ALL CIRCUITS (Verilog + AIG)")
    print("=" * 80)
    
    # All circuits (both working and sorting)
    all_circuits = [
        'adder', 'max', 'mem_ctrl', 'voter',  # Working circuits (Verilog)
        'sort_16x16b_bitonic_l3', 'sort_32x8b_bitonic_l2', 
        'sort_32x8b_bitonic_l6', 'sort_32x16b_bitonic_l4'  # Sorting circuits (AIG)
    ]
    
    all_results = []
    
    for circuit in all_circuits:
        print(f"\n{'='*20} {circuit.upper()} {'='*20}")
        
        # Run optimization
        result = optimize_circuit(circuit, n_trials=20, timeout=600)
        
        if result:
            all_results.append(result)
        
        print("-" * 60)
    
    # Print summary
    print("\n" + "=" * 80)
    print("🏆 COMPREHENSIVE OPTIMIZATION SUMMARY")
    print("=" * 80)
    
    print(f"{'Circuit':<30} {'File Type':<8} {'Best LUTs':<12} {'File Size':<12} {'Trials':<8}")
    print("-" * 80)
    
    total_luts = 0
    total_trials = 0
    verilog_circuits = 0
    aig_circuits = 0
    
    for result in all_results:
        circuit = result['circuit']
        file_type = result['file_type']
        luts = result['best_luts']
        size_kb = result['best_file_size'] / 1024
        trials = result['n_trials']
        
        print(f"{circuit:<30} {file_type.upper():<8} {luts:<12} {size_kb:>8.1f} KB {trials:<8}")
        
        total_luts += luts
        total_trials += trials
        
        if file_type == "verilog":
            verilog_circuits += 1
        else:
            aig_circuits += 1
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {'MIXED':<8} {total_luts:<12} {total_trials:<8}")
    
    print(f"\n📊 CIRCUIT BREAKDOWN:")
    print(f"   Verilog circuits: {verilog_circuits}")
    print(f"   AIG circuits: {aig_circuits}")
    print(f"   Total circuits: {len(all_results)}")
    print(f"   Total LUTs: {total_luts:,}")
    print(f"   Total trials: {total_trials}")
    
    # Save overall results
    overall_results = {
        'optimization_date': datetime.now().isoformat(),
        'total_circuits': len(all_results),
        'verilog_circuits': verilog_circuits,
        'aig_circuits': aig_circuits,
        'total_luts': total_luts,
        'total_trials': total_trials,
        'circuit_results': all_results
    }
    
    with open('comprehensive_optimization_results.json', 'w') as f:
        json.dump(overall_results, f, indent=2)
    
    print(f"\n✅ Comprehensive results saved to: comprehensive_optimization_results.json")
    print("🎯 All-circuit optimization completed successfully!")

if __name__ == "__main__":
    main()


