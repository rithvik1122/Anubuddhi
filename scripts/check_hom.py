#!/usr/bin/env python3
"""Check HOM design details"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from llm_designer import LLMDesigner
from agentic_quantum.llm import SimpleLLM
import json

# Initialize LLM
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_key:
    print("Error: OPENROUTER_API_KEY not set")
    sys.exit(1)

llm_client = SimpleLLM(
    provider='openrouter',
    model='anthropic/claude-3.5-sonnet',
    api_key=openrouter_key
)

designer = LLMDesigner(llm_client)
result = designer.design_experiment('Design a Hong-Ou-Mandel experiment')

print('=' * 70)
print('COMPONENTS:')
print('=' * 70)
for comp in result.components:
    print(f'{comp["type"]:15s} @ ({comp["x"]:.1f}, {comp["y"]:.1f})')

print('\n' + '=' * 70)
print('BEAM PATHS:')
print('=' * 70)
design = json.loads(result.parsed_design_json)
for i, path in enumerate(design['beam_path'], 1):
    print(f'Path {i}: {len(path)} waypoints')
    for j, point in enumerate(path):
        print(f'  [{j}] ({point[0]:.1f}, {point[1]:.1f})')

print('\n' + '=' * 70)
print('PHYSICS:')
print('=' * 70)
print(result.physics_explanation)
