#!/usr/bin/env python3
"""
Test Bell State Design Through Simulation

This script:
1. Designs a Bell state experiment (template-based)
2. Simulates the quantum physics using QuTiP
3. Analyzes the actual quantum state produced
4. Validates if it's really a Bell state
5. Visualizes the results
"""

import sys
import asyncio
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.core.config import Config
from agentic_quantum.agents.base_agent import AgentMessage, MessageType
from agentic_quantum.quantum import QuantumExperiment, QuantumSimulator


def calculate_entanglement_metrics(state_vector, num_modes=2):
    """Calculate entanglement metrics from state vector."""
    # For a two-mode system
    if num_modes != 2:
        return {"entanglement": "N/A - only for 2-mode systems"}
    
    # Convert to density matrix
    rho = np.outer(state_vector, np.conj(state_vector))
    
    # Calculate purity
    purity = np.real(np.trace(rho @ rho))
    
    # For Bell state analysis
    # Check overlap with ideal Bell states
    dim = len(state_vector)
    mode_dim = int(np.sqrt(dim))
    
    # Ideal Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 in Fock basis
    bell_plus = np.zeros(dim, dtype=complex)
    if mode_dim >= 2:
        # |00⟩ and |11⟩ indices in tensor product basis
        bell_plus[0] = 1/np.sqrt(2)  # |0,0⟩
        if dim > mode_dim + 1:
            bell_plus[mode_dim + 1] = 1/np.sqrt(2)  # |1,1⟩
    
    # Calculate fidelity with ideal Bell state
    fidelity = np.abs(np.vdot(bell_plus, state_vector))**2
    
    return {
        "purity": float(purity),
        "bell_state_fidelity": float(fidelity),
        "is_entangled": purity > 0.9 and fidelity > 0.5,
        "entanglement_quality": "excellent" if fidelity > 0.9 else "good" if fidelity > 0.7 else "moderate" if fidelity > 0.5 else "poor"
    }


def visualize_state(state_vector, mode_dim=5):
    """Create ASCII visualization of quantum state."""
    # Get significant components (amplitude > 0.01)
    significant = []
    dim = len(state_vector)
    
    for i, amp in enumerate(state_vector):
        if np.abs(amp) > 0.01:
            # Convert index to Fock basis |n1,n2⟩
            n1 = i // mode_dim
            n2 = i % mode_dim
            prob = np.abs(amp)**2
            phase = np.angle(amp)
            significant.append((n1, n2, amp, prob, phase))
    
    # Sort by probability
    significant.sort(key=lambda x: x[3], reverse=True)
    
    return significant


