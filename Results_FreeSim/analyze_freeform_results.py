#!/usr/bin/env python3
"""
Analyze FreeSim (freeform simulation) results with focus on alignment scores.

Primary metric: alignment_score (how well simulation matches design intent)
Secondary metric: rating (overall simulation quality)
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

def parse_experiment_name(dirname):
    """Extract clean experiment name from directory"""
    # Remove _freeform_YYYY-MM-DD_HH-MM-SS suffix
    name = dirname.replace('_freeform_', ' FREEFORM ')
    # Extract just the experiment part before timestamp
    match = re.match(r'(.+?)_freeform_\d{4}-\d{2}-\d{2}', dirname)
    if match:
        clean_name = match.group(1).replace('_', ' ').title()
        # Get timestamp for version tracking
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', dirname)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        return clean_name, timestamp
    return dirname, None

def find_latest_versions(results_dir):
    """Group experiments by base name and find latest version"""
    experiments = {}
    
    for item in results_dir.iterdir():
        if item.is_dir() and 'freeform' in item.name:
            clean_name, timestamp = parse_experiment_name(item.name)
            
            # Check if analysis results exist
            analysis_file = item / '04_analysis_results.json'
            if not analysis_file.exists():
                print(f"  ⚠ Skipping {item.name} - no analysis file")
                continue
            
            # Group by base name (without timestamp)
            base_name = re.sub(r'\s+\d{4}-\d{2}-\d{2}.*$', '', clean_name)
            
            if base_name not in experiments:
                experiments[base_name] = {
                    'name': clean_name,
                    'base_name': base_name,
                    'timestamp': timestamp,
                    'directory': item,
                    'analysis_file': analysis_file
                }
            else:
                # Keep the latest version
                if timestamp and timestamp > experiments[base_name]['timestamp']:
                    experiments[base_name] = {
                        'name': clean_name,
                        'base_name': base_name,
                        'timestamp': timestamp,
                        'directory': item,
                        'analysis_file': analysis_file
                    }
    
    return list(experiments.values())

def extract_key_metrics(analysis_file):
    """Extract the most important metrics from analysis JSON"""
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        
        # Primary metric: alignment check
        alignment = data.get('alignment_check', {})
        
        metrics = {
            # PRIMARY METRIC
            'alignment_score': alignment.get('alignment_score'),
            'actually_models_design': alignment.get('actually_models_design'),
            'physics_match_quality': alignment.get('physics_match_quality'),
            
            # SECONDARY METRICS
            'rating': data.get('rating'),
            'verdict': data.get('verdict'),
            
            # DETAILED ASSESSMENT
            'overall_assessment': alignment.get('overall_assessment', ''),
            'all_components_used': alignment.get('all_components_used'),
            'parameter_accuracy': alignment.get('parameter_accuracy'),
            'outputs_correct_observables': alignment.get('outputs_correct_observables'),
            'is_arbitrary_jazz': alignment.get('is_arbitrary_jazz'),
            
            # PHYSICS QUALITY
            'physics_correctness': data.get('physics_correctness', '')[:200] + '...' if data.get('physics_correctness') else None,
            'key_findings': data.get('key_findings', []),
            'limitations': data.get('limitations', []),
            
            # USEFUL COUNTS
            'num_key_findings': len(data.get('key_findings', [])),
            'num_limitations': len(data.get('limitations', [])),
            'has_refinement_instructions': bool(data.get('refinement_instructions'))
        }
        
        return metrics
    except Exception as e:
        print(f"  ✗ Error reading {analysis_file}: {e}")
        return None

def categorize_by_alignment(alignment_score):
    """Categorize alignment quality"""
    if alignment_score is None:
        return "UNKNOWN"
    elif alignment_score >= 9:
        return "EXCELLENT"
    elif alignment_score >= 7:
        return "GOOD"
    elif alignment_score >= 5:
        return "FAIR"
    else:
        return "POOR"

def main():
    results_dir = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/Results_FreeSim')
    
    print("="*70)
    print("FREEFORM SIMULATION ANALYSIS")
    print("="*70)
    print("\nFinding latest versions of experiments...")
    
    experiments = find_latest_versions(results_dir)
    print(f"Found {len(experiments)} unique experiments (latest versions)\n")
    
    # Extract metrics from all experiments
    results = []
    for exp in experiments:
        print(f"Analyzing: {exp['base_name']}")
        metrics = extract_key_metrics(exp['analysis_file'])
        
        if metrics:
            results.append({
                'name': exp['base_name'],
                'timestamp': exp['timestamp'],
                'directory': str(exp['directory'].name),
                **metrics
            })
            
            # Quick status
            align_cat = categorize_by_alignment(metrics['alignment_score'])
            models_design = "✓" if metrics['actually_models_design'] else "✗"
            print(f"  Alignment: {metrics['alignment_score']}/10 ({align_cat}) | Models Design: {models_design} | Rating: {metrics['rating']}/10\n")
    
    # Sort by alignment score (descending)
    results.sort(key=lambda x: x['alignment_score'] if x['alignment_score'] is not None else -1, reverse=True)
    
    # Save detailed JSON
    output_json = results_dir / 'freeform_analysis_summary.json'
    with open(output_json, 'w') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_experiments': len(results),
            'experiments': results
        }, f, indent=2)
    
    print(f"\nDetailed JSON saved to: {output_json}")
    
    # Generate statistics
    print("\n" + "="*70)
    print("ALIGNMENT SCORE STATISTICS")
    print("="*70)
    
    alignment_scores = [r['alignment_score'] for r in results if r['alignment_score'] is not None]
    models_design_count = sum(1 for r in results if r['actually_models_design'])
    
    if alignment_scores:
        avg_alignment = sum(alignment_scores) / len(alignment_scores)
        print(f"\nAlignment Scores:")
        print(f"  Average: {avg_alignment:.1f}/10")
        print(f"  Range: {min(alignment_scores)}-{max(alignment_scores)}")
        print(f"  Excellent (≥9): {sum(1 for s in alignment_scores if s >= 9)} experiments")
        print(f"  Good (7-8): {sum(1 for s in alignment_scores if 7 <= s < 9)} experiments")
        print(f"  Fair (5-6): {sum(1 for s in alignment_scores if 5 <= s < 7)} experiments")
        print(f"  Poor (<5): {sum(1 for s in alignment_scores if s < 5)} experiments")
    
    print(f"\nActually Models Design: {models_design_count}/{len(results)} ({100*models_design_count/len(results):.1f}%)")
    
    # Rating statistics
    ratings = [r['rating'] for r in results if r['rating'] is not None]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        print(f"\nSimulation Quality Ratings:")
        print(f"  Average: {avg_rating:.1f}/10")
        print(f"  Range: {min(ratings)}-{max(ratings)}")
    
    # Physics match quality distribution
    physics_quality = {}
    for r in results:
        quality = r['physics_match_quality']
        physics_quality[quality] = physics_quality.get(quality, 0) + 1
    
    print(f"\nPhysics Match Quality:")
    for quality, count in sorted(physics_quality.items(), key=lambda x: -x[1]):
        print(f"  {quality}: {count} experiments")
    
    # Generate ranked list
    print("\n" + "="*70)
    print("EXPERIMENTS RANKED BY ALIGNMENT SCORE")
    print("="*70)
    
    for i, exp in enumerate(results, 1):
        align = exp['alignment_score']
        rating = exp['rating']
        models = "✓" if exp['actually_models_design'] else "✗"
        physics = exp['physics_match_quality']
        
        print(f"\n{i}. {exp['name']}")
        print(f"   Alignment: {align}/10 ({categorize_by_alignment(align)}) | "
              f"Rating: {rating}/10 | Models Design: {models} | Physics: {physics}")
        
        if exp['overall_assessment']:
            # Print first 150 chars of assessment
            assessment = exp['overall_assessment'][:150]
            print(f"   → {assessment}...")
    
    # Create simplified CSV for paper
    csv_file = results_dir / 'freeform_results_for_paper.csv'
    with open(csv_file, 'w') as f:
        f.write("Experiment,Alignment_Score,Models_Design,Physics_Quality,Rating,Verdict\n")
        for exp in results:
            f.write(f'"{exp["name"]}",'
                   f'{exp["alignment_score"]},'
                   f'{exp["actually_models_design"]},'
                   f'{exp["physics_match_quality"]},'
                   f'{exp["rating"]},'
                   f'{exp["verdict"]}\n')
    
    print(f"\n\nSimplified CSV for paper: {csv_file}")
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == '__main__':
    main()
