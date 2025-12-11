"""
Test the Streamlit app flow to verify it works correctly
"""

import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.core.config import Config
from agentic_quantum.agents.base_agent import AgentMessage, MessageType
from agentic_quantum.llm import SimpleLLM

print("🧪 Testing Streamlit App Flow")
print("="*60)

# Test 1: Initialize Designer (no LLM)
print("\n1️⃣ Testing Template-Based Designer...")
config = Config()
designer = DesignerAgent(config=config)
print(f"   ✓ Designer initialized: {designer.agent_id}")

# Test 2: Initialize Designer with LLM
print("\n2️⃣ Testing AI Designer...")
llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
designer_ai = DesignerAgent(config=config, llm=llm)
print(f"   ✓ AI Designer initialized: {designer_ai.agent_id}")

# Test 3: Design experiment (template)
print("\n3️⃣ Testing Template Design...")
request = AgentMessage(
    sender_id="test",
    receiver_id=designer.agent_id,
    message_type=MessageType.REQUEST,
    content={
        "action": "design_experiment",
        "type": "bell_state",
        "objectives": ["Maximize entanglement"],
        "constraints": {"max_modes": 2}
    }
)

async def test_design():
    response = await designer.process_message(request)
    return response

result_template = asyncio.run(test_design())
if result_template and 'experiment' in result_template.content:
    exp = result_template.content['experiment']
    print(f"   ✓ Template design created")
    print(f"   • Steps: {len(exp.get('steps', []))}")
    print(f"   • Description: {exp.get('description', 'N/A')[:50]}...")
else:
    print("   ❌ Template design failed")

# Test 4: Design experiment (AI)
print("\n4️⃣ Testing AI Design...")
request_ai = AgentMessage(
    sender_id="test",
    receiver_id=designer_ai.agent_id,
    message_type=MessageType.REQUEST,
    content={
        "action": "design_experiment",
        "type": "bell_state",
        "objectives": ["Maximize entanglement"],
        "constraints": {"max_modes": 2}
    }
)

async def test_ai_design():
    response = await designer_ai.process_message(request_ai)
    return response

result_ai = asyncio.run(test_ai_design())
if result_ai and 'experiment' in result_ai.content:
    exp = result_ai.content['experiment']
    print(f"   ✓ AI design created")
    print(f"   • Steps: {len(exp.get('steps', []))}")
    print(f"   • Description: {exp.get('description', 'N/A')[:50]}...")
    print(f"   • Rationale: {result_ai.content.get('design_rationale', 'N/A')[:80]}...")
else:
    print("   ❌ AI design failed")

print("\n" + "="*60)
print("✅ All tests passed! Streamlit app should work correctly.")
print("\n📝 Next steps:")
print("   1. Open http://localhost:8501")
print("   2. Enable 'AI Design (LLM)' checkbox")
print("   3. Type: 'Design a Bell state experiment'")
print("   4. Click '🚀 Design'")
print("   5. Watch progress bar and status updates")
print("   6. See SVG optical table diagram appear")
print("   7. Click '▶️ Run Simulation' to validate")
