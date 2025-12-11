#!/usr/bin/env python3
"""
Validate optical table geometry and beam paths
Tests if the setup is physically realizable
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_designer import LLMDesigner
from agentic_quantum.llm import SimpleLLM
import matplotlib.pyplot as plt
from simple_optical_table import create_optical_table_figure


def validate_optical_geometry(result):
    """Check if the optical table layout makes physical sense."""
    issues = []
    warnings = []
    
    components = result.components
    beam_paths = result.beam_path
    
    print(f"\n🔍 OPTICAL TABLE GEOMETRY VALIDATION")
    print(f"=" * 60)
    
    # 1. Check for overlapping components
    positions = {}
    for comp in components:
        pos = (comp['x'], comp['y'])
        if pos in positions:
            issues.append(f"❌ Components overlap at {pos}: {positions[pos]} and {comp['name']}")
        positions[pos] = comp['name']
    
    # 2. Check beam path physics
    if beam_paths:
        print(f"\n📍 Analyzing {len(beam_paths)} beam path(s):")
        
        for path_idx, path in enumerate(beam_paths, 1):
            print(f"\n  Path {path_idx}: {len(path)} waypoints")
            
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                
                distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                
                # Check for unrealistic jumps
                if distance > 5.0:
                    issues.append(f"❌ Path {path_idx}: Large jump {distance:.2f} units from {path[i]} to {path[i+1]}")
                    print(f"    ❌ Waypoint {i}→{i+1}: {distance:.2f} units (too large!)")
                elif distance > 3.0:
                    warnings.append(f"⚠️  Path {path_idx}: Unusual distance {distance:.2f} units from {path[i]} to {path[i+1]}")
                    print(f"    ⚠️  Waypoint {i}→{i+1}: {distance:.2f} units (unusual)")
                else:
                    print(f"    ✓ Waypoint {i}→{i+1}: {distance:.2f} units")
                
                # Check if beam passes through a component
                # For each segment, check if it's near a component
                segment_components = []
                for comp in components:
                    comp_x, comp_y = comp['x'], comp['y']
                    
                    # Check if component is on the line segment
                    # Simple check: is component within 0.3 units of either endpoint?
                    dist_to_start = ((comp_x - x1)**2 + (comp_y - y1)**2)**0.5
                    dist_to_end = ((comp_x - x2)**2 + (comp_y - y2)**2)**0.5
                    
                    if dist_to_start < 0.3 or dist_to_end < 0.3:
                        segment_components.append(comp['name'])
                
                if segment_components:
                    print(f"      Components nearby: {', '.join(segment_components)}")
    
    # 3. Check Hong-Ou-Mandel specific geometry
    if 'hong' in result.title.lower() or 'hom' in result.title.lower():
        print(f"\n🔬 HOM-Specific Geometry Checks:")
        
        # Find key components
        crystal = next((c for c in components if c['type'] == 'crystal'), None)
        bs = next((c for c in components if c['type'] == 'beam_splitter'), None)
        detectors = [c for c in components if c['type'] == 'detector']
        
        if crystal and bs:
            # SPDC crystal should come before beam splitter
            if crystal['x'] >= bs['x']:
                issues.append(f"❌ HOM: Crystal should be before beam splitter (Crystal x={crystal['x']}, BS x={bs['x']})")
            else:
                print(f"  ✓ Crystal ({crystal['x']}) before BS ({bs['x']})")
            
            # Two photons should travel separate paths to BS
            # Check if there are mirrors to redirect photons
            mirrors = [c for c in components if c['type'] == 'mirror']
            if len(mirrors) >= 2:
                print(f"  ✓ Has {len(mirrors)} mirrors for separate arms")
                
                # Check if mirrors are positioned symmetrically around center
                avg_y = sum(c['y'] for c in components) / len(components)
                upper_mirrors = [m for m in mirrors if m['y'] > avg_y]
                lower_mirrors = [m for m in mirrors if m['y'] < avg_y]
                
                if len(upper_mirrors) > 0 and len(lower_mirrors) > 0:
                    print(f"  ✓ Mirrors split into upper ({len(upper_mirrors)}) and lower ({len(lower_mirrors)}) arms")
                else:
                    warnings.append(f"⚠️  HOM: Mirrors should split into upper/lower arms for separate photon paths")
            else:
                warnings.append(f"⚠️  HOM: Needs mirrors to create separate paths (found {len(mirrors)})")
        
        # Detectors should be at BS outputs
        if bs and len(detectors) == 2:
            bs_x, bs_y = bs['x'], bs['y']
            det_positions = [(d['x'], d['y']) for d in detectors]
            
            # Check if detectors are downstream from BS
            for d in detectors:
                if d['x'] <= bs_x:
                    issues.append(f"❌ HOM: Detector '{d['name']}' should be after BS (Det x={d['x']}, BS x={bs_x})")
            
            # Check if detectors are symmetrically placed
            det_ys = [d['y'] for d in detectors]
            if abs(det_ys[0] - bs_y) > 0.5 or abs(det_ys[1] - bs_y) > 0.5:
                print(f"  ✓ Detectors at different heights (for two output ports)")
    
    # Summary
    print(f"\n{'='*60}")
    if issues:
        print(f"❌ OPTICAL TABLE VALIDATION FAILED")
        print(f"\nCritical Issues ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"✅ OPTICAL TABLE GEOMETRY VALID")
    
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warn in warnings:
            print(f"  {warn}")
    
    return issues, warnings


def test_and_visualize(query):
    """Test a query and create visualization."""
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
    designer = LLMDesigner(llm_client=llm)
    
    result = designer.design_experiment(query)
    
    print(f"\n✓ {result.title}")
    print(f"  {result.description}")
    
    # Validate geometry
    issues, warnings = validate_optical_geometry(result)
    
    # Create visualization
    print(f"\n🎨 Creating optical table visualization...")
    optical_format = {
        'title': result.title,
        'description': result.description,
        'steps': []
    }
    
    for comp in result.components:
        step = {
            'type': comp['type'],
            'description': comp['name'],
            'position': (comp['x'], comp['y']),
            'x': comp['x'],
            'y': comp['y'],
            'angle': comp.get('angle', 0),
            'parameters': comp.get('parameters', {})
        }
        optical_format['steps'].append(step)
    
    if result.beam_path:
        optical_format['beam_path'] = result.beam_path
    
    fig = create_optical_table_figure(optical_format, figsize=(16, 10))
    
    filename = f"/tmp/test_{query.replace(' ', '_')[:30]}.png"
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✓ Saved to: {filename}")
    
    plt.close(fig)
    
    return result, issues, warnings


if __name__ == '__main__':
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = "Design a Hong-Ou-Mandel experiment to demonstrate two-photon interference"
    
    test_and_visualize(query)
