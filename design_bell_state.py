#!/usr/bin/env python3
"""
Bell State Experiment Designer

Designs a quantum experiment to prepare entangled Bell states.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.core.config import Config
from agentic_quantum.agents.base_agent import AgentMessage, MessageType


async def design_bell_state():
    """Design a Bell state preparation experiment."""
    
    print("\n" + "="*70)
    print("🔬 BELL STATE PREPARATION EXPERIMENT DESIGNER")
    print("="*70)
    print()
    
    # Initialize designer
    print("🚀 Initializing designer agent...")
    config = Config()
    designer = DesignerAgent(config=config)
    print("✅ Designer ready!\n")
    
    print("🎯 Designing Bell State Preparation Experiment")
    print("\n📋 Objectives:")
    objectives = [
        "Maximize entanglement fidelity",
        "Optimize state purity",
        "Minimize preparation time",
        "Ensure measurement accuracy"
    ]
    for i, obj in enumerate(objectives, 1):
        print(f"   {i}. {obj}")
    print()
    
    # Create design request message
    request = AgentMessage(
        sender_id="user",
        receiver_id=designer.agent_id,
        message_type=MessageType.REQUEST,
        content={
            "action": "design_experiment",
            "type": "bell_state",
            "objectives": objectives,
            "constraints": {
                "max_modes": 2,
                "max_operations": 6,
                "max_photons": 2
            }
        }
    )
    
    print("🔧 Designing experiment (this may take a moment)...")
    response = await designer.process_message(request)
    
    print("\n" + "="*70)
    print("📊 DESIGN RESULTS")
    print("="*70)
    
    if response and response.content and 'experiment' in response.content:
        result = response.content
        experiment = result['experiment']
        
        print("\n✅ Design successful!\n")
        print(f"🔬 Experiment ID: {experiment['experiment_id']}")
        print(f"📝 Description: {experiment['description']}")
        print(f"✓ Validation: {result.get('validation_status', 'unknown')}")
        print(f"🎯 Confidence: {result.get('design_confidence', 'N/A')}")
        
        print(f"\n⚙️  Configuration:")
        print(f"   • Number of modes: {experiment['num_modes']}")
        print(f"   • Mode dimensions: {experiment['mode_dimensions']}")
        
        # Show experimental steps
        steps = experiment.get('steps', [])
        if steps:
            print(f"\n   • Experimental Protocol ({len(steps)} steps):")
            for i, step in enumerate(steps, 1):
                step_type = step['step_type']
                desc = step['description']
                print(f"     {i}. [{step_type.upper()}] {desc}")
                
                # Show component details for operations
                if step_type == 'operation':
                    comp = step.get('component', {})
                    params = comp.get('parameters', {})
                    if params:
                        for k, v in params.items():
                            if isinstance(v, float):
                                print(f"        • {k}: {v:.4f}")
                            else:
                                print(f"        • {k}: {v}")
        
        # Design rationale
        rationale = result.get('design_rationale', '')
        if rationale:
            print(f"\n   📝 Design Rationale:")
            print(f"     {rationale}")
        
        complexity = result.get('estimated_complexity', 'N/A')
        print(f"\n   🧮 Estimated Complexity: {complexity}")
        
        print("\n✨ This experiment generates entangled Bell states!")
        print("   The two modes will be quantum correlated after the operations.")
        
    else:
        error = response.content.get('error', 'Unknown error') if response and response.content else 'No response'
        print(f"\n❌ Design failed: {error}")
    
    print("\n" + "="*70)
    print("🎉 Design session complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    asyncio.run(design_bell_state())
