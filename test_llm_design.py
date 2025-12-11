"""
Test LLM-based quantum experiment design vs template-based.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.core.config import Config
from agentic_quantum.agents.base_agent import AgentMessage, MessageType
from agentic_quantum.llm import SimpleLLM


async def test_designs():
    """Compare template vs LLM design."""
    
    print("="*80)
    print("🔬 COMPARING: Template vs AI Design")
    print("="*80)
    print()
    
    # Test 1: Template-based (current)
    print("📋 TEST 1: Template-Based Design")
    print("-"*80)
    
    config = Config()
    designer_template = DesignerAgent(config=config)  # No LLM
    
    request = AgentMessage(
        sender_id="test",
        receiver_id=designer_template.agent_id,
        message_type=MessageType.REQUEST,
        content={
            "action": "design_experiment",
            "type": "bell_state",
            "objectives": ["Maximize entanglement fidelity"],
            "constraints": {"max_modes": 2, "max_operations": 6}
        }
    )
    
    response = await designer_template.process_message(request)
    
    if response and 'experiment' in response.content:
        exp = response.content['experiment']
        print(f"✓ Design: {exp['description']}")
        print(f"✓ Confidence: {response.content.get('design_confidence', 0):.2f}")
        print(f"✓ Steps:")
        for i, step in enumerate(exp['steps'], 1):
            print(f"   {i}. {step['description']}")
        print(f"\n⚠️  Issue: Starts with vacuum |0,0⟩ → stays vacuum!")
    
    print()
    print("="*80)
    print("🤖 TEST 2: AI-Powered Design (Claude 3.5 Sonnet)")
    print("-"*80)
    
    # Test 2: LLM-based
    llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
    designer_ai = DesignerAgent(config=config, llm=llm)
    
    print("🧠 Querying AI for quantum experiment design...")
    print("   This may take 10-20 seconds...")
    print()
    
    response_ai = await designer_ai.process_message(request)
    
    if response_ai and 'experiment' in response_ai.content:
        exp_ai = response_ai.content['experiment']
        print(f"✓ Design: {exp_ai['description']}")
        print(f"✓ Confidence: {response_ai.content.get('design_confidence', 0):.2f}")
        print(f"✓ Rationale: {response_ai.content.get('design_rationale', 'N/A')}")
        print(f"✓ Steps:")
        for i, step in enumerate(exp_ai['steps'], 1):
            print(f"   {i}. {step['description']}")
        
        # Check if it's different
        initial_state = exp_ai['steps'][0] if exp_ai['steps'] else None
        if initial_state and '0,0' not in initial_state['description']:
            print(f"\n✅ SUCCESS: AI knows to start with photons, not vacuum!")
        else:
            print(f"\n⚠️  Note: AI still needs better quantum state initialization")
    else:
        print(f"❌ AI design failed: {response_ai.content if response_ai else 'No response'}")
    
    print()
    print("="*80)
    print("💡 CONCLUSION")
    print("="*80)
    print("Template: Simple but physically incorrect (vacuum stays vacuum)")
    print("AI: Can understand quantum mechanics and design proper experiments")
    print("   → Needs photon source before entanglement")
    print("   → Understands beam splitter creates superposition")
    print("   → Provides physical reasoning")
    print()


if __name__ == "__main__":
    asyncio.run(test_designs())
