#!/usr/bin/env python3
"""
Compare QuTiP vs FreeSim results and select best simulation for each experiment.

Strategy: For each experiment, use ALIGNMENT as primary criterion.
- FreeSim has alignment_score (0-10) 
- QuTiP doesn't have alignment but has rating (0-10) and limitations flag
- Choose whichever shows better design-simulation match
"""

import json
from pathlib import Path
import re

# Tier classification based on EXPERIMENT_TEST_SUITE.md
TIER_1_EXPERIMENTS = [
    "Mach-Zehnder Interferometer",
    "Hong-Ou-Mandel",
    "Bell State Generator",
    "Michelson Interferometer",
    "Quantum Eraser",
    "Delayed Choice"
]

TIER_2_EXPERIMENTS = [
    "GHZ State",
    "Quantum Teleportation",
    "Franson Interferometer",
    "Time-Bin",
    "Squeezed Light",
    "BB84",
    "Quantum Key Distribution"
]

TIER_3_EXPERIMENTS = [
    "Boson Sampling",
    "Continuous-Variable",
    "Hyperentangle",
    "EIT",
    "Electromagnetically Induced Transparency",
    "Quantum Frequency Converter"
]

def classify_tier(experiment_name):
    """Determine which tier an experiment belongs to"""
    name_lower = experiment_name.lower()
    
    for tier1 in TIER_1_EXPERIMENTS:
        if tier1.lower() in name_lower:
            return 1
    
    for tier2 in TIER_2_EXPERIMENTS:
        if tier2.lower() in name_lower:
            return 2
    
    for tier3 in TIER_3_EXPERIMENTS:
        if tier3.lower() in name_lower:
            return 3
    
    return None  # Unknown

def normalize_name(name):
    """Normalize experiment names for matching"""
    # Remove common variations
    normalized = name.lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return normalized.strip()

def find_matching_experiments(qutip_data, freesim_data):
    """Match experiments between QuTiP and FreeSim by name similarity"""
    matches = []
    
    qutip_exps = {normalize_name(exp['name']): exp for exp in qutip_data}
    freesim_exps = {normalize_name(exp['name']): exp for exp in freesim_data}
    
    # Try exact matches first
    for norm_name in qutip_exps:
        if norm_name in freesim_exps:
            matches.append((qutip_exps[norm_name], freesim_exps[norm_name]))
    
    # Find remaining unmatched
    matched_qutip = {normalize_name(q['name']) for q, f in matches}
    matched_freesim = {normalize_name(f['name']) for q, f in matches}
    
    unmatched_qutip = [name for name in qutip_exps if name not in matched_qutip]
    unmatched_freesim = [name for name in freesim_exps if name not in matched_freesim]
    
    # Try fuzzy matching for remaining
    for q_name in unmatched_qutip:
        for f_name in unmatched_freesim:
            # Check if key terms overlap
            q_words = set(q_name.split())
            f_words = set(f_name.split())
            overlap = len(q_words & f_words)
            
            if overlap >= 2:  # At least 2 words in common
                matches.append((qutip_exps[q_name], freesim_exps[f_name]))
                matched_qutip.add(q_name)
                matched_freesim.add(f_name)
                break
    
    return matches

def choose_best_simulation(qutip_exp, freesim_exp):
    """
    Select best simulation based on alignment/validation quality.
    
    Primary: Alignment score (FreeSim has explicit, QuTiP inferred from rating + limitations)
    Secondary: Rating
    """
    # FreeSim metrics
    fs_alignment = freesim_exp.get('alignment_score', 0)
    fs_models_design = freesim_exp.get('actually_models_design', False)
    fs_rating = freesim_exp.get('rating', 0)
    
    # QuTiP metrics (no explicit alignment, use rating + limitations as proxy)
    qt_rating = qutip_exp.get('rating', 0)
    qt_has_limitations = qutip_exp.get('has_simulation_limitations', True)
    qt_conclusion = qutip_exp.get('conclusion', '')
    
    # Infer QuTiP "alignment" from rating and whether it captured physics
    qt_captured_physics = '✅' in qt_conclusion or 'successfully' in qt_conclusion.lower()
    qt_alignment_proxy = qt_rating if qt_captured_physics else qt_rating * 0.5
    
    # Decision logic
    if fs_alignment >= 7 and fs_models_design:
        # FreeSim shows good alignment
        if qt_alignment_proxy >= 8:
            choice = "QuTiP" if qt_rating > fs_rating else "FreeSim"
            reason = "Both good, chose higher rating"
        else:
            choice = "FreeSim"
            reason = f"FreeSim alignment={fs_alignment}, models design correctly"
    elif qt_alignment_proxy >= 7:
        # QuTiP better
        choice = "QuTiP"
        reason = f"QuTiP rating={qt_rating}, captured physics"
    elif fs_alignment > qt_alignment_proxy:
        choice = "FreeSim"
        reason = f"FreeSim alignment={fs_alignment} > QuTiP proxy={qt_alignment_proxy:.1f}"
    elif qt_alignment_proxy > fs_alignment:
        choice = "QuTiP"
        reason = f"QuTiP proxy={qt_alignment_proxy:.1f} > FreeSim alignment={fs_alignment}"
    else:
        # Tie-breaker: prefer higher rating
        choice = "QuTiP" if qt_rating >= fs_rating else "FreeSim"
        reason = f"Tie-break on rating: QuTiP={qt_rating}, FreeSim={fs_rating}"
    
    return choice, reason, {
        'freesim_alignment': fs_alignment,
        'freesim_models_design': fs_models_design,
        'freesim_rating': fs_rating,
        'qutip_rating': qt_rating,
        'qutip_alignment_proxy': qt_alignment_proxy
    }

