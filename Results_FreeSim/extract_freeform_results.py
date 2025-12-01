#!/usr/bin/env python3
"""
Extract and analyze FreeSim (freeform simulation) experiment results
"""

import json
import os
import zipfile
from pathlib import Path
from datetime import datetime
import re

def extract_zip(zip_path, extract_dir):
    """Extract a zip file to a directory"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    return extract_dir

def parse_experiment_name(filename):
    """Extract experiment name and timestamp from filename"""
    # Remove .zip extension
    name = filename.replace('.zip', '')
    # Remove _freeform_ suffix and date
    match = re.match(r'(.+?)_freeform_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', name)
    if match:
        exp_name = match.group(1).replace('_', ' ').title()
        timestamp = match.group(2)
        return exp_name, timestamp
    return name, None

def find_latest_version(experiments):
    """Group experiments by name and find latest version"""
    grouped = {}
    for exp in experiments:
        name = exp['base_name']
        if name not in grouped:
            grouped[name] = exp
        else:
            # Compare timestamps
            if exp['timestamp'] > grouped[name]['timestamp']:
                grouped[name] = exp
    return list(grouped.values())

def extract_simulation_metrics(result_file):
    """Extract key metrics from simulation result"""
    try:
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        metrics = {
            'alignment_score': None,
            'actually_models_design': None,
            'converged': None,
            'iteration_count': None,
            'rating': None,
            'physics_explanation': None,
            'key_findings': [],
            'recommendations': []
        }
        
        # Check different possible structures
        if 'alignment_assessment' in data:
            assess = data['alignment_assessment']
            metrics['alignment_score'] = assess.get('alignment_score')
            metrics['actually_models_design'] = assess.get('actually_models_design')
        
        if 'iteration_summary' in data:
            summary = data['iteration_summary']
            metrics['converged'] = summary.get('converged')
            metrics['iteration_count'] = summary.get('total_iterations')
        
        if 'final_analysis' in data:
            analysis = data['final_analysis']
            metrics['rating'] = analysis.get('rating')
            metrics['physics_explanation'] = analysis.get('physics_explanation', '')
            metrics['key_findings'] = analysis.get('key_findings', [])
            metrics['recommendations'] = analysis.get('recommendations', [])
        
        return metrics
    except Exception as e:
        print(f"Error extracting metrics from {result_file}: {e}")
        return None

def main():
    results_dir = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/Results_FreeSim')
    
    # Find all zip files
    zip_files = list(results_dir.glob('*.zip'))
    print(f"Found {len(zip_files)} FreeSim experiment archives")
    
    experiments = []
    
    for zip_file in zip_files:
        exp_name, timestamp = parse_experiment_name(zip_file.name)
        
        # Extract to temporary directory
        extract_dir = results_dir / zip_file.stem
        if not extract_dir.exists():
            print(f"Extracting {zip_file.name}...")
            extract_zip(zip_file, extract_dir)
        
        # Find simulation_result.json
        result_files = list(extract_dir.rglob('simulation_result.json'))
        if not result_files:
            print(f"  WARNING: No simulation_result.json found in {zip_file.name}")
            continue
        
        result_file = result_files[0]
        metrics = extract_simulation_metrics(result_file)
        
        if metrics:
            experiments.append({
                'name': exp_name,
                'base_name': re.sub(r'\s*\d{4}-\d{2}-\d{2}.*$', '', exp_name),
                'timestamp': timestamp,
                'zip_file': zip_file.name,
                'extract_dir': str(extract_dir),
                'metrics': metrics
            })
            print(f"  ✓ {exp_name}")
            print(f"    Alignment: {metrics['alignment_score']}, Converged: {metrics['converged']}, Rating: {metrics['rating']}")
    
    # Find latest versions
    print(f"\n\nFiltering to latest versions...")
    latest_experiments = find_latest_version(experiments)
    print(f"Found {len(latest_experiments)} unique experiments (latest versions)")
    
    # Sort by name
    latest_experiments.sort(key=lambda x: x['base_name'])
    
    # Create summary
    summary = {
        'extraction_date': datetime.now().isoformat(),
        'total_archives': len(zip_files),
        'unique_experiments': len(latest_experiments),
        'experiments': []
    }
    
    for exp in latest_experiments:
        summary['experiments'].append({
            'name': exp['base_name'],
            'timestamp': exp['timestamp'],
            'alignment_score': exp['metrics']['alignment_score'],
            'actually_models_design': exp['metrics']['actually_models_design'],
            'converged': exp['metrics']['converged'],
            'iterations': exp['metrics']['iteration_count'],
            'rating': exp['metrics']['rating'],
            'has_physics_explanation': bool(exp['metrics']['physics_explanation']),
            'key_findings_count': len(exp['metrics']['key_findings']),
            'recommendations_count': len(exp['metrics']['recommendations']),
            'directory': exp['extract_dir']
        })
    
    # Save summary
    output_file = results_dir / 'freeform_experiments_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n\nSummary saved to: {output_file}")
    
    # Print statistics
    print("\n" + "="*60)
    print("FREEFORM SIMULATION STATISTICS")
    print("="*60)
    
    converged_count = sum(1 for e in latest_experiments if e['metrics']['converged'])
    high_alignment = sum(1 for e in latest_experiments if e['metrics']['alignment_score'] and e['metrics']['alignment_score'] >= 7)
    models_design = sum(1 for e in latest_experiments if e['metrics']['actually_models_design'])
    
    print(f"Total experiments: {len(latest_experiments)}")
    print(f"Converged: {converged_count}/{len(latest_experiments)} ({100*converged_count/len(latest_experiments):.1f}%)")
    print(f"High alignment (≥7): {high_alignment}/{len(latest_experiments)} ({100*high_alignment/len(latest_experiments):.1f}%)")
    print(f"Actually models design: {models_design}/{len(latest_experiments)} ({100*models_design/len(latest_experiments):.1f}%)")
    
    # Rating distribution
    ratings = [e['metrics']['rating'] for e in latest_experiments if e['metrics']['rating']]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        print(f"\nAverage rating: {avg_rating:.1f}/10")
        print(f"Rating range: {min(ratings)}-{max(ratings)}")
    
    # Iteration statistics
    iterations = [e['metrics']['iteration_count'] for e in latest_experiments if e['metrics']['iteration_count']]
    if iterations:
        avg_iter = sum(iterations) / len(iterations)
        print(f"\nAverage iterations: {avg_iter:.1f}")
        print(f"Iteration range: {min(iterations)}-{max(iterations)}")
    
    print("\n" + "="*60)
    print("\nExperiment Details:")
    print("="*60)
    for exp in latest_experiments:
        m = exp['metrics']
        status = "✓" if m['converged'] else "✗"
        print(f"\n{status} {exp['base_name']}")
        print(f"   Alignment: {m['alignment_score']}/10 | Models Design: {m['actually_models_design']} | Rating: {m['rating']}/10")
        print(f"   Iterations: {m['iteration_count']} | Converged: {m['converged']}")

if __name__ == '__main__':
    main()
