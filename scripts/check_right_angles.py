#!/usr/bin/env python3
"""Check if beam paths are at right angles"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_quantum.llm import SimpleLLM
from llm_designer import LLMDesigner
import json
import os
import numpy as np

# Init LLM
llm = SimpleLLM(
    provider='openrouter',
    model='anthropic/claude-3.5-sonnet',
    api_key=os.getenv('OPENROUTER_API_KEY')
)

designer = LLMDesigner(llm)

query = "Design a Mach-Zehnder interferometer"
print(f"Testing: {query}\n")

result = designer.design_experiment(query)
design = json.loads(result.parsed_design_json)

print("BEAM PATHS:")
print("="*70)
for path_idx, path in enumerate(design['beam_path'], 1):
    print(f"\nPath {path_idx}: {len(path)} waypoints")
    for i, (x, y) in enumerate(path):
        print(f"  [{i}] ({x:.1f}, {y:.1f})", end="")
        if i > 0:
            prev_x, prev_y = path[i-1]
            dx = x - prev_x
            dy = y - prev_y
            if abs(dx) < 0.1:
                print(f"  ← VERTICAL (dy={dy:.1f})")
            elif abs(dy) < 0.1:
                print(f"  ← HORIZONTAL (dx={dx:.1f})")
            else:
                angle = np.degrees(np.arctan2(dy, dx))
                print(f"  ← DIAGONAL (dx={dx:.1f}, dy={dy:.1f}, angle={angle:.1f}°)")
        else:
            print()

print("\n" + "="*70)
print("\nIf most segments are HORIZONTAL or VERTICAL, the layout uses right angles! ✓")
