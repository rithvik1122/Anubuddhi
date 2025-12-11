#!/usr/bin/env python3
"""
Interactive Quantum Experiment Designer

This script allows you to use the Agentic Quantum system to design custom
quantum experiments based on your specifications.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.core.system import AgenticQuantumSystem
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def design_experiment():
    """Interactive experiment design session."""
    
    print("\n" + "="*70)
    print("🔬 AGENTIC QUANTUM EXPERIMENT DESIGNER")
    print("="*70)
    print()
    
    # Initialize system
    print("🚀 Initializing Agentic Quantum System...")
    system = AgenticQuantumSystem()
    print("✅ System initialized!\n")
    
    # Get user input for what to design
    print("What would you like to design? Here are some examples:")
    print()
    print("1. Squeezed light generation")
    print("2. Quantum teleportation protocol")
    print("3. Bell state preparation")
    print("4. Photon number state engineering")
    print("5. Quantum entanglement generation")
    print("6. Homodyne detection optimization")
    print("7. Custom design (specify your own)")
    print()
    
    choice = input("Enter your choice (1-7): ").strip()
    
    # Map choices to experiment goals
    goals = {
        "1": {
            "goal": "Design an experiment to generate highly squeezed light",
            "objectives": [
                "Maximize squeezing parameter",
                "Minimize losses",
                "Optimize detection efficiency",
                "Ensure experimental feasibility"
            ]
        },
        "2": {
            "goal": "Design a quantum teleportation protocol",
            "objectives": [
                "Maximize teleportation fidelity",
                "Minimize resource requirements",
                "Optimize Bell measurement",
                "Ensure robust error correction"
            ]
        },
        "3": {
            "goal": "Design Bell state preparation experiment",
            "objectives": [
                "Maximize entanglement fidelity",
                "Optimize state purity",
                "Minimize preparation time",
                "Ensure measurement accuracy"
            ]
        },
        "4": {
            "goal": "Design photon number state engineering protocol",
            "objectives": [
                "Maximize state fidelity",
                "Optimize photon number distribution",
                "Minimize losses",
                "Enable efficient detection"
            ]
        },
        "5": {
            "goal": "Design quantum entanglement generation experiment",
            "objectives": [
                "Maximize entanglement measure (concurrence or negativity)",
                "Optimize two-mode correlations",
                "Minimize decoherence",
                "Ensure scalability"
            ]
        },
        "6": {
            "goal": "Optimize homodyne detection setup",
            "objectives": [
                "Maximize detection efficiency",
                "Minimize noise",
                "Optimize local oscillator power",
                "Ensure phase stability"
            ]
        }
    }
    
    if choice == "7":
        print("\n📝 Enter your custom design goal:")
        custom_goal = input("Goal: ").strip()
        print("\n📝 Enter objectives (comma-separated):")
        objectives_input = input("Objectives: ").strip()
        objectives = [obj.strip() for obj in objectives_input.split(",")]
        
        experiment_spec = {
            "goal": custom_goal,
            "objectives": objectives
        }
    elif choice in goals:
        experiment_spec = goals[choice]
    else:
        print("❌ Invalid choice. Using default: Squeezed light generation")
        experiment_spec = goals["1"]
    
    print("\n" + "="*70)
    print("🎯 EXPERIMENT SPECIFICATION")
    print("="*70)
    print(f"\n🎯 Goal: {experiment_spec['goal']}")
    print("\n📋 Objectives:")
    for i, obj in enumerate(experiment_spec['objectives'], 1):
        print(f"   {i}. {obj}")
    print()
    
    # Create workflow
    print("🔧 Creating design workflow...")
    workflow_id = await system.coordinator_agent.create_workflow(
        goal=experiment_spec['goal'],
        tasks=[
            {
                "id": "task_001",
                "name": "design_experiment",
                "agent": "designer",
                "priority": 1,
                "parameters": {
                    "objectives": experiment_spec['objectives']
                }
            },
            {
                "id": "task_002",
                "name": "analyze_design",
                "agent": "analyzer",
                "priority": 2,
                "dependencies": ["task_001"],
                "parameters": {
                    "analysis_type": "comprehensive"
                }
            },
            {
                "id": "task_003",
                "name": "optimize_design",
                "agent": "optimizer",
                "priority": 3,
                "dependencies": ["task_001", "task_002"],
                "parameters": {
                    "optimization_method": "genetic_algorithm",
                    "max_iterations": 50
                }
            }
        ]
    )
    
    print(f"✅ Workflow created: {workflow_id}\n")
    
    # Execute workflow
    print("🚀 Executing design workflow...")
    print("   This may take a moment...\n")
    
    result = await system.coordinator_agent.execute_workflow(
        workflow_id,
        strategy="priority_based"
    )
    
    print("\n" + "="*70)
    print("📊 DESIGN RESULTS")
    print("="*70)
    
    # Get workflow status
    status = system.coordinator_agent.get_workflow_status(workflow_id)
    
    print(f"\n✅ Status: {status.get('status', 'unknown')}")
    print(f"📈 Progress: {status.get('progress', 0)*100:.1f}%")
    print(f"✓ Completed tasks: {status.get('completed_tasks', 0)}/{status.get('total_tasks', 0)}")
    
    if status.get('results'):
        print("\n🎨 Generated Design:")
        results = status['results']
        
        # Show design results
        if 'task_001' in results:
            design = results['task_001']
            print(f"\n🔬 Experiment Design:")
            print(f"   - Configuration: {design.get('experiment_id', 'N/A')}")
            print(f"   - Status: {design.get('status', 'N/A')}")
            if 'configuration' in design:
                config = design['configuration']
                print(f"\n   Configuration Details:")
                print(f"   - Number of modes: {config.get('num_modes', 'N/A')}")
                print(f"   - Initial state: {config.get('initial_state', {}).get('type', 'N/A')}")
                operations = config.get('operations', [])
                if operations:
                    print(f"   - Operations: {len(operations)} steps")
                    for i, op in enumerate(operations[:3], 1):  # Show first 3
                        print(f"      {i}. {op.get('type', 'unknown')}")
                measurements = config.get('measurements', [])
                if measurements:
                    print(f"   - Measurements: {len(measurements)} types")
        
        # Show analysis results
        if 'task_002' in results:
            analysis = results['task_002']
            print(f"\n📊 Analysis Results:")
            print(f"   - Status: {analysis.get('status', 'N/A')}")
            if 'metrics' in analysis:
                metrics = analysis['metrics']
                print(f"   - Metrics analyzed: {len(metrics)}")
        
        # Show optimization results
        if 'task_003' in results:
            optimization = results['task_003']
            print(f"\n⚡ Optimization Results:")
            print(f"   - Method: {optimization.get('method', 'N/A')}")
            print(f"   - Status: {optimization.get('status', 'N/A')}")
            if 'best_parameters' in optimization:
                print(f"   - Optimized parameters: {len(optimization['best_parameters'])} values")
            if 'improvement' in optimization:
                print(f"   - Improvement: {optimization['improvement']*100:.2f}%")
    
    # Store in knowledge base
    print("\n💾 Storing results in knowledge base...")
    await system.knowledge_agent.store_knowledge(
        entry_type="experiment",
        content={
            "goal": experiment_spec['goal'],
            "objectives": experiment_spec['objectives'],
            "workflow_id": workflow_id,
            "results": status.get('results', {}),
            "timestamp": status.get('created_at', 'unknown')
        },
        metadata={
            "status": status.get('status'),
            "progress": status.get('progress'),
            "tags": ["custom_design", "interactive"]
        }
    )
    
    print("✅ Results stored!\n")
    
    # Cleanup
    await system.coordinator_agent.shutdown()
    
    print("="*70)
    print("🎉 Design session complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    asyncio.run(design_experiment())
