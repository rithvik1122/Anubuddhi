#!/usr/bin/env python3
"""
Simple Quantum Experiment Designer

This script allows you to directly use the designer agent to create
quantum experiments.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.agents.analyzer_agent import AnalyzerAgent
from agentic_quantum.agents.optimizer_agent import OptimizerAgent
from agentic_quantum.core.config import Config
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def design_experiment():
    """Direct experiment design."""
    
    print("\n" + "="*70)
    print("🔬 QUANTUM EXPERIMENT DESIGNER")
    print("="*70)
    print()
    
    # Initialize agents
    print("🚀 Initializing agents...")
    config = Config()
    designer = DesignerAgent(config=config)
    analyzer = AnalyzerAgent(config=config)
    optimizer = OptimizerAgent(config=config)
    print("✅ Agents ready!\n")
    
    # Experiment options
    print("What would you like to design?")
    print()
    print("1. Squeezed light generation")
    print("2. Quantum teleportation protocol")  
    print("3. Bell state preparation")
    print("4. Photon number state engineering")
    print("5. Quantum entanglement generation")
    print("6. Homodyne detection optimization")
    print("7. Custom design")
    print()
    
    choice = input("Enter your choice (1-7): ").strip()
    
    # Experiment specifications
    experiments = {
        "1": {
            "name": "Squeezed Light Generation",
            "objectives": [
                "Maximize squeezing parameter",
                "Minimize losses",
                "Optimize detection efficiency"
            ],
            "constraints": {
                "max_modes": 2,
                "max_operations": 5
            }
        },
        "2": {
            "name": "Quantum Teleportation",
            "objectives": [
                "Maximize teleportation fidelity",
                "Minimize resource requirements",
                "Optimize Bell measurement"
            ],
            "constraints": {
                "max_modes": 3,
                "max_operations": 8
            }
        },
        "3": {
            "name": "Bell State Preparation",
            "objectives": [
                "Maximize entanglement fidelity",
                "Optimize state purity",
                "Minimize preparation time"
            ],
            "constraints": {
                "max_modes": 2,
                "max_operations": 4
            }
        },
        "4": {
            "name": "Photon Number State Engineering",
            "objectives": [
                "Maximize state fidelity",
                "Optimize photon number distribution",
                "Minimize losses"
            ],
            "constraints": {
                "max_modes": 1,
                "max_operations": 6
            }
        },
        "5": {
            "name": "Quantum Entanglement Generation",
            "objectives": [
                "Maximize entanglement measure",
                "Optimize two-mode correlations",
                "Minimize decoherence"
            ],
            "constraints": {
                "max_modes": 2,
                "max_operations": 6
            }
        },
        "6": {
            "name": "Homodyne Detection Optimization",
            "objectives": [
                "Maximize detection efficiency",
                "Minimize noise",
                "Optimize local oscillator power"
            ],
            "constraints": {
                "max_modes": 2,
                "max_operations": 3
            }
        }
    }
    
    if choice == "7":
        print("\n📝 Custom Design:")
        name = input("Experiment name: ").strip()
        print("Enter objectives (comma-separated):")
        obj_input = input("Objectives: ").strip()
        objectives = [o.strip() for o in obj_input.split(",")]
        
        spec = {
            "name": name,
            "objectives": objectives,
            "constraints": {"max_modes": 2, "max_operations": 5}
        }
    elif choice in experiments:
        spec = experiments[choice]
    else:
        print("❌ Invalid choice. Using default.")
        spec = experiments["5"]  # Entanglement by default
    
    print("\n" + "="*70)
    print(f"🎯 DESIGNING: {spec['name']}")
    print("="*70)
    print("\n📋 Objectives:")
    for i, obj in enumerate(spec['objectives'], 1):
        print(f"   {i}. {obj}")
    print()
    
    # Design the experiment
    print("🔧 Designing experiment...")
    design_result = designer.design_experiment(
        objectives=spec['objectives'],
        constraints=spec.get('constraints', {})
    )
    
    print("\n✅ Design complete!\n")
    
    # Display results
    print("=" *70)
    print("📊 DESIGN RESULTS")
    print("="*70)
    
    if design_result.get('status') == 'success':
        experiment = design_result.get('experiment')
        if experiment:
            config_data = experiment.get('configuration', {})
            
            print(f"\n🔬 Experiment ID: {design_result.get('experiment_id', 'N/A')}")
            print(f"\n⚙️  Configuration:")
            print(f"   • Number of modes: {config_data.get('num_modes', 'N/A')}")
            
            initial_state = config_data.get('initial_state', {})
            print(f"   • Initial state: {initial_state.get('type', 'N/A')}")
            if 'parameters' in initial_state:
                params = initial_state['parameters']
                if params:
                    print(f"     Parameters: {params}")
            
            operations = config_data.get('operations', [])
            if operations:
                print(f"\n   • Operations ({len(operations)} steps):")
                for i, op in enumerate(operations, 1):
                    op_type = op.get('type', 'unknown')
                    params = op.get('parameters', {})
                    print(f"     {i}. {op_type}")
                    if params:
                        for key, val in params.items():
                            if isinstance(val, float):
                                print(f"        - {key}: {val:.3f}")
                            else:
                                print(f"        - {key}: {val}")
            
            measurements = config_data.get('measurements', [])
            if measurements:
                print(f"\n   • Measurements:")
                for i, meas in enumerate(measurements, 1):
                    meas_type = meas.get('type', 'unknown')
                    modes = meas.get('modes', [])
                    print(f"     {i}. {meas_type} on mode(s) {modes}")
        
        # Analyze the design
        print("\n📊 Analyzing design...")
        analysis_result = analyzer.analyze_experiment(experiment_id=design_result.get('experiment_id'))
        
        if analysis_result.get('status') == 'success':
            metrics = analysis_result.get('metrics', {})
            print(f"\n✅ Analysis complete:")
            if metrics:
                print(f"   • Metrics calculated: {len(metrics)}")
                for metric_name, value in list(metrics.items())[:5]:  # Show first 5
                    if isinstance(value, float):
                        print(f"     - {metric_name}: {value:.4f}")
                    else:
                        print(f"     - {metric_name}: {value}")
        
        # Optimize the design
        print("\n⚡ Optimizing design...")
        opt_result = optimizer.optimize_experiment(
            experiment_id=design_result.get('experiment_id'),
            method='genetic_algorithm',
            max_iterations=20
        )
        
        if opt_result.get('status') == 'success':
            print(f"\n✅ Optimization complete:")
            improvement = opt_result.get('improvement', 0)
            print(f"   • Performance improvement: {improvement*100:.2f}%")
            
            best_params = opt_result.get('best_parameters', {})
            if best_params:
                print(f"   • Optimized parameters:")
                for param, value in list(best_params.items())[:5]:
                    if isinstance(value, float):
                        print(f"     - {param}: {value:.4f}")
                    else:
                        print(f"     - {param}: {value}")
    
    else:
        print(f"\n❌ Design failed: {design_result.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("🎉 Design session complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    design_experiment()
