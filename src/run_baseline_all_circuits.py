#!/usr/bin/env python3
"""
Run baseline ABC optimization on all 8 circuits
Baseline: strash; balance; resub; resub; balance; if -K 6; write_blif baseline.blif
"""

import subprocess
import os
import json
from datetime import datetime
from pathlib import Path
import re # Added for extract_max_level

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

def create_baseline_script(input_file: str, file_type: str) -> str:
    """Create baseline ABC script"""
    return f"""read {input_file}
strash
balance
resub
resub
balance
if -K 6
print_level
write_blif baseline.blif"""

def count_luts(blif_file: str) -> int:
    """Count LUTs in BLIF file"""
    try:
        result = subprocess.run(
            ['grep', '-c', '^.names', blif_file],
            capture_output=True, text=True, check=True
        )
        return int(result.stdout.strip())
    except Exception as e:
        print(f"Warning: Failed to count LUTs: {e}")
        return 0

def extract_max_level(abc_output: str) -> int:
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
        print(f"Warning: Failed to extract level: {e}")
        return 0

def run_baseline_for_circuit(circuit_name: str) -> dict:
    """Run baseline optimization for a single circuit"""
    print(f"\n🔧 Running baseline for {circuit_name}")
    print("=" * 50)
    
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
    
    # Create baseline script
    script_content = create_baseline_script(input_file, file_type)
    script_file = os.path.join(circuit_dir, "baseline_script.abc")
    
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"📝 Created baseline script: {script_file}")
    
    # Run ABC
    try:
        # Change to circuit directory and run ABC
        original_dir = os.getcwd()
        os.chdir(circuit_dir)
        
        print("🚀 Running ABC baseline optimization...")
        result = subprocess.run(
            ['/home/qiang/Applications/abc/abc-master/abc', '-f', 'baseline_script.abc'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Change back to original directory
        os.chdir(original_dir)
        
        if result.returncode == 0:
            # Check if output file was generated
            baseline_blif = os.path.join(circuit_dir, "baseline.blif")
            if os.path.exists(baseline_blif):
                # Count LUTs and get file size
                lut_count = count_luts(baseline_blif)
                file_size = os.path.getsize(baseline_blif)
                
                # Extract maximum level from ABC output
                max_level = extract_max_level(result.stdout)
                
                print(f"✅ Baseline completed successfully!")
                print(f"   LUTs: {lut_count}")
                print(f"   Max Level: {max_level}")
                print(f"   File size: {file_size / 1024:.1f} KB")
                
                return {
                    'circuit': circuit_name,
                    'file_type': file_type,
                    'input_file': input_file,
                    'baseline_luts': lut_count,
                    'baseline_level': max_level,
                    'baseline_file_size': file_size,
                    'success': True
                }
            else:
                print(f"❌ Baseline BLIF file not generated")
                return {
                    'circuit': circuit_name,
                    'file_type': file_type,
                    'input_file': input_file,
                    'success': False,
                    'error': 'BLIF file not generated'
                }
        else:
            print(f"❌ ABC execution failed")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            
            return {
                'circuit': circuit_name,
                'file_type': file_type,
                'input_file': input_file,
                'success': False,
                'error': f'ABC returned code {result.returncode}',
                'stderr': result.stderr.strip()
            }
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Execution timed out")
        return {
            'circuit': circuit_name,
            'file_type': file_type,
            'input_file': input_file,
            'success': False,
            'error': 'Execution timed out'
        }
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return {
            'circuit': circuit_name,
            'file_type': file_type,
            'input_file': input_file,
            'success': False,
            'error': str(e)
        }

def main():
    """Main function to run baseline on all circuits"""
    print("🚀 BASELINE ABC OPTIMIZATION FOR ALL 8 CIRCUITS")
    print("=" * 80)
    print("Baseline script: strash; balance; resub; resub; balance; if -K 6; write_blif baseline.blif")
    print("=" * 80)
    
    # All circuits
    all_circuits = [
        'adder', 'max', 'mem_ctrl', 'voter',  # Working circuits
        'sort_16x16b_bitonic_l3', 'sort_32x8b_bitonic_l2', 
        'sort_32x8b_bitonic_l6', 'sort_32x16b_bitonic_l4'  # Sorting circuits
    ]
    
    all_results = []
    successful_circuits = 0
    total_baseline_luts = 0
    
    for circuit in all_circuits:
        print(f"\n{'='*20} {circuit.upper()} {'='*20}")
        
        # Run baseline
        result = run_baseline_for_circuit(circuit)
        
        if result:
            all_results.append(result)
            if result['success']:
                successful_circuits += 1
                total_baseline_luts += result['baseline_luts']
        
        print("-" * 50)
    
    # Print summary
    print("\n" + "=" * 80)
    print("🏆 BASELINE OPTIMIZATION SUMMARY")
    print("=" * 80)
    
    print(f"{'Circuit':<30} {'File Type':<8} {'Baseline LUTs':<15} {'Baseline Level':<15} {'File Size':<12} {'Status':<10}")
    print("-" * 80)
    
    for result in all_results:
        circuit = result['circuit']
        file_type = result['file_type']
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        
        if result['success']:
            luts = result['baseline_luts']
            level = result['baseline_level']
            size_kb = result['baseline_file_size'] / 1024
            print(f"{circuit:<30} {file_type.upper():<8} {luts:<15} {level:<15} {size_kb:>8.1f} KB {status:<10}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"{circuit:<30} {file_type.upper():<8} {'N/A':<15} {'N/A':<15} {'N/A':>8} KB {status:<10}")
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {'MIXED':<8} {total_baseline_luts:<15}")
    
    print(f"\n📊 BASELINE RESULTS:")
    print(f"   Successful circuits: {successful_circuits}/{len(all_circuits)}")
    print(f"   Failed circuits: {len(all_circuits) - successful_circuits}/{len(all_circuits)}")
    print(f"   Success rate: {successful_circuits/len(all_circuits)*100:.1f}%")
    print(f"   Total baseline LUTs: {total_baseline_luts:,}")
    
    # Save results
    baseline_results = {
        'baseline_date': datetime.now().isoformat(),
        'total_circuits': len(all_circuits),
        'successful_circuits': successful_circuits,
        'failed_circuits': len(all_circuits) - successful_circuits,
        'success_rate': successful_circuits/len(all_circuits)*100,
        'total_baseline_luts': total_baseline_luts,
        'circuit_results': all_results
    }
    
    with open('baseline_results_all_circuits.json', 'w') as f:
        json.dump(baseline_results, f, indent=2)
    
    print(f"\n✅ Baseline results saved to: baseline_results_all_circuits.json")
    
    # Now compare with optimized results if available
    if os.path.exists('comprehensive_optimization_results.json'):
        print(f"\n🔍 COMPARISON WITH OPTIMIZED RESULTS")
        print("=" * 80)
        
        with open('comprehensive_optimization_results.json', 'r') as f:
            opt_results = json.load(f)
        
        print(f"{'Circuit':<30} {'Baseline':<10} {'Optimized':<10} {'Improvement':<12}")
        print("-" * 80)
        
        total_improvement = 0
        circuits_with_improvement = 0
        
        for baseline_result in all_results:
            if not baseline_result['success']:
                continue
                
            circuit = baseline_result['circuit']
            baseline_luts = baseline_result['baseline_luts']
            
            # Find corresponding optimized result
            opt_result = None
            for opt in opt_results['circuit_results']:
                if opt['circuit'] == circuit:
                    opt_result = opt
                    break
            
            if opt_result:
                optimized_luts = opt_result['best_luts']
                improvement = baseline_luts - optimized_luts
                improvement_pct = (improvement / baseline_luts) * 100 if baseline_luts > 0 else 0
                
                if improvement > 0:
                    total_improvement += improvement
                    circuits_with_improvement += 1
                    status = f"✅ {improvement_pct:.1f}%"
                else:
                    status = f"⚠️  {improvement_pct:.1f}%"
                
                print(f"{circuit:<30} {baseline_luts:<10} {optimized_luts:<10} {status:<12}")
            else:
                print(f"{circuit:<30} {baseline_luts:<10} {'N/A':<10} {'N/A':<12}")
        
        print("-" * 80)
        print(f"📊 OPTIMIZATION SUMMARY:")
        print(f"   Circuits with improvement: {circuits_with_improvement}")
        print(f"   Total LUT improvement: {total_improvement:,}")
        print(f"   Average improvement: {total_improvement/circuits_with_improvement:.1f} LUTs" if circuits_with_improvement > 0 else "   Average improvement: N/A")
    
    print(f"\n🎯 Baseline optimization completed!")

if __name__ == "__main__":
    main()

