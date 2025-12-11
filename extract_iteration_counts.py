#!/usr/bin/env python3
"""
Extract iteration counts from FreeSim experiment README files
and add to simulation comparison data.
"""

import json
import re
from pathlib import Path

# Load existing comparison data
with open('simulation_comparison.json', 'r') as f:
    comparison_data = json.load(f)

# Map experiment names to their iteration counts
iteration_map = {}

freesim_dir = Path('Results_FreeSim')
for exp_dir in freesim_dir.iterdir():
    if not exp_dir.is_dir():
        continue
    
    readme_path = exp_dir / 'README.md'
    if not readme_path.exists():
        continue
    
    # Read README and extract convergence info
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Extract iteration count
    match = re.search(r'\*\*Converged:\*\* (Yes|No) \(in (\d+) iteration\(s\)\)', content)
    if match:
        converged = match.group(1) == 'Yes'
        iterations = int(match.group(2))
        
        # Extract experiment name from directory
        exp_name = exp_dir.name.replace('_freeform_', ' ').split(' 2025-')[0]
        exp_name = exp_name.replace('_', ' ').title()
        
        # Store with both directory name and cleaned name
        iteration_map[exp_dir.name] = {
            'converged': converged,
            'iterations': iterations,
            'clean_name': exp_name
        }

# Add iteration data to comparison
for exp in comparison_data['experiments']:
    exp_name = exp['experiment_name']
    
    # Try to find matching iteration data
    found = False
    for dir_name, iter_data in iteration_map.items():
        if exp_name.lower().replace(' ', '_').replace('-', '_') in dir_name.lower():
            exp['design_iterations'] = iter_data['iterations']
            exp['design_converged'] = iter_data['converged']
            found = True
            break
    
    if not found:
        exp['design_iterations'] = 'N/A'
        exp['design_converged'] = 'N/A'
        print(f"Warning: No iteration data found for: {exp_name}")

# Print summary
print("\n=== ITERATION STATISTICS ===")
print(f"Total experiments: {len(comparison_data['experiments'])}")

iterations_list = [exp.get('design_iterations', 'N/A') 
                   for exp in comparison_data['experiments'] 
                   if exp.get('design_iterations') != 'N/A']
converged_list = [exp.get('design_converged', False) 
                  for exp in comparison_data['experiments'] 
                  if exp.get('design_converged') != 'N/A']

if iterations_list:
    print(f"Average iterations: {sum(iterations_list) / len(iterations_list):.1f}")
    print(f"Converged: {sum(converged_list)}/{len(converged_list)} ({100*sum(converged_list)/len(converged_list):.0f}%)")
    print(f"Iteration distribution: 1={iterations_list.count(1)}, 2={iterations_list.count(2)}, 3={iterations_list.count(3)}")

# Save updated comparison
with open('simulation_comparison_with_iterations.json', 'w') as f:
    json.dump(comparison_data, f, indent=2)

print("\n✓ Updated comparison saved to: simulation_comparison_with_iterations.json")

# Print table for LaTeX
print("\n=== EXPERIMENT ITERATION TABLE ===")
print("Experiment | Iterations | Converged")
print("-" * 60)
for exp in sorted(comparison_data['experiments'], key=lambda x: x['tier']):
    name = exp['experiment_name']
    iters = exp.get('design_iterations', 'N/A')
    conv = exp.get('design_converged', 'N/A')
    conv_str = '✓' if conv else '✗' if conv != 'N/A' else 'N/A'
    print(f"{name:<45} | {iters:>3} | {conv_str}")