def main():
    # Load both summaries
    qutip_file = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/Results_QuTiP/experiments_summary.json')
    freesim_file = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/Results_FreeSim/freeform_analysis_summary.json')
    
    with open(qutip_file, 'r') as f:
        qutip_data = json.load(f)
    
    with open(freesim_file, 'r') as f:
        freesim_data = json.load(f)
    
    print("="*80)
    print("COMPARING QuTiP vs FreeSim SIMULATION RESULTS")
    print("="*80)
    
    print(f"\nQuTiP experiments: {len(qutip_data)}")
    print(f"FreeSim experiments: {len(freesim_data['experiments'])}")
    
    # Match experiments
    matches = find_matching_experiments(qutip_data, freesim_data['experiments'])
    print(f"\nMatched experiments: {len(matches)}")
    
    # Compare and choose best
    results = []
    
    for qutip_exp, freesim_exp in matches:
        choice, reason, metrics = choose_best_simulation(qutip_exp, freesim_exp)
        
        # Determine tier
        tier = classify_tier(qutip_exp['name'])
        
        results.append({
            'experiment_name': qutip_exp['name'],
            'tier': tier,
            'tier_label': f"Tier {tier}" if tier else "Unknown",
            'best_simulation': choice,
            'reason': reason,
            'qutip_rating': metrics['qutip_rating'],
            'qutip_category': qutip_exp.get('category', 'Unknown'),
            'freesim_alignment': metrics['freesim_alignment'],
            'freesim_models_design': metrics['freesim_models_design'],
            'freesim_rating': metrics['freesim_rating'],
            'qutip_key_insight': qutip_exp.get('key_insight', ''),
            'freesim_physics_quality': freesim_exp.get('physics_match_quality', '')
        })
    
    # Sort by tier, then by best simulation quality
    results.sort(key=lambda x: (x['tier'] if x['tier'] else 99, 
                                 -max(x['qutip_rating'], x['freesim_alignment'])))
    
    # Statistics
    print("\n" + "="*80)
    print("RESULTS BY TIER")
    print("="*80)
    
    for tier_num in [1, 2, 3]:
        tier_results = [r for r in results if r['tier'] == tier_num]
        if not tier_results:
            continue
        
        print(f"\n{'='*80}")
        print(f"TIER {tier_num}: {len(tier_results)} experiments")
        print(f"{'='*80}")
        
        freesim_chosen = sum(1 for r in tier_results if r['best_simulation'] == 'FreeSim')
        qutip_chosen = sum(1 for r in tier_results if r['best_simulation'] == 'QuTiP')
        
        print(f"  Best simulation: FreeSim={freesim_chosen}, QuTiP={qutip_chosen}")
        
        for r in tier_results:
            symbol = "🟢" if r['best_simulation'] == 'FreeSim' else "🔵"
            print(f"\n{symbol} {r['experiment_name']}")
            print(f"   Best: {r['best_simulation']}")
            print(f"   QuTiP: rating={r['qutip_rating']}/10")
            print(f"   FreeSim: alignment={r['freesim_alignment']}/10, "
                  f"models_design={r['freesim_models_design']}, rating={r['freesim_rating']}/10")
            print(f"   → {r['reason']}")
    
    # Save comparison
    output_file = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/simulation_comparison.json')
    with open(output_file, 'w') as f:
        json.dump({
            'total_experiments': len(results),
            'tier_1_count': len([r for r in results if r['tier'] == 1]),
            'tier_2_count': len([r for r in results if r['tier'] == 2]),
            'tier_3_count': len([r for r in results if r['tier'] == 3]),
            'freesim_chosen': sum(1 for r in results if r['best_simulation'] == 'FreeSim'),
            'qutip_chosen': sum(1 for r in results if r['best_simulation'] == 'QuTiP'),
            'experiments': results
        }, f, indent=2)
    
    print(f"\n\nComparison saved to: {output_file}")
    
    # Create CSV for LaTeX table
    csv_file = Path('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/results_for_paper.csv')
    with open(csv_file, 'w') as f:
        f.write("Tier,Experiment,Best_Sim,QuTiP_Rating,FreeSim_Alignment,FreeSim_Models_Design\n")
        for r in results:
            f.write(f'{r["tier"]},"{r["experiment_name"]}",{r["best_simulation"]},'
                   f'{r["qutip_rating"]},{r["freesim_alignment"]},{r["freesim_models_design"]}\n')
    
    print(f"CSV for paper: {csv_file}")
    
    print("\n" + "="*80)
    print("COMPARISON COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
