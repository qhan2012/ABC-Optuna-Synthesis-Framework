#!/usr/bin/env python3
"""
Compare baseline vs Optuna optimization results
Shows area (LUT count) and level improvements for all circuits
"""

import json
import os
from datetime import datetime

def load_baseline_results():
    """Load baseline optimization results"""
    baseline_file = 'baseline_results_all_circuits.json'
    if not os.path.exists(baseline_file):
        print(f"❌ Baseline results file not found: {baseline_file}")
        return None
    
    try:
        with open(baseline_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load baseline results: {e}")
        return None

def load_optuna_results():
    """Load Optuna optimization results"""
    optuna_file = 'comprehensive_optimization_results.json'
    if not os.path.exists(optuna_file):
        print(f"❌ Optuna results file not found: {optuna_file}")
        return None
    
    try:
        with open(optuna_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load Optuna results: {e}")
        return None

def compare_results(baseline_data, optuna_data):
    """Compare baseline vs Optuna results"""
    print("🔍 COMPREHENSIVE BASELINE vs OPTUNA COMPARISON")
    print("=" * 100)
    
    # Create a mapping of baseline results by circuit name
    baseline_map = {}
    for circuit_result in baseline_data.get('circuit_results', []):
        if circuit_result['success']:
            baseline_map[circuit_result['circuit']] = circuit_result
    
    # Process each Optuna result
    comparison_results = []
    total_baseline_luts = 0
    total_optuna_luts = 0
    total_baseline_level = 0
    total_optuna_level = 0
    circuits_with_improvement = 0
    circuits_with_level_improvement = 0
    
    for optuna_result in optuna_data.get('circuit_results', []):
        circuit_name = optuna_result['circuit']
        baseline_result = baseline_map.get(circuit_name)
        
        if not baseline_result:
            print(f"⚠️  No baseline data found for {circuit_name}")
            continue
        
        # Extract values
        baseline_luts = baseline_result['baseline_luts']
        baseline_level = baseline_result['baseline_level']
        optuna_luts = optuna_result['best_luts']
        optuna_level = optuna_result.get('best_level', 0)
        
        # Calculate improvements
        lut_improvement = baseline_luts - optuna_luts
        lut_improvement_pct = (lut_improvement / baseline_luts) * 100 if baseline_luts > 0 else 0
        
        level_change = optuna_level - baseline_level
        level_change_pct = (level_change / baseline_level) * 100 if baseline_level > 0 else 0
        
        # Determine status
        if lut_improvement > 0:
            lut_status = "✅ IMPROVED"
            circuits_with_improvement += 1
        elif lut_improvement < 0:
            lut_status = "⚠️  DEGRADED"
        else:
            lut_status = "➡️  SAME"
        
        if level_change < 0:
            level_status = "✅ IMPROVED"
            circuits_with_level_improvement += 1
        elif level_change > 0:
            level_status = "⚠️  DEGRADED"
        else:
            level_status = "➡️  SAME"
        
        # Check level constraint
        level_constraint_status = "✅ RESPECTED"
        if optuna_result.get('level_constraint_applied', False):
            constraint_limit = optuna_result.get('level_constraint_limit', 0)
            if optuna_level > constraint_limit:
                level_constraint_status = "❌ VIOLATED"
        else:
            level_constraint_status = "🔒 DISABLED"
        
        # Store comparison result
        comparison_result = {
            'circuit': circuit_name,
            'baseline_luts': baseline_luts,
            'optuna_luts': optuna_luts,
            'lut_improvement': lut_improvement,
            'lut_improvement_pct': lut_improvement_pct,
            'lut_status': lut_status,
            'baseline_level': baseline_level,
            'optuna_level': optuna_level,
            'level_change': level_change,
            'level_change_pct': level_change_pct,
            'level_status': level_status,
            'level_constraint_status': level_constraint_status,
            'level_constraint_limit': optuna_result.get('level_constraint_limit', 0),
            'level_constraint_applied': optuna_result.get('level_constraint_applied', False),
            'n_trials': optuna_result.get('n_trials', 0)
        }
        
        comparison_results.append(comparison_result)
        
        # Accumulate totals
        total_baseline_luts += baseline_luts
        total_optuna_luts += optuna_luts
        total_baseline_level += baseline_level
        total_optuna_level += optuna_level
    
    # Print detailed comparison table
    print(f"{'Circuit':<25} {'Baseline':<10} {'Optuna':<10} {'Improvement':<12} {'Status':<12} {'Baseline':<10} {'Optuna':<10} {'Level':<10} {'Status':<12} {'Constraint':<12}")
    print("-" * 100)
    
    for result in comparison_results:
        circuit = result['circuit']
        baseline_luts = result['baseline_luts']
        optuna_luts = result['optuna_luts']
        lut_improvement = result['lut_improvement']
        lut_status = result['lut_status']
        baseline_level = result['baseline_level']
        optuna_level = result['optuna_level']
        level_status = result['level_status']
        constraint_status = result['level_constraint_status']
        
        # Format improvement display
        if lut_improvement > 0:
            improvement_display = f"+{lut_improvement} ({result['lut_improvement_pct']:.1f}%)"
        elif lut_improvement < 0:
            improvement_display = f"{lut_improvement} ({result['lut_improvement_pct']:.1f}%)"
        else:
            improvement_display = "0 (0.0%)"
        
        # Format level change display
        level_change = result['level_change']
        if level_change < 0:
            level_display = f"{level_change} ({result['level_change_pct']:.1f}%)"
        elif level_change > 0:
            level_display = f"+{level_change} ({result['level_change_pct']:.1f}%)"
        else:
            level_display = "0 (0.0%)"
        
        print(f"{circuit:<25} {baseline_luts:<10} {optuna_luts:<10} {improvement_display:<12} {lut_status:<12} {baseline_level:<10} {optuna_level:<10} {level_display:<10} {level_status:<12} {constraint_status:<12}")
    
    print("-" * 100)
    
    # Print summary statistics
    print("\n📊 SUMMARY STATISTICS")
    print("=" * 100)
    
    total_lut_improvement = total_baseline_luts - total_optuna_luts
    total_lut_improvement_pct = (total_lut_improvement / total_baseline_luts) * 100 if total_baseline_luts > 0 else 0
    
    total_level_change = total_optuna_level - total_baseline_level
    total_level_change_pct = (total_level_change / total_baseline_level) * 100 if total_baseline_level > 0 else 0
    
    print(f"Total Circuits: {len(comparison_results)}")
    print(f"Circuits with LUT improvement: {circuits_with_improvement}/{len(comparison_results)} ({circuits_with_improvement/len(comparison_results)*100:.1f}%)")
    print(f"Circuits with level improvement: {circuits_with_level_improvement}/{len(comparison_results)} ({circuits_with_level_improvement/len(comparison_results)*100:.1f}%)")
    print()
    
    print(f"AREA (LUT COUNT):")
    print(f"  Total Baseline LUTs: {total_baseline_luts:,}")
    print(f"  Total Optuna LUTs: {total_optuna_luts:,}")
    print(f"  Total LUT Improvement: {total_lut_improvement:,} ({total_lut_improvement_pct:.1f}%)")
    print(f"  Average LUT Improvement per Circuit: {total_lut_improvement/len(comparison_results):.1f}")
    print()
    
    print(f"LEVEL (DEPTH):")
    print(f"  Total Baseline Level: {total_baseline_level}")
    print(f"  Total Optuna Level: {total_optuna_level}")
    print(f"  Total Level Change: {total_level_change:+d} ({total_level_change_pct:+.1f}%)")
    print(f"  Average Level Change per Circuit: {total_level_change/len(comparison_results):+.1f}")
    print()
    
    # Level constraint analysis
    constraint_applied = [r for r in comparison_results if r['level_constraint_applied']]
    constraint_respected = [r for r in constraint_applied if r['level_constraint_status'] == "✅ RESPECTED"]
    constraint_violated = [r for r in constraint_applied if r['level_constraint_status'] == "❌ VIOLATED"]
    
    print(f"LEVEL CONSTRAINT ANALYSIS:")
    print(f"  Constraint Applied: {len(constraint_applied)}/{len(comparison_results)} circuits")
    print(f"  Constraint Respected: {len(constraint_respected)}/{len(constraint_applied)} circuits")
    print(f"  Constraint Violated: {len(constraint_violated)}/{len(constraint_applied)} circuits")
    
    if constraint_violated:
        print(f"  ⚠️  Circuits with violated constraints:")
        for result in constraint_violated:
            print(f"    - {result['circuit']}: Level {result['optuna_level']} > Limit {result['level_constraint_limit']:.1f}")
    
    # Save comparison results
    comparison_file = 'baseline_vs_optuna_comparison.json'
    comparison_data = {
        'comparison_date': datetime.now().isoformat(),
        'summary': {
            'total_circuits': len(comparison_results),
            'circuits_with_lut_improvement': circuits_with_improvement,
            'circuits_with_level_improvement': circuits_with_level_improvement,
            'total_baseline_luts': total_baseline_luts,
            'total_optuna_luts': total_optuna_luts,
            'total_lut_improvement': total_lut_improvement,
            'total_lut_improvement_pct': total_lut_improvement_pct,
            'total_baseline_level': total_baseline_level,
            'total_optuna_level': total_optuna_level,
            'total_level_change': total_level_change,
            'total_level_change_pct': total_level_change_pct
        },
        'circuit_comparisons': comparison_results
    }
    
    with open(comparison_file, 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"\n✅ Comparison results saved to: {comparison_file}")
    
    return comparison_results

def main():
    """Main function"""
    print("🚀 BASELINE vs OPTUNA OPTIMIZATION COMPARISON")
    print("=" * 100)
    
    # Load data
    baseline_data = load_baseline_results()
    if not baseline_data:
        return
    
    optuna_data = load_optuna_results()
    if not optuna_data:
        return
    
    # Compare results
    comparison_results = compare_results(baseline_data, optuna_data)
    
    if comparison_results:
        print(f"\n🎯 Comparison completed successfully!")
        print(f"📊 Analyzed {len(comparison_results)} circuits")
    else:
        print(f"\n❌ No comparison results generated")

if __name__ == "__main__":
    main()
