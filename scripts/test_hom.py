#!/usr/bin/env python3
"""
Batch testing script - runs all tests without interaction
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_designer import LLMDesigner
from agentic_quantum.llm import SimpleLLM


def analyze_hom(result):
    """Specific analysis for Hong-Ou-Mandel."""
    issues = []
    
    # Critical requirements
    sources = [c for c in result.components if c['type'] in ['laser', 'source']]
    crystals = [c for c in result.components if c['type'] == 'crystal']
    bs = [c for c in result.components if c['type'] == 'beam_splitter']
    dets = [c for c in result.components if c['type'] == 'detector']
    
    # HOM needs: SPDC OR 2 sources
    if len(crystals) == 0 and len(sources) < 2:
        issues.append("❌ HOM needs SPDC crystal OR 2 separate photon sources")
    
    # HOM needs: 50:50 beam splitter
    if not bs:
        issues.append("❌ HOM needs 50:50 beam splitter for interference")
    elif bs[0].get('parameters', {}).get('transmittance', 0.5) != 0.5:
        issues.append(f"⚠️  BS transmittance is {bs[0]['parameters'].get('transmittance')}, should be 0.5")
    
    # HOM needs: 2 detectors for coincidence
    if len(dets) < 2:
        issues.append(f"❌ HOM needs 2 detectors for coincidence counting, found {len(dets)}")
    
    # Check physics explanation
    phys = result.physics_explanation.lower()
    
    critical_concepts = {
        'indistinguish': 'photon indistinguishability',
        'bunch': 'photon bunching',
        'coincid': 'coincidence counting',
        'interfere': 'quantum interference'
    }
    
    missing_concepts = []
    for keyword, concept in critical_concepts.items():
        if keyword not in phys:
            missing_concepts.append(concept)
    
    if missing_concepts:
        issues.append(f"⚠️  Physics explanation missing: {', '.join(missing_concepts)}")
    
    # Check expected outcome mentions HOM dip
    outcome = result.expected_outcome.lower()
    if 'dip' not in outcome:
        issues.append("⚠️  Expected outcome should mention 'HOM dip'")
    
    return issues


def test_single(query_name, query_text):
    """Test a single query."""
    print(f"\n{'='*80}")
    print(f"TEST: {query_name}")
    print(f"{'='*80}")
    
    llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
    designer = LLMDesigner(llm_client=llm)
    
    try:
        result = designer.design_experiment(query_text)
        
        print(f"✓ {result.title}")
        print(f"\n📦 Components: {len(result.components)}")
        for comp in result.components:
            print(f"  - {comp['name']} ({comp['type']})")
        
        print(f"\n🔬 Physics: {result.physics_explanation[:150]}...")
        
        # Analyze based on type
        if 'hong' in query_name.lower() or 'hom' in query_name.lower():
            issues = analyze_hom(result)
        else:
            issues = []
        
        if issues:
            print(f"\n❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print(f"\n✅ PASS")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == '__main__':
    # Allow command-line query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        test_single("Custom", query)
    else:
        print("Usage: python test_hom.py <your query>")
        print("\nExample queries:")
        print("  python test_hom.py Design a Hong-Ou-Mandel experiment")
        print("  python test_hom.py Create a Bell state generator")
        print("  python test_hom.py Build a Mach-Zehnder interferometer")
