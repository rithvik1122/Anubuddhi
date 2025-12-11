#!/usr/bin/env python3
"""Check what the double-slit design looks like"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_quantum.llm import SimpleLLM
from llm_designer import LLMDesigner
import json
import os

# Init LLM
llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")

designer = LLMDesigner(llm)

query = "Design a double slit experiment"
print(f"Query: {query}\n")

result = designer.design_experiment(query)

# Check if parsed_design_json is already a dict or needs parsing
if isinstance(result.parsed_design_json, str):
    design = json.loads(result.parsed_design_json)
else:
    design = result.parsed_design_json

print("="*70)
print("TITLE:", result.title)
print("="*70)
print("\nDESCRIPTION:")
print(result.description)

print("\n" + "="*70)
print("COMPONENTS:")
print("="*70)
for comp in result.components:
    params = comp.get('parameters', {})
    param_str = ", ".join([f"{k}={v}" for k, v in params.items()]) if params else ""
    print(f"{comp['type']:15s} @ ({comp['x']:.1f}, {comp['y']:.1f}) - {comp.get('name', 'N/A'):20s} [{param_str}]")

print("\n" + "="*70)
print("BEAM PATH(S):")
print("="*70)
if isinstance(result.beam_path, list):
    if result.beam_path and isinstance(result.beam_path[0], list):
        if isinstance(result.beam_path[0][0], (int, float)):
            # Single path
            print(f"Single path with {len(result.beam_path)} waypoints:")
            for i, (x, y) in enumerate(result.beam_path):
                print(f"  [{i}] ({x:.1f}, {y:.1f})")
        else:
            # Multiple paths
            print(f"{len(result.beam_path)} separate paths:")
            for path_idx, path in enumerate(result.beam_path, 1):
                print(f"\n  Path {path_idx}: {len(path)} waypoints")
                for i, (x, y) in enumerate(path):
                    print(f"    [{i}] ({x:.1f}, {y:.1f})")

print("\n" + "="*70)
print("PHYSICS EXPLANATION:")
print("="*70)
print(result.physics_explanation)

print("\n" + "="*70)
print("EXPECTED OUTCOME:")
print("="*70)
print(design.get('expected_outcome', 'N/A'))
