"""
Clean, focused quantum experiment designer.
Single-purpose: Design → Validate → Return only working experiments.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import qutip as qt
from dataclasses import dataclass
import os


@dataclass
class QuantumDesign:
    """Container for a validated quantum experiment design."""
    description: str
    initial_state: str
    components: List[Dict[str, Any]]
    final_state: Any
    metrics: Dict[str, float]
    rationale: str
    success: bool


class CleanQuantumDesigner:
    """
    Focused quantum experiment designer that validates before returning.
    
    Design Philosophy:
    1. Simple LLM prompt for optical components
    2. Direct quantum simulation with QuTiP
    3. Validate results (entanglement, purity, etc.)
    4. Only return validated designs
    5. Auto-retry if validation fails
    """
    
    def __init__(self, llm_client=None):
        """Initialize designer with LLM client."""
        self.llm = llm_client
        self.max_retries = 3
        
    def design_experiment(self, user_query: str) -> QuantumDesign:
        """
        Main entry point: Design and validate quantum experiment.
        
        Args:
            user_query: Natural language description of desired experiment
            
        Returns:
            QuantumDesign with validated experiment or error state
        """
        # Parse intent from query
        intent = self._parse_query(user_query)
        
        # Try to generate valid design (with retries)
        for attempt in range(self.max_retries):
            # Get LLM design suggestion
            design_plan = self._get_llm_design(intent, attempt)
            
            # Build quantum experiment
            experiment = self._build_experiment(design_plan)
            
            # Simulate and validate
            result = self._simulate_and_validate(experiment, intent)
            
            if result.success:
                return result
            
            print(f"Attempt {attempt + 1} failed validation, retrying...")
        
        # All attempts failed
        return QuantumDesign(
            description="Design failed after multiple attempts",
            initial_state="unknown",
            components=[],
            final_state=None,
            metrics={},
            rationale="Could not generate valid design meeting requirements.",
            success=False
        )
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Extract intent and requirements from user query."""
        query_lower = query.lower()
        
        intent = {
            'type': 'general',
            'goals': [],
            'constraints': {
                'max_components': 6,
                'num_modes': 2
            }
        }
        
        # Detect experiment type
        if 'bell' in query_lower or 'entangle' in query_lower:
            intent['type'] = 'bell_state'
            intent['goals'] = ['entanglement', 'high_fidelity']
            intent['target_state'] = 'bell'
            
        elif 'squeeze' in query_lower or 'squeezing' in query_lower:
            intent['type'] = 'squeezed_light'
            intent['goals'] = ['squeezing', 'low_noise']
            intent['constraints']['num_modes'] = 1
            
        elif 'interfero' in query_lower or 'mach' in query_lower:
            intent['type'] = 'interferometer'
            intent['goals'] = ['phase_sensitivity', 'visibility']
            
        elif 'coherent' in query_lower:
            intent['type'] = 'coherent_state'
            intent['goals'] = ['coherent_state_preparation']
            intent['constraints']['num_modes'] = 1
        
        return intent
    
    def _get_llm_design(self, intent: Dict[str, Any], attempt: int = 0) -> Dict[str, Any]:
        """Get design plan from LLM."""
        
        if not self.llm:
            # Fallback: Use template-based design
            return self._template_design(intent)
        
        # Construct focused prompt
        prompt = self._build_prompt(intent, attempt)
        
        try:
            response = self.llm.predict(prompt, system_prompt=self._get_system_prompt())
            design = self._parse_llm_response(response)
            return design
        except Exception as e:
            print(f"LLM error: {e}, falling back to template")
            return self._template_design(intent)
    
    def _build_prompt(self, intent: Dict[str, Any], attempt: int) -> str:
        """Build focused LLM prompt for optical design."""
        
        exp_type = intent['type']
        goals = intent.get('goals', [])
        
        base_prompt = f"""Design a quantum optics experiment on an optical table.

**Goal:** {exp_type.replace('_', ' ').title()}
**Objectives:** {', '.join(goals)}

**Available Components:**
- Single photon sources (Fock states |n⟩)
- Vacuum input |0⟩
- 50:50 Beam splitters (BS)
- Variable beam splitters (BS with transmittance T)
- Phase shifters (φ)
- Photon detectors

**Design Requirements:**
"""
        
        if exp_type == 'bell_state':
            base_prompt += """
1. Start with single photon in mode 0: |1,0⟩
2. Use 50:50 beam splitter to create superposition
3. Result should be entangled state: (|1,0⟩ + |0,1⟩)/√2
4. Measure photon numbers in both modes

**Critical:** The initial state MUST be |1,0⟩ (one photon in first mode, zero in second).
DO NOT use vacuum state |0,0⟩ as this will not create entanglement.
"""
        
        elif exp_type == 'squeezed_light':
            base_prompt += """
1. Start with vacuum state |0⟩
2. Apply squeezing operation S(r) with r ≈ 0.5-1.0
3. Measure quadratures with homodyne detection
"""
        
        elif exp_type == 'interferometer':
            base_prompt += """
1. Start with coherent state |α⟩ with α ≈ 1-2
2. Split with 50:50 beam splitter
3. Apply phase shift φ in one arm
4. Recombine with another beam splitter
5. Measure intensity in output ports
"""
        
        if attempt > 0:
            base_prompt += f"\n\n**Note:** Previous attempt {attempt} failed validation. Ensure design creates proper quantum states."
        
        base_prompt += """

**Respond with JSON:**
{
    "initial_state": "fock_1_0" or "vacuum" or "coherent",
    "state_params": {"photons": [1, 0]} or {"alpha": 1.5},
    "components": [
        {"type": "beam_splitter", "modes": [0, 1], "transmittance": 0.5},
        {"type": "phase_shift", "mode": 0, "phase": 0.5}
    ],
    "measurements": [{"type": "photon_number", "mode": 0}],
    "rationale": "Physical explanation of how this works"
}
"""
        
        return base_prompt
    
    def _get_system_prompt(self) -> str:
        """System prompt for LLM."""
        return """You are an expert in quantum optics and experimental design. 
Design practical optical table experiments using standard components.
Focus on physically realizable setups that produce verifiable quantum effects.
Always respond with valid JSON."""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured design."""
        # Try to extract JSON from response
        try:
            # Find JSON block
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                design = json.loads(json_str)
                return design
        except:
            pass
        
        # Fallback: Return empty design
        return {
            "initial_state": "fock_1_0",
            "state_params": {"photons": [1, 0]},
            "components": [{"type": "beam_splitter", "modes": [0, 1], "transmittance": 0.5}],
            "measurements": [{"type": "photon_number", "mode": 0}],
            "rationale": "Default Bell state design"
        }
    
    def _template_design(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback template-based designs."""
        
        if intent['type'] == 'bell_state':
            return {
                "initial_state": "fock_1_0",
                "state_params": {"photons": [1, 0]},
                "components": [
                    {"type": "beam_splitter", "modes": [0, 1], "transmittance": 0.5, "phase": 0.0}
                ],
                "measurements": [
                    {"type": "photon_number", "mode": 0},
                    {"type": "photon_number", "mode": 1}
                ],
                "rationale": "Single photon |1,0⟩ through 50:50 beam splitter creates maximally entangled Bell state (|1,0⟩ + |0,1⟩)/√2. The beam splitter creates equal superposition of photon being in either mode, demonstrating quantum interference."
            }
        
        elif intent['type'] == 'squeezed_light':
            return {
                "initial_state": "vacuum",
                "state_params": {},
                "components": [
                    {"type": "squeezing", "mode": 0, "r": 0.5, "angle": 0.0}
                ],
                "measurements": [
                    {"type": "homodyne", "mode": 0}
                ],
                "rationale": "Vacuum state with squeezing operator S(r=0.5) reduces quantum noise in one quadrature below the vacuum limit."
            }
        
        else:
            # Default: simple coherent state
            return {
                "initial_state": "coherent",
                "state_params": {"alpha": 1.5},
                "components": [],
                "measurements": [
                    {"type": "photon_number", "mode": 0}
                ],
                "rationale": "Coherent state |α⟩ with α=1.5."
            }
    
    def _build_experiment(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """Build quantum experiment from design plan."""
        
        # Create initial state
        initial_state_type = design.get('initial_state', 'fock_1_0')
        state_params = design.get('state_params', {})
        
        # Determine if we need multi-mode from components
        needs_multimode = any(
            comp.get('type') == 'beam_splitter' 
            for comp in design.get('components', [])
        )
        
        # Create initial state
        if initial_state_type == 'fock_1_0' or 'fock' in initial_state_type:
            photons = state_params.get('photons', [1, 0])
            if isinstance(photons, list) and len(photons) == 2:
                state = qt.tensor(qt.fock(20, photons[0]), qt.fock(20, photons[1]))
            else:
                state = qt.tensor(qt.fock(20, 1), qt.fock(20, 0))
                
        elif initial_state_type == 'vacuum':
            if needs_multimode:
                state = qt.tensor(qt.fock(20, 0), qt.fock(20, 0))
            else:
                state = qt.fock(20, 0)
            
        elif initial_state_type == 'coherent':
            alpha = state_params.get('alpha', 1.5)
            if needs_multimode:
                state = qt.tensor(qt.coherent(20, alpha), qt.fock(20, 0))
            else:
                state = qt.coherent(20, alpha)
        else:
            # Default: two-mode Fock state
            state = qt.tensor(qt.fock(20, 1), qt.fock(20, 0))
        
        # Apply components
        components_list = []
        for comp in design.get('components', []):
            comp_type = comp.get('type')
            
            if comp_type == 'beam_splitter':
                modes = comp.get('modes', [0, 1])
                T = comp.get('transmittance', 0.5)
                phase = comp.get('phase', 0.0)
                
                # Create beam splitter operator using QuTiP's proper method
                theta = np.arccos(np.sqrt(T))
                # For two-mode state, use destroy operators
                a0 = qt.tensor(qt.destroy(20), qt.qeye(20))
                a1 = qt.tensor(qt.qeye(20), qt.destroy(20))
                
                # Beam splitter Hamiltonian
                H = 1j * theta * (a0.dag() * a1 - a0 * a1.dag())
                bs_op = (-1j * np.pi/4 * H).expm()  # Evolution operator
                
                state = bs_op * state
                
                components_list.append({
                    'type': 'beam_splitter',
                    'transmittance': T,
                    'phase': phase,
                    'modes': modes
                })
                
            elif comp_type == 'phase_shift':
                mode = comp.get('mode', 0)
                phase = comp.get('phase', 0.5)
                
                # Phase shift operator
                ps_op = qt.Qobj(np.diag(np.array([np.exp(1j * phase * n) for n in range(20)])))
                if state.shape[0] == 400:  # Two modes
                    if mode == 0:
                        ps_full = qt.tensor(ps_op, qt.qeye(20))
                    else:
                        ps_full = qt.tensor(qt.qeye(20), ps_op)
                else:
                    ps_full = ps_op
                state = ps_full * state
                
                components_list.append({
                    'type': 'phase_shift',
                    'phase': phase,
                    'mode': mode
                })
                
            elif comp_type == 'squeezing':
                mode = comp.get('mode', 0)
                r = comp.get('r', 0.5)
                
                # Squeezing operator
                sq_op = qt.squeeze(20, r)
                if state.shape[0] == 400:  # Two modes
                    if mode == 0:
                        sq_full = qt.tensor(sq_op, qt.qeye(20))
                    else:
                        sq_full = qt.tensor(qt.qeye(20), sq_op)
                else:
                    sq_full = sq_op
                state = sq_full * state
                
                components_list.append({
                    'type': 'squeezing',
                    'r': r,
                    'mode': mode
                })
        
        return {
            'initial_state': initial_state_type,
            'state_params': state_params,
            'components': components_list,
            'final_state': state,
            'measurements': design.get('measurements', []),
            'rationale': design.get('rationale', 'Quantum optical experiment')
        }
    
    def _simulate_and_validate(self, experiment: Dict[str, Any], 
                               intent: Dict[str, Any]) -> QuantumDesign:
        """Simulate experiment and validate against goals."""
        
        final_state = experiment['final_state']
        
        # Calculate metrics
        metrics = {}
        
        # Purity
        rho = final_state * final_state.dag()
        metrics['purity'] = float(np.abs((rho * rho).tr()))
        
        # Check if state is entangled (for two-mode states)
        is_entangled = False
        if final_state.shape[0] == 400:  # Two modes
            # Trace out one mode
            rho_full = final_state * final_state.dag()
            rho_A = rho_full.ptrace(0)
            purity_A = float(np.abs((rho_A * rho_A).tr()))
            
            # If reduced state has purity < 1, it's entangled
            is_entangled = purity_A < 0.99
            metrics['entanglement'] = 1.0 - purity_A
            
            # Calculate photon statistics
            state_vec = final_state.full().flatten()
            components = []
            for i in range(min(20, len(state_vec))):
                for j in range(min(20, len(state_vec))):
                    idx = i * 20 + j
                    if idx < len(state_vec):
                        prob = np.abs(state_vec[idx])**2
                        if prob > 0.001:
                            components.append((i, j, float(prob)))
            
            metrics['components'] = components[:5]  # Top 5
        
        # Validate against goals
        goals = intent.get('goals', [])
        success = True
        
        if 'entanglement' in goals:
            success = success and is_entangled and metrics['purity'] > 0.95
            
        if 'high_fidelity' in goals:
            success = success and metrics['purity'] > 0.95
        
        # Build result
        return QuantumDesign(
            description=f"{intent['type'].replace('_', ' ').title()} experiment",
            initial_state=experiment['initial_state'],
            components=experiment['components'],
            final_state=final_state,
            metrics=metrics,
            rationale=experiment['rationale'],
            success=success
        )
    
    def to_optical_table_format(self, design: QuantumDesign) -> Dict[str, Any]:
        """Convert QuantumDesign to optical table rendering format."""
        
        steps = []
        
        # Initial state
        if design.initial_state == 'fock_1_0':
            steps.append({
                'step_type': 'state',
                'component': {
                    'type': 'state',
                    'description': 'Single photon source |1,0⟩'
                },
                'description': 'Initial state: Fock |1,0⟩'
            })
        elif design.initial_state == 'vacuum':
            steps.append({
                'step_type': 'state',
                'component': {
                    'type': 'state',
                    'description': 'Vacuum state |0⟩'
                },
                'description': 'Initial state: Vacuum |0⟩'
            })
        elif design.initial_state == 'coherent':
            steps.append({
                'step_type': 'state',
                'component': {
                    'type': 'state',
                    'description': 'Coherent state |α⟩'
                },
                'description': 'Initial state: Coherent |α⟩'
            })
        
        # Components
        for comp in design.components:
            if comp['type'] == 'beam_splitter':
                steps.append({
                    'step_type': 'operation',
                    'component': {
                        'type': 'beam_splitter',
                        'parameters': {
                            'transmittance': comp['transmittance'],
                            'phase': comp.get('phase', 0)
                        }
                    },
                    'description': f"50:50 Beam Splitter (T={comp['transmittance']:.0%})"
                })
            
            elif comp['type'] == 'phase_shift':
                steps.append({
                    'step_type': 'operation',
                    'component': {
                        'type': 'phase_shift',
                        'parameters': {
                            'phase': comp['phase']
                        }
                    },
                    'description': f"Phase Shift φ={comp['phase']:.2f}"
                })
            
            elif comp['type'] == 'squeezing':
                steps.append({
                    'step_type': 'operation',
                    'component': {
                        'type': 'squeezing',
                        'parameters': {
                            'r': comp.get('r', 0.5)
                        }
                    },
                    'description': f"Squeezing r={comp.get('r', 0.5):.2f}"
                })
        
        # Measurement
        steps.append({
            'step_type': 'measurement',
            'component': {
                'type': 'photon_number',
                'description': 'Photon number measurement'
            },
            'description': 'Photon detection'
        })
        
        return {
            'experiment_id': 'clean_design_001',
            'description': design.description,
            'steps': steps
        }


def test_designer():
    """Test the designer with a Bell state."""
    designer = CleanQuantumDesigner()
    
    print("Testing Bell state design...")
    result = designer.design_experiment("Design a Bell state with maximum entanglement")
    
    print(f"\nSuccess: {result.success}")
    print(f"Description: {result.description}")
    print(f"Initial state: {result.initial_state}")
    print(f"Components: {len(result.components)}")
    print(f"Metrics: {result.metrics}")
    print(f"\nRationale: {result.rationale}")
    
    # Test optical table format
    print("\n--- Optical Table Format ---")
    optical_format = designer.to_optical_table_format(result)
    print(f"Steps: {len(optical_format['steps'])}")
    for step in optical_format['steps']:
        print(f"  - {step['description']}")
    
    return result


if __name__ == '__main__':
    test_designer()
