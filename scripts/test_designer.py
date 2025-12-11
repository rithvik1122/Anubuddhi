#!/usr/bin/env python3
"""
Interactive testing script for LLM Quantum Designer
Tests various quantum experiments and analyzes output quality
"""

import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_designer import LLMDesigner
from agentic_quantum.llm import SimpleLLM


def test_query(designer, query_name, query_text):
    """Test a single query and analyze the result."""
    print(f"\n{'='*80}")
    print(f"TEST: {query_name}")
    print(f"Query: {query_text}")
    print(f"{'='*80}\n")
    
    try:
        result = designer.design_experiment(query_text)
        
        # Show what we got
        print(f"✓ Title: {result.title}")
        print(f"✓ Description: {result.description}")
        print(f"\n📦 Components ({len(result.components)}):")
        for i, comp in enumerate(result.components, 1):
            print(f"  {i}. {comp['name']} ({comp['type']}) at ({comp['x']}, {comp['y']})")
            if 'parameters' in comp:
                print(f"     Parameters: {comp['parameters']}")
        
        print(f"\n🔬 Physics Explanation:")
        print(f"  {result.physics_explanation}")
        
        print(f"\n📊 Expected Outcome:")
        print(f"  {result.expected_outcome}")
        
        print(f"\n🛤️  Beam Path:")
        if result.beam_path:
            print(f"  Number of paths: {len(result.beam_path)}")
            for i, path in enumerate(result.beam_path, 1):
                print(f"  Path {i}: {len(path)} points")
                print(f"    {path}")
        else:
            print("  No explicit paths (will auto-generate)")
        
        # Analysis
        print(f"\n🔍 ANALYSIS:")
        analyze_design(query_name, result)
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_design(query_name, result):
    """Analyze if the design is correct for the given experiment type."""
    
    issues = []
    good = []
    
    query_lower = query_name.lower()
    
    # Hong-Ou-Mandel specific checks
    if 'hong' in query_lower or 'hom' in query_lower:
        print("  Checking Hong-Ou-Mandel requirements...")
        
        # Need 2 photon sources OR 1 SPDC crystal
        sources = [c for c in result.components if c['type'] in ['laser', 'source']]
        crystals = [c for c in result.components if c['type'] == 'crystal']
        
        if len(sources) >= 2:
            good.append("✓ Has 2+ photon sources (correct for HOM)")
        elif len(crystals) >= 1:
            good.append("✓ Has SPDC crystal (can create photon pairs)")
        else:
            issues.append("✗ Missing: Need 2 photon sources OR SPDC crystal for HOM")
        
        # Need beam splitter
        bs = [c for c in result.components if c['type'] == 'beam_splitter']
        if bs:
            good.append(f"✓ Has beam splitter ({len(bs)} found)")
            # Check if it's 50:50
            for b in bs:
                T = b.get('parameters', {}).get('transmittance', 0.5)
                if abs(T - 0.5) < 0.01:
                    good.append("✓ Beam splitter is 50:50")
                else:
                    issues.append(f"⚠ Beam splitter transmittance is {T}, should be 0.5")
        else:
            issues.append("✗ Missing: Need 50:50 beam splitter for HOM interference")
        
        # Need 2 detectors
        dets = [c for c in result.components if c['type'] == 'detector']
        if len(dets) >= 2:
            good.append(f"✓ Has {len(dets)} detectors for coincidence counting")
        else:
            issues.append(f"✗ Missing: Need 2 detectors, only found {len(dets)}")
        
        # Check physics explanation mentions key concepts
        phys = result.physics_explanation.lower()
        if 'interfere' in phys or 'interference' in phys:
            good.append("✓ Mentions interference")
        if 'coincid' in phys:
            good.append("✓ Mentions coincidence")
        if 'indistinguish' in phys:
            good.append("✓ Mentions indistinguishability")
        if 'bunch' in phys:
            good.append("✓ Mentions bunching")
    
    # Bell state / Entanglement checks
    elif 'bell' in query_lower or 'entangle' in query_lower:
        print("  Checking Bell state / Entanglement requirements...")
        
        crystals = [c for c in result.components if c['type'] == 'crystal']
        bs = [c for c in result.components if c['type'] == 'beam_splitter']
        
        if crystals:
            good.append(f"✓ Has nonlinear crystal ({crystals[0]['name']})")
            # Check for pump laser
            lasers = [c for c in result.components if c['type'] in ['laser', 'source']]
            if lasers:
                good.append("✓ Has pump laser for SPDC")
        elif bs:
            good.append("✓ Using beam splitter for spatial entanglement")
        else:
            issues.append("✗ Missing: Need crystal (SPDC) or beam splitter")
        
        dets = [c for c in result.components if c['type'] == 'detector']
        if len(dets) >= 2:
            good.append(f"✓ Has {len(dets)} detectors")
        else:
            issues.append(f"⚠ Only {len(dets)} detector(s), typically need 2 for entanglement verification")
    
    # Mach-Zehnder checks
    elif 'mach' in query_lower or 'zehnder' in query_lower:
        print("  Checking Mach-Zehnder requirements...")
        
        bs = [c for c in result.components if c['type'] == 'beam_splitter']
        if len(bs) >= 2:
            good.append(f"✓ Has {len(bs)} beam splitters")
        else:
            issues.append(f"✗ Missing: Mach-Zehnder needs 2 beam splitters, found {len(bs)}")
        
        mirrors = [c for c in result.components if c['type'] == 'mirror']
        if len(mirrors) >= 2:
            good.append(f"✓ Has {len(mirrors)} mirrors")
        else:
            issues.append(f"⚠ Only {len(mirrors)} mirror(s), typically need 2")
        
        ps = [c for c in result.components if c['type'] == 'phase_shifter']
        if ps:
            good.append("✓ Has phase shifter")
    
    # Print results
    print()
    for g in good:
        print(f"  {g}")
    for i in issues:
        print(f"  {i}")
    
    if not issues:
        print(f"\n  ✅ PASS: Design looks correct!")
    else:
        print(f"\n  ⚠️  ISSUES FOUND: {len(issues)} problem(s)")
    
    return issues


def main():
    """Run test suite."""
    print("🔬 LLM Quantum Designer Test Suite")
    print("=" * 80)
    
    # Initialize designer
    print("\n🤖 Initializing LLM Designer...")
    llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
    designer = LLMDesigner(llm_client=llm)
    print("✓ Ready!")
    
    # Test cases
    tests = [
        ("Hong-Ou-Mandel Effect", "Design a Hong-Ou-Mandel experiment to demonstrate two-photon interference"),
        ("Bell State", "Design a Bell state generator with maximum entanglement"),
        ("Mach-Zehnder", "Design a Mach-Zehnder interferometer for quantum interference"),
        ("Squeezed Light", "Design an experiment to generate squeezed light"),
    ]
    
    results = {}
    
    for test_name, query in tests:
        result = test_query(designer, test_name, query)
        results[test_name] = result
        
        # Ask user if they want to continue
        print("\n" + "="*80)
        response = input("Continue to next test? [Y/n/q to quit]: ").strip().lower()
        if response == 'q':
            break
        elif response == 'n':
            # Let user enter custom query
            custom = input("Enter custom query: ").strip()
            if custom:
                result = test_query(designer, "Custom", custom)
                results["Custom"] = result
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    for name, result in results.items():
        if result:
            print(f"✓ {name}: {result.title}")
        else:
            print(f"✗ {name}: FAILED")


if __name__ == '__main__':
    main()
