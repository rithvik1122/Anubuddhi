#!/usr/bin/env python3
"""
Extract structured data from all experimental results for journal article.
"""

import json
import re
from pathlib import Path

def extract_experiment_data(analysis_path):
    """Extract key information from deep analysis markdown."""
    with open(analysis_path, 'r') as f:
        content = f.read()
    
    data = {}
    
    # Extract experiment name
    match = re.search(r'\*\*Experiment:\*\* (.+)', content)
    data['name'] = match.group(1) if match else "Unknown"
    
    # Extract quality rating
    match = re.search(r'\*\*Quality Rating:\*\* (\d+)/10 \((\w+)\)', content)
    if match:
        data['rating'] = int(match.group(1))
        data['rating_label'] = match.group(2)
    else:
        data['rating'] = 0
        data['rating_label'] = "UNKNOWN"
    
    # Extract key insight
    match = re.search(r'## Key Insight\n\n(.+?)(?=\n\n##|\Z)', content, re.DOTALL)
    data['key_insight'] = match.group(1).strip() if match else ""
    
    # Extract conclusion
    match = re.search(r'## Conclusion\n\n(.+?)(?=\n\n|\Z)', content, re.DOTALL)
    data['conclusion'] = match.group(1).strip() if match else ""
    
    # Determine if design was good regardless of simulation
    design_quality_markers = [
        "designer wants to",
        "design intent",
        "components:",
        "physics goal:"
    ]
    
    # Check if simulation limitations mentioned
    simulation_limitations = [
        "fock state",
        "cannot capture",
        "cannot model",
        "missing",
        "temporal",
        "catastrophic",
        "critical flaw"
    ]
    
    content_lower = content.lower()
    data['has_simulation_limitations'] = any(marker in content_lower for marker in simulation_limitations)
    
    # Categorize experiment type
    name_lower = data['name'].lower()
    if 'interferometer' in name_lower:
        data['category'] = 'Interferometry'
    elif 'bell' in name_lower or 'entangle' in name_lower or 'ghz' in name_lower:
        data['category'] = 'Entanglement'
    elif 'teleportation' in name_lower:
        data['category'] = 'Quantum Communication'
    elif 'squeezed' in name_lower or 'parametric' in name_lower:
        data['category'] = 'Nonlinear Optics'
    elif 'hong-ou-mandel' in name_lower or 'hom' in name_lower:
        data['category'] = 'Quantum Interference'
    elif 'bb84' in name_lower or 'qkd' in name_lower or 'key distribution' in name_lower:
        data['category'] = 'Quantum Communication'
    elif 'boson sampling' in name_lower:
        data['category'] = 'Quantum Computation'
    elif 'eit' in name_lower or 'transparency' in name_lower:
        data['category'] = 'Atomic Physics'
    elif 'frequency' in name_lower:
        data['category'] = 'Quantum Conversion'
    else:
        data['category'] = 'Other'
    
    return data

def main():
    results_dir = Path(__file__).parent
    
    experiments = []
    for analysis_file in sorted(results_dir.glob('*/05_deep_analysis.md')):
        data = extract_experiment_data(analysis_file)
        data['directory'] = analysis_file.parent.name
        experiments.append(data)
    
    # Save as JSON
    output_file = results_dir / 'experiments_summary.json'
    with open(output_file, 'w') as f:
        json.dump(experiments, f, indent=2)
    
    print(f"✓ Extracted data from {len(experiments)} experiments")
    print(f"✓ Saved to {output_file}")
    
    # Print summary statistics
    print("\n=== SUMMARY STATISTICS ===\n")
    
    # Rating distribution
    from collections import Counter
    ratings = Counter([e['rating'] for e in experiments])
    print("Rating Distribution:")
    for rating in sorted(ratings.keys(), reverse=True):
        count = ratings[rating]
        label = [e['rating_label'] for e in experiments if e['rating'] == rating][0]
        print(f"  {rating}/10 ({label:10s}): {count} experiments")
    
    # Category distribution
    categories = Counter([e['category'] for e in experiments])
    print("\nExperiment Categories:")
    for cat, count in categories.most_common():
        print(f"  {cat:25s}: {count} experiments")
    
    # Simulation limitations
    with_limitations = sum(1 for e in experiments if e['has_simulation_limitations'])
    print(f"\nExperiments with identified simulation limitations: {with_limitations}/{len(experiments)}")
    
    # High design quality despite low simulation rating
    design_good_sim_poor = [e for e in experiments if e['rating'] <= 4 and e['has_simulation_limitations']]
    print(f"\nGood designs limited by simulation constraints: {len(design_good_sim_poor)}")
    for e in design_good_sim_poor:
        print(f"  - {e['name']} ({e['rating']}/10)")

if __name__ == '__main__':
    main()