async def test_bell_state():
    """Test Bell state design through full simulation."""
    
    print("\n" + "="*80)
    print("🧪 BELL STATE EXPERIMENT: DESIGN → SIMULATE → VALIDATE")
    print("="*80)
    print()
    
    # Step 1: Design the experiment
    print("📐 STEP 1: DESIGN")
    print("-" * 80)
    
    config = Config()
    designer = DesignerAgent(config=config)
    
    request = AgentMessage(
        sender_id="test",
        receiver_id=designer.agent_id,
        message_type=MessageType.REQUEST,
        content={
            "action": "design_experiment",
            "type": "bell_state",
            "objectives": ["Maximize entanglement"],
            "constraints": {"max_modes": 2, "max_operations": 6}
        }
    )
    
    response = await designer.process_message(request)
    
    if not response or 'experiment' not in response.content:
        print("❌ Design failed!")
        return
    
    experiment_dict = response.content['experiment']
    print(f"✅ Design complete: {experiment_dict['description']}")
    print(f"   • Modes: {experiment_dict['num_modes']}")
    print(f"   • Steps: {len(experiment_dict['steps'])}")
    print()
    
    # Step 2: Get the actual experiment from designer's memory
    print("⚛️  STEP 2: QUANTUM SIMULATION")
    print("-" * 80)
    
    # Access the experiment directly from designer's last design
    experiment_id = experiment_dict['experiment_id']
    stored_data = designer.memory.get(f"design_{experiment_id}")
    
    # Rebuild experiment manually from the dict
    from agentic_quantum.quantum import (
        QuantumExperiment, FockState, BeamSplitter, PhaseShift,
        PhotonNumberMeasurement, ExperimentStep
    )
    
    experiment = QuantumExperiment(description=experiment_dict['description'])
    experiment.experiment_id = experiment_id
    experiment.num_modes = experiment_dict['num_modes']
    experiment.mode_dimensions = experiment_dict['mode_dimensions']
    
    # Rebuild initial state
    experiment.initial_state = FockState(photon_numbers=[0, 0])
    
    # Rebuild steps
    for step_dict in experiment_dict['steps']:
        if step_dict['step_type'] == 'state':
            continue  # Already set initial state
        elif step_dict['step_type'] == 'operation':
            comp_dict = step_dict['component']
            if comp_dict['type'] == 'beam_splitter':
                modes = comp_dict['target_modes']
                component = BeamSplitter(
                    mode1=modes[0],
                    mode2=modes[1],
                    transmittance=comp_dict['parameters']['transmittance'],
                    phase=comp_dict['parameters']['phase']
                )
                experiment.add_operation(component)
            elif comp_dict['type'] == 'phase_shift':
                component = PhaseShift(
                    mode=comp_dict['target_modes'][0],
                    phase=comp_dict['parameters']['phase']
                )
                experiment.add_operation(component)
        elif step_dict['step_type'] == 'measurement':
            # Skip measurements for this test - we only care about the final state
            pass
    
    print(f"Simulating quantum evolution...")
    print(f"Initial state: {experiment.initial_state}")
    
    # Create simulator  
    simulator = QuantumSimulator(max_dimension=experiment.mode_dimensions[0])
    
    try:
        # Execute the experiment
        results = simulator.execute_experiment(experiment)
        
        print(f"✅ Simulation complete!")
        print(f"   • Execution time: {results.execution_time:.3f}s")
        print()
        
        # Step 3: Analyze the resulting state
        print("🔬 STEP 3: QUANTUM STATE ANALYSIS")
        print("-" * 80)
        
        final_state = results.final_state
        
        # Get state vector (QuTiP object)
        state_qobj = final_state.to_qutip()
        state_vector = state_qobj.data.toarray().flatten()
        
        # Calculate entanglement metrics
        metrics = calculate_entanglement_metrics(state_vector, experiment.num_modes)
        
        print(f"📊 Quantum Metrics:")
        print(f"   • Purity: {metrics['purity']:.4f}")
        print(f"   • Bell State Fidelity: {metrics['bell_state_fidelity']:.4f}")
        print(f"   • Is Entangled: {metrics['is_entangled']}")
        print(f"   • Quality: {metrics['entanglement_quality']}")
        print()
        
        # Visualize the state
        print("📈 State Composition (Fock basis |n₁,n₂⟩):")
        print("-" * 80)
        
        significant = visualize_state(state_vector, experiment.mode_dimensions[0])
        
        print("  |n₁,n₂⟩      Amplitude          Probability    Phase")
        print("-" * 80)
        for n1, n2, amp, prob, phase in significant[:10]:  # Top 10 components
            real = np.real(amp)
            imag = np.imag(amp)
            print(f"  |{n1},{n2}⟩      {real:+.4f}{imag:+.4f}i    {prob:.4f}       {phase:+.3f}")
        
        print()
        
        # Step 4: Validate against physics expectations
        print("✓ STEP 4: VALIDATION")
        print("-" * 80)
        
        validations = []
        
        # Check 1: Is it pure?
        if metrics['purity'] > 0.99:
            validations.append(("✅", "State is pure (purity > 0.99)"))
        else:
            validations.append(("⚠️", f"State has mixed character (purity = {metrics['purity']:.3f})"))
        
        # Check 2: Is it entangled?
        if metrics['is_entangled']:
            validations.append(("✅", "State shows quantum entanglement"))
        else:
            validations.append(("❌", "State is NOT entangled"))
        
        # Check 3: Bell state fidelity
        if metrics['bell_state_fidelity'] > 0.9:
            validations.append(("✅", f"Excellent Bell state fidelity ({metrics['bell_state_fidelity']:.3f})"))
        elif metrics['bell_state_fidelity'] > 0.7:
            validations.append(("⚠️", f"Good Bell state fidelity ({metrics['bell_state_fidelity']:.3f})"))
        else:
            validations.append(("❌", f"Poor Bell state fidelity ({metrics['bell_state_fidelity']:.3f})"))
        
        for status, msg in validations:
            print(f"{status} {msg}")
        
        print()
        
        # Step 5: Figures of Merit
        print("📈 STEP 5: FIGURES OF MERIT")
        print("-" * 80)
        
        if results.figures_of_merit:
            for name, value in results.figures_of_merit.items():
                if isinstance(value, (int, float)):
                    print(f"   • {name}: {value:.4f}")
                else:
                    print(f"   • {name}: {value}")
        else:
            print("   No figures of merit calculated")
        
        print()
        
        # Final verdict
        print("="*80)
        if metrics['is_entangled'] and metrics['bell_state_fidelity'] > 0.7:
            print("✨ SUCCESS! The template design DOES produce entangled Bell states!")
            print(f"   The experimental protocol is physically valid.")
        elif metrics['bell_state_fidelity'] > 0.5:
            print("⚠️  PARTIAL SUCCESS. The design produces entanglement but not ideal Bell states.")
            print(f"   Consider using LLM-based design or optimization for better results.")
        else:
            print("❌ FAILURE. The template does NOT produce proper Bell states.")
            print(f"   This design needs refinement.")
        print("="*80)
        print()
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bell_state())
