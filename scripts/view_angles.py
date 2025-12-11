#!/usr/bin/env python3
"""
Quick test to see if component angles are correct
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_quantum.llm import SimpleLLM
from llm_designer import LLMDesigner
from simple_optical_table import create_optical_table_figure
import matplotlib.pyplot as plt
import os

# Init LLM
llm = SimpleLLM(
    provider='openrouter',
    model='anthropic/claude-3.5-sonnet',
    api_key=os.getenv('OPENROUTER_API_KEY')
)

designer = LLMDesigner(llm)

# Test a few experiments
experiments = [
    "Design a Mach-Zehnder interferometer",
    "Design a Hong-Ou-Mandel experiment",
    "Design a Michelson interferometer"
]

for query in experiments:
    print(f"\n{'='*70}")
    print(f"Testing: {query}")
    print('='*70)
    
    result = designer.design_experiment(query)
    
    # Convert to optical format
    optical_format = {
        'title': result.title,
        'steps': result.components,
        'beam_path': result.beam_path
    }
    
    # Create figure
    fig = create_optical_table_figure(optical_format)
    
    # Save
    safe_name = query.replace(" ", "_").replace("-", "_")[:40]
    out_path = f"/tmp/angles_{safe_name}.png"
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#1a1410')
    plt.close(fig)
    
    print(f"✓ Saved to: {out_path}")
    print(f"  Components: {len(result.components)}")
    print(f"  Beam paths: {len(result.beam_path)}")
    
    # Show component types and positions
    for comp in result.components:
        if comp['type'] in ['mirror', 'beam_splitter']:
            print(f"  {comp['type']:15s} @ ({comp['x']:.1f}, {comp['y']:.1f})")

print("\n✅ All test images saved to /tmp/angles_*.png")
print("Please check if mirrors and beam splitters are oriented correctly!")
