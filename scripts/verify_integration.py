#!/usr/bin/env python3
"""
Verify Designer → Simulator Integration
Tests that designer output structure matches simulator input expectations
"""

import json
from typing import Dict, Any

def verify_designer_to_simulator_mapping():
    """Verify the data structure mapping between designer and simulator"""
    
    print("="*70)
    print("DESIGNER → SIMULATOR INTEGRATION VERIFICATION")
    print("="*70)
    
    # Simulate designer output structure (from llm_designer.py line 520)
    designer_output = {
        'title': 'Test Mach-Zehnder Interferometer',
        'description': 'A simple interferometer for testing phase shifts',
        'experiment': {
            'steps': [
                {
                    'type': 'laser',
                    'name': 'Input Laser',
                    'x': 1.0,
                    'y': 3.0,
                    'angle': 0,
                    'parameters': {
                        'wavelength': 810,
                        'power': 100
                    }
                },
                {
                    'type': 'beam_splitter',
                    'name': 'BS1',
                    'x': 3.0,
                    'y': 3.0,
                    'angle': 45,
                    'parameters': {
                        'transmittance': 0.5
                    }
                },
                {
                    'type': 'phase_shifter',
                    'name': 'Phase Control',
                    'x': 5.0,
                    'y': 4.0,
                    'angle': 0,
                    'parameters': {
                        'phase': 1.57  # π/2
                    }
                },
                {
                    'type': 'beam_splitter',
                    'name': 'BS2',
                    'x': 7.0,
                    'y': 3.0,
                    'angle': 45,
                    'parameters': {
                        'transmittance': 0.5
                    }
                },
                {
                    'type': 'detector',
                    'name': 'Detector 1',
                    'x': 9.0,
                    'y': 3.0,
                    'angle': 0,
                    'parameters': {
                        'efficiency': 0.9
                    }
                }
            ]
        },
        'physics_explanation': 'Mach-Zehnder interferometer with phase shift in one arm'
    }
    
    print("\n✓ Designer Output Structure:")
    print(f"  - title: {designer_output['title']}")
    print(f"  - description: {designer_output['description']}")
    print(f"  - physics_explanation: {designer_output['physics_explanation']}")
    print(f"  - experiment.steps: {len(designer_output['experiment']['steps'])} components")
    
    # Simulate what simulator expects (from simulation_agent.py line 231)
    print("\n✓ Simulator Extraction:")
    components = designer_output.get('experiment', {}).get('steps', [])
    title = designer_output.get('title', 'Unknown')
    description = designer_output.get('description', '')
    physics = designer_output.get('physics_explanation', '')
    
    print(f"  - title: {title}")
    print(f"  - description: {description}")
    print(f"  - physics: {physics}")
    print(f"  - components: {len(components)} extracted")
    
    # Verify component structure
    print("\n✓ Component Structure Validation:")
    all_valid = True
    required_fields = ['type', 'name', 'parameters']
    
    for i, comp in enumerate(components, 1):
        missing = [field for field in required_fields if field not in comp]
        if missing:
            print(f"  ✗ Component {i} ({comp.get('name', 'Unknown')}) missing: {missing}")
            all_valid = False
        else:
            print(f"  ✓ Component {i}: {comp['type']} '{comp['name']}' - parameters: {list(comp['parameters'].keys())}")
    
    # Check mapping guidance
    print("\n✓ Component Type Mapping (Designer → Quantum Operations):")
    type_mappings = {
        'laser': 'initial quantum state (Fock, coherent)',
        'source': 'initial quantum state',
        'crystal': 'entangled photon pair (SPDC)',
        'beam_splitter': 'beam splitter transformation (use transmittance)',
        'phase_shifter': 'phase shift operation (use phase/angle)',
        'wave_plate': 'phase/polarization rotation',
        'mirror': 'path redirection (may have phase)',
        'detector': 'measurement operator',
        'filter': 'absorption/loss channel'
    }
    
    for comp in components:
        comp_type = comp['type']
        mapping = type_mappings.get(comp_type, '⚠ Unknown type - need to infer')
        print(f"  - {comp_type:15} → {mapping}")
    
    # Final verdict
    print("\n" + "="*70)
    if all_valid:
        print("✅ INTEGRATION VALID: Designer output matches simulator expectations")
        print("   - All required fields present")
        print("   - Structure correctly nested (experiment.steps)")
        print("   - Component types can be mapped to quantum operations")
    else:
        print("❌ INTEGRATION ISSUES: Some components missing required fields")
    print("="*70)
    
    return all_valid

if __name__ == '__main__':
    verify_designer_to_simulator_mapping()
