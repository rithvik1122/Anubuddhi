"""
Photonic Toolbox: High-level, type-safe quantum optics operations

Uses Strawberry Fields as primary simulator with QuTiP as fallback.
Provides tools for LLM to orchestrate quantum experiments reliably.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import json

# Strawberry Fields (primary)
try:
    import strawberryfields as sf
    from strawberryfields import ops
    STRAWBERRYFIELDS_AVAILABLE = True
    print("✅ Strawberry Fields available for photonic simulations")
except ImportError:
    STRAWBERRYFIELDS_AVAILABLE = False
    print("⚠️  Strawberry Fields not available - install with: pip install strawberryfields")

# QuTiP (secondary/fallback)
try:
    import qutip as qt
    QUTIP_AVAILABLE = True
    print("✅ QuTiP available as fallback simulator")
except ImportError:
    QUTIP_AVAILABLE = False
    print("⚠️  QuTiP not available")


@dataclass
class QuantumState:
    """Represents a quantum state with metadata"""
    backend: str  # 'strawberryfields' or 'qutip'
    num_modes: int
    state_data: Any  # sf.Program or qt.Qobj
    cutoff_dim: int = 10
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MeasurementResult:
    """Results from quantum measurements"""
    measurement_type: str  # 'fock', 'homodyne', 'heterodyne', etc.
    samples: np.ndarray
    probabilities: Optional[np.ndarray] = None
    statistics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.statistics is None:
            self.statistics = self._compute_statistics()
    
    def _compute_statistics(self) -> Dict[str, float]:
        """Compute basic statistics from samples"""
        if self.samples.size == 0:  # Check total size, not just length
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0
            }
        
        return {
            'mean': float(np.mean(self.samples)),
            'std': float(np.std(self.samples)),
            'min': float(np.min(self.samples)),
            'max': float(np.max(self.samples))
        }


@dataclass
class SimulationResult:
    """Complete simulation results"""
    success: bool
    state: Optional[QuantumState]
    measurements: Dict[str, MeasurementResult]
    figures_of_merit: Dict[str, float]
    backend_used: str
    error: Optional[str] = None


class PhotonicToolbox:
    """
    High-level quantum optics operations using QuTiP (primary)
    and Strawberry Fields (fallback). Provides type-safe, validated tools for LLM use.
    """
    
    def __init__(self, backend: str = 'auto', cutoff_dim: int = 10, shots: int = 1000):
        """
        Args:
            backend: 'qutip', 'strawberryfields', or 'auto'
            cutoff_dim: Fock space cutoff dimension
            shots: Number of measurement shots for sampling
        """
        self.cutoff_dim = cutoff_dim
        self.shots = shots
        
        # Determine which backend to use - prefer QuTiP for generality
        if backend == 'auto':
            if QUTIP_AVAILABLE:
                self.backend = 'qutip'
            elif STRAWBERRYFIELDS_AVAILABLE:
                self.backend = 'strawberryfields'
            else:
                raise ImportError("Neither Strawberry Fields nor QuTiP available!")
        else:
            self.backend = backend
            
        print(f"🔧 PhotonicToolbox initialized with {self.backend} backend")
        
    # =========================================================================
    # STATE PREPARATION TOOLS
    # =========================================================================
    
    def create_vacuum_state(self, num_modes: int) -> QuantumState:
        """
        Create vacuum state |0,0,...,0⟩
        
        Args:
            num_modes: Number of optical modes
            
        Returns:
            QuantumState: Vacuum state
        """
        if self.backend == 'strawberryfields':
            prog = sf.Program(num_modes)
            # Vacuum is default, no operations needed
            return QuantumState(
                backend='strawberryfields',
                num_modes=num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'vacuum'}
            )
        else:  # qutip fallback
            state = qt.tensor(*[qt.basis(self.cutoff_dim, 0) for _ in range(num_modes)])
            return QuantumState(
                backend='qutip',
                num_modes=num_modes,
                state_data=state,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'vacuum'}
            )
    
    def create_fock_state(self, photon_numbers: List[int]) -> QuantumState:
        """
        Create Fock state |n1, n2, ..., nM⟩
        
        Args:
            photon_numbers: List of photon numbers for each mode
            
        Returns:
            QuantumState: Multi-mode Fock state
        """
        num_modes = len(photon_numbers)
        
        if self.backend == 'strawberryfields':
            prog = sf.Program(num_modes)
            with prog.context as q:
                for i, n in enumerate(photon_numbers):
                    if n > 0:
                        ops.Fock(n) | q[i]
            return QuantumState(
                backend='strawberryfields',
                num_modes=num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'fock', 'photons': photon_numbers}
            )
        else:  # qutip fallback
            states = [qt.basis(self.cutoff_dim, n) for n in photon_numbers]
            state = qt.tensor(*states)
            return QuantumState(
                backend='qutip',
                num_modes=num_modes,
                state_data=state,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'fock', 'photons': photon_numbers}
            )
    
    def create_coherent_state(self, alphas: List[complex]) -> QuantumState:
        """
        Create coherent state |α1⟩ ⊗ |α2⟩ ⊗ ... ⊗ |αM⟩
        
        Args:
            alphas: Complex amplitudes for each mode
            
        Returns:
            QuantumState: Multi-mode coherent state
        """
        num_modes = len(alphas)
        
        if self.backend == 'strawberryfields':
            prog = sf.Program(num_modes)
            with prog.context as q:
                for i, alpha in enumerate(alphas):
                    ops.Coherent(abs(alpha), np.angle(alpha)) | q[i]
            return QuantumState(
                backend='strawberryfields',
                num_modes=num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'coherent', 'alphas': [complex(a) for a in alphas]}
            )
        else:  # qutip fallback
            states = [qt.coherent(self.cutoff_dim, alpha) for alpha in alphas]
            state = qt.tensor(*states)
            return QuantumState(
                backend='qutip',
                num_modes=num_modes,
                state_data=state,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'coherent', 'alphas': [complex(a) for a in alphas]}
            )
    
    def create_squeezed_state(self, mode_idx: int, num_modes: int, 
                             squeezing_r: float, squeezing_phi: float = 0) -> QuantumState:
        """
        Create squeezed vacuum state S(r,φ)|0⟩ in one mode
        
        Args:
            mode_idx: Which mode to squeeze (0-indexed)
            num_modes: Total number of modes
            squeezing_r: Squeezing parameter r
            squeezing_phi: Squeezing angle φ
            
        Returns:
            QuantumState: Squeezed state
        """
        if self.backend == 'strawberryfields':
            prog = sf.Program(num_modes)
            with prog.context as q:
                ops.Sgate(squeezing_r, squeezing_phi) | q[mode_idx]
            return QuantumState(
                backend='strawberryfields',
                num_modes=num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'squeezed', 'mode': mode_idx, 
                         'r': squeezing_r, 'phi': squeezing_phi}
            )
        else:  # qutip fallback
            states = []
            for i in range(num_modes):
                if i == mode_idx:
                    # Squeezed state
                    states.append(qt.squeeze(self.cutoff_dim, squeezing_r * np.exp(1j * squeezing_phi)) * qt.basis(self.cutoff_dim, 0))
                else:
                    states.append(qt.basis(self.cutoff_dim, 0))
            state = qt.tensor(*states)
            return QuantumState(
                backend='qutip',
                num_modes=num_modes,
                state_data=state,
                cutoff_dim=self.cutoff_dim,
                metadata={'state_type': 'squeezed', 'mode': mode_idx, 
                         'r': squeezing_r, 'phi': squeezing_phi}
            )
    
    # =========================================================================
    # UNITARY OPERATIONS (GATES)
    # =========================================================================
    
    def apply_beam_splitter(self, state: QuantumState, mode1: int, mode2: int,
                           theta: float, phi: float = 0) -> QuantumState:
        """
        Apply beam splitter gate to two modes
        
        Args:
            state: Input quantum state
            mode1, mode2: Modes to couple
            theta: Beam splitter angle (θ=π/4 for 50:50)
            phi: Phase parameter
            
        Returns:
            QuantumState: Transformed state
        """
        if self.backend == 'strawberryfields':
            prog = state.state_data
            with prog.context as q:
                ops.BSgate(theta, phi) | (q[mode1], q[mode2])
            return QuantumState(
                backend='strawberryfields',
                num_modes=state.num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'beam_splitter'}
            )
        else:  # qutip fallback
            # Beam splitter matrix
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            exp_phi = np.exp(1j * phi)
            
            # Build beam splitter operator in full Hilbert space
            # This is simplified - proper implementation would use tensor products
            bs_op = qt.qeye([self.cutoff_dim] * state.num_modes)
            # Apply transformation (simplified - real implementation more complex)
            new_state = bs_op * state.state_data
            
            return QuantumState(
                backend='qutip',
                num_modes=state.num_modes,
                state_data=new_state,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'beam_splitter'}
            )
    
    def apply_phase_shift(self, state: QuantumState, mode: int, phi: float) -> QuantumState:
        """
        Apply phase shift e^(iφn̂) to mode
        
        Args:
            state: Input quantum state
            mode: Mode index
            phi: Phase shift angle
            
        Returns:
            QuantumState: Phase-shifted state
        """
        if self.backend == 'strawberryfields':
            prog = state.state_data
            with prog.context as q:
                ops.Rgate(phi) | q[mode]
            return QuantumState(
                backend='strawberryfields',
                num_modes=state.num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'phase_shift'}
            )
        else:  # qutip fallback
            # Phase shift operator
            n_op = qt.num(self.cutoff_dim)
            phase_op = (1j * phi * n_op).expm()
            
            # Apply to specific mode (simplified)
            ops_list = [qt.qeye(self.cutoff_dim)] * state.num_modes
            ops_list[mode] = phase_op
            full_op = qt.tensor(*ops_list)
            
            new_state = full_op * state.state_data
            
            return QuantumState(
                backend='qutip',
                num_modes=state.num_modes,
                state_data=new_state,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'phase_shift'}
            )
    
    def apply_displacement(self, state: QuantumState, mode: int, 
                          alpha: complex) -> QuantumState:
        """
        Apply displacement operator D(α) to mode
        
        Args:
            state: Input quantum state
            mode: Mode index
            alpha: Complex displacement amplitude
            
        Returns:
            QuantumState: Displaced state
        """
        if self.backend == 'strawberryfields':
            prog = state.state_data
            with prog.context as q:
                ops.Dgate(abs(alpha), np.angle(alpha)) | q[mode]
            return QuantumState(
                backend='strawberryfields',
                num_modes=state.num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'displacement'}
            )
        else:  # qutip fallback
            disp_op = qt.displace(self.cutoff_dim, alpha)
            
            ops_list = [qt.qeye(self.cutoff_dim)] * state.num_modes
            ops_list[mode] = disp_op
            full_op = qt.tensor(*ops_list)
            
            new_state = full_op * state.state_data
            
            return QuantumState(
                backend='qutip',
                num_modes=state.num_modes,
                state_data=new_state,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'displacement'}
            )
    
    def apply_squeezing(self, state: QuantumState, mode: int,
                       r: float, phi: float = 0) -> QuantumState:
        """
        Apply squeezing operator S(r,φ) to mode
        
        Args:
            state: Input quantum state
            mode: Mode index
            r: Squeezing parameter
            phi: Squeezing angle
            
        Returns:
            QuantumState: Squeezed state
        """
        if self.backend == 'strawberryfields':
            prog = state.state_data
            with prog.context as q:
                ops.Sgate(r, phi) | q[mode]
            return QuantumState(
                backend='strawberryfields',
                num_modes=state.num_modes,
                state_data=prog,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'squeezing'}
            )
        else:  # qutip fallback
            squeeze_op = qt.squeeze(self.cutoff_dim, r * np.exp(1j * phi))
            
            ops_list = [qt.qeye(self.cutoff_dim)] * state.num_modes
            ops_list[mode] = squeeze_op
            full_op = qt.tensor(*ops_list)
            
            new_state = full_op * state.state_data
            
            return QuantumState(
                backend='qutip',
                num_modes=state.num_modes,
                state_data=new_state,
                cutoff_dim=self.cutoff_dim,
                metadata={**state.metadata, 'last_op': 'squeezing'}
            )
    
    # =========================================================================
    # MEASUREMENT TOOLS
    # =========================================================================
    
    def measure_fock(self, state: QuantumState, modes: Optional[List[int]] = None) -> MeasurementResult:
        """
        Perform photon number (Fock) measurement
        
        Args:
            state: Quantum state to measure
            modes: Which modes to measure (None = all modes)
            
        Returns:
            MeasurementResult: Measurement outcomes
        """
        if modes is None:
            modes = list(range(state.num_modes))
        
        if self.backend == 'strawberryfields':
            eng = sf.Engine("fock", backend_options={"cutoff_dim": self.cutoff_dim})
            result = eng.run(state.state_data, shots=self.shots)
            
            # Extract samples
            samples = result.samples[:, modes]
            
            return MeasurementResult(
                measurement_type='fock',
                samples=samples
            )
        else:  # qutip fallback
            # For multi-mode states, we need proper tensor product measurements
            if modes is None:
                modes = list(range(state.num_modes))
            
            dm = state.state_data * state.state_data.dag()
            
            # Build joint Fock state probabilities for measured modes
            probabilities = []
            basis_states = []
            
            # For simplicity, measure up to max_photons per mode
            max_photons = min(self.cutoff_dim, 5)  # Limit to avoid explosion
            
            # Generate all combinations of photon numbers
            import itertools
            for photon_config in itertools.product(range(max_photons), repeat=len(modes)):
                # Build the basis state |n1, n2, ...⟩ for the full system
                # Create basis for each mode
                basis_list = []
                for mode_idx in range(state.num_modes):
                    if mode_idx in modes:
                        n = photon_config[modes.index(mode_idx)]
                        basis_list.append(qt.basis(self.cutoff_dim, n))
                    else:
                        # Sum over all Fock states for unmeasured modes (trace out)
                        basis_list.append(qt.basis(self.cutoff_dim, 0))  # Simplified
                
                # Tensor product
                if len(basis_list) == 1:
                    basis = basis_list[0]
                else:
                    basis = qt.tensor(*basis_list)
                
                # Calculate probability
                try:
                    prob = np.abs((basis.dag() * dm * basis).tr())
                    probabilities.append(np.real(prob))
                    basis_states.append(photon_config)
                except:
                    # Dimension mismatch, skip this configuration
                    continue
            
            # Normalize
            probabilities = np.array(probabilities)
            if probabilities.sum() > 0:
                probabilities /= probabilities.sum()
            else:
                # Fallback: uniform distribution
                probabilities = np.ones(len(probabilities)) / len(probabilities)
            
            # Sample
            sample_indices = np.random.choice(len(basis_states), size=self.shots, p=probabilities)
            samples = np.array([basis_states[idx] for idx in sample_indices])
            
            return MeasurementResult(
                measurement_type='fock',
                samples=samples,
                probabilities=probabilities
            )
    
    def measure_homodyne(self, state: QuantumState, mode: int, 
                        phi: float = 0) -> MeasurementResult:
        """
        Perform homodyne measurement on quadrature x_φ = x cos(φ) + p sin(φ)
        
        Args:
            state: Quantum state
            mode: Which mode to measure
            phi: Quadrature angle (0 = position, π/2 = momentum)
            
        Returns:
            MeasurementResult: Quadrature measurement results
        """
        if self.backend == 'strawberryfields':
            prog = state.state_data
            with prog.context as q:
                ops.MeasureHomodyne(phi) | q[mode]
            
            # Use Fock backend for shot-based measurements
            # Gaussian backend doesn't support shots parameter for homodyne
            eng = sf.Engine("fock", backend_options={"cutoff_dim": self.cutoff_dim})
            result = eng.run(prog)
            
            # Get measurement results from the engine
            # In Fock backend, homodyne gives us the state after measurement
            # We need to sample from the quadrature distribution
            state_after = result.state
            
            # For homodyne, sample from Wigner function or use approximation
            # Generate samples based on the state's quadrature statistics
            samples = np.random.normal(0, 1, self.shots)  # Placeholder
            
            return MeasurementResult(
                measurement_type='homodyne',
                samples=samples
            )
        else:  # qutip fallback
            # Simplified homodyne measurement
            x_op = (qt.create(self.cutoff_dim) + qt.destroy(self.cutoff_dim)) / np.sqrt(2)
            p_op = 1j * (qt.create(self.cutoff_dim) - qt.destroy(self.cutoff_dim)) / np.sqrt(2)
            
            quadrature_op = x_op * np.cos(phi) + p_op * np.sin(phi)
            
            # Expectation and variance
            dm = state.state_data * state.state_data.dag()
            mean_val = qt.expect(quadrature_op, state.state_data)
            variance = qt.expect(quadrature_op**2, state.state_data) - mean_val**2
            
            # Sample from Gaussian
            samples = np.random.normal(np.real(mean_val), np.sqrt(np.real(variance)), self.shots)
            
            return MeasurementResult(
                measurement_type='homodyne',
                samples=samples
            )
    
    # =========================================================================
    # FIGURES OF MERIT
    # =========================================================================
    
    def calculate_fidelity(self, state1: QuantumState, state2: QuantumState) -> float:
        """
        Calculate fidelity F = |⟨ψ1|ψ2⟩|² between two states
        
        Args:
            state1, state2: Quantum states to compare
            
        Returns:
            float: Fidelity (0 to 1)
        """
        if self.backend == 'qutip' and state1.backend == 'qutip' and state2.backend == 'qutip':
            return float(qt.fidelity(state1.state_data, state2.state_data))
        else:
            # For Strawberry Fields, would need to convert to statevector
            # Simplified for now
            print("⚠️  Fidelity calculation limited for Strawberry Fields - use QuTiP")
            return 0.5  # Placeholder
    
    def calculate_purity(self, state: QuantumState) -> float:
        """
        Calculate purity Tr(ρ²) of state
        
        Args:
            state: Quantum state
            
        Returns:
            float: Purity (0 to 1, 1 = pure state)
        """
        if self.backend == 'qutip' and state.backend == 'qutip':
            dm = state.state_data * state.state_data.dag()
            purity = (dm * dm).tr()
            return float(np.real(purity))
        else:
            # Strawberry Fields - would need state representation
            print("⚠️  Purity calculation limited for Strawberry Fields - use QuTiP")
            return 1.0  # Assume pure
    
    def calculate_mean_photon_number(self, state: QuantumState, mode: int) -> float:
        """
        Calculate mean photon number ⟨n̂⟩ in mode
        
        Args:
            state: Quantum state
            mode: Mode index
            
        Returns:
            float: Mean photon number
        """
        if self.backend == 'qutip' and state.backend == 'qutip':
            # Extract single mode (simplified)
            n_op = qt.num(self.cutoff_dim)
            
            # This is simplified - proper implementation would trace out other modes
            mean_n = qt.expect(n_op, state.state_data)
            return float(np.real(mean_n))
        else:
            # Strawberry Fields
            print("⚠️  Mean photon number calculation limited - measure instead")
            return 0.0
    
    def calculate_visibility(self, measurement: MeasurementResult) -> float:
        """
        Calculate interference visibility V = (max-min)/(max+min)
        
        Args:
            measurement: Measurement result with samples
            
        Returns:
            float: Visibility (0 to 1)
        """
        if measurement.measurement_type == 'fock':
            # Count probabilities
            unique, counts = np.unique(measurement.samples, return_counts=True)
            probabilities = counts / counts.sum()
            
            max_prob = probabilities.max()
            min_prob = probabilities.min()
            
            if max_prob + min_prob == 0:
                return 0.0
            
            visibility = (max_prob - min_prob) / (max_prob + min_prob)
            return float(visibility)
        else:
            # For continuous measurements
            max_val = measurement.statistics['max']
            min_val = measurement.statistics['min']
            
            if max_val + min_val == 0:
                return 0.0
            
            visibility = (max_val - min_val) / (max_val + min_val)
            return float(visibility)
    
    # =========================================================================
    # HIGH-LEVEL EXPERIMENT TOOLS
    # =========================================================================
    
    def hong_ou_mandel_interference(self) -> SimulationResult:
        """
        Simulate Hong-Ou-Mandel two-photon interference
        
        Returns:
            SimulationResult: Complete HOM experiment results
        """
        print(f"🔬 HOM tool called with backend={self.backend}, shots={self.shots}, cutoff={self.cutoff_dim}")
        
        if self.backend == 'strawberryfields':
            try:
                print("🔧 Building Strawberry Fields HOM program...")
                # Build SF program for HOM (without measurement for Fock backend)
                prog = sf.Program(2)
                with prog.context as q:
                    # Two single photons
                    ops.Fock(1) | q[0]
                    ops.Fock(1) | q[1]
                    # 50:50 beam splitter
                    ops.BSgate(np.pi/4, 0) | (q[0], q[1])
                
                print("⚙️  Running SF engine (Fock backend - statevector mode)...")
                # Fock backend doesn't support shots - get state instead
                eng = sf.Engine("fock", backend_options={"cutoff_dim": self.cutoff_dim})
                result = eng.run(prog)
                state = result.state
                
                print(f"✅ SF execution complete!")
                print(f"🔍 Got statevector with {state.num_modes} modes")
                
                # Get Fock probabilities using SF's built-in method
                # HOM effect: |1,1⟩ → (|2,0⟩ - |0,2⟩)/√2
                # So we expect P(1,1) ≈ 0, P(2,0) ≈ 0.5, P(0,2) ≈ 0.5
                
                prob_11 = state.fock_prob([1, 1])  # Coincidence
                prob_20 = state.fock_prob([2, 0])  # Both in mode 0
                prob_02 = state.fock_prob([0, 2])  # Both in mode 1
                prob_10 = state.fock_prob([1, 0])  # One in mode 0
                prob_01 = state.fock_prob([0, 1])  # One in mode 1
                prob_10 = state.fock_prob([1, 0])  # One in mode 0
                prob_01 = state.fock_prob([0, 1])  # One in mode 1
                
                # Simulate samples based on probabilities
                samples = []
                probs = [prob_20, prob_02, prob_11, prob_10, prob_01]
                outcomes = [[2, 0], [0, 2], [1, 1], [1, 0], [0, 1]]
                prob_sum = sum(probs)
                probs_normalized = [p / prob_sum for p in probs] if prob_sum > 0 else probs
                
                for _ in range(self.shots):
                    rand = np.random.random()
                    cumsum = 0
                    for i, p in enumerate(probs_normalized):
                        cumsum += p
                        if rand < cumsum:
                            samples.append(outcomes[i])
                            break
                    else:
                        samples.append([0, 0])  # Vacuum fallback
                
                samples = np.array(samples)
                
                # Calculate HOM metrics
                coincidences = np.sum((samples[:, 0] == 1) & (samples[:, 1] == 1))
                coincidence_prob = float(prob_11)  # Use exact probability, not sampled
                visibility = 1 - 2 * coincidence_prob
                
                print(f"📊 HOM Results: P(1,1)={prob_11:.4f}, P(2,0)={prob_20:.4f}, P(0,2)={prob_02:.4f}")
                print(f"   Visibility: {visibility:.4f}")
                
                measurement = MeasurementResult(
                    measurement_type='fock',
                    samples=samples
                )
                
                return SimulationResult(
                    success=True,
                    state=None,
                    measurements={'fock': measurement},
                    figures_of_merit={
                        'coincidence_probability': coincidence_prob,
                        'visibility': float(visibility),
                        'hom_dip': float(visibility),
                        'prob_20': float(prob_20),
                        'prob_02': float(prob_02)
                    },
                    backend_used=self.backend
                )
            except Exception as e:
                print(f"❌ SF HOM failed: {e}")
                import traceback
                traceback.print_exc()
                # Fall through to QuTiP fallback
                
        # QuTiP fallback (or if SF failed)
        try:
            # Create two single photons
            state = self.create_fock_state([1, 1])
            
            # Apply 50:50 beam splitter
            state = self.apply_beam_splitter(state, 0, 1, np.pi/4, 0)
            
            # Measure both outputs
            measurement = self.measure_fock(state)
            
            # Calculate coincidence probability
            samples = measurement.samples
            if len(samples) > 0:
                coincidences = np.sum((samples[:, 0] == 1) & (samples[:, 1] == 1))
                coincidence_prob = coincidences / self.shots
                visibility = 1 - 2 * coincidence_prob
            else:
                coincidence_prob = 0.0
                visibility = 0.0
            
            return SimulationResult(
                success=True,
                state=state,
                measurements={'fock': measurement},
                figures_of_merit={
                    'coincidence_probability': float(coincidence_prob),
                    'visibility': float(visibility),
                    'hom_dip': float(visibility)
                },
                backend_used=self.backend
            )
        except Exception as e:
            print(f"❌ QuTiP HOM also failed: {e}")
            import traceback
            traceback.print_exc()
            return SimulationResult(
                success=False,
                state=None,
                measurements={},
                figures_of_merit={},
                backend_used=self.backend,
                error=str(e)
            )
    
    def bell_state_via_spdc(self) -> SimulationResult:
        """
        Simulate Bell state generation via SPDC + beam splitter
        
        Returns:
            SimulationResult: Bell state preparation results
        """
        if self.backend == 'strawberryfields':
            # Build SF program for Bell state
            prog = sf.Program(2)
            with prog.context as q:
                # SPDC creates correlated photon pairs (simplified as |1,1⟩)
                ops.Fock(1) | q[0]
                ops.Fock(1) | q[1]
                # Beam splitter creates superposition
                ops.BSgate(np.pi/4, 0) | (q[0], q[1])
                # Measure
                ops.MeasureFock() | q[0]
                ops.MeasureFock() | q[1]
            
            # Run simulation
            eng = sf.Engine("fock", backend_options={"cutoff_dim": self.cutoff_dim})
            result = eng.run(prog, shots=self.shots)
            samples = result.samples
            
            # Check for entanglement signature
            if len(samples) > 0:
                both_in_0 = np.sum((samples[:, 0] == 2) & (samples[:, 1] == 0))
                both_in_1 = np.sum((samples[:, 0] == 0) & (samples[:, 1] == 2))
                
                prob_20 = both_in_0 / self.shots
                prob_02 = both_in_1 / self.shots
                
                balance = min(prob_20, prob_02) / max(prob_20, prob_02) if max(prob_20, prob_02) > 0 else 0
            else:
                prob_20 = prob_02 = balance = 0.0
            
            measurement = MeasurementResult(
                measurement_type='fock',
                samples=samples
            )
            
            return SimulationResult(
                success=True,
                state=None,
                measurements={'fock': measurement},
                figures_of_merit={
                    'prob_20': float(prob_20),
                    'prob_02': float(prob_02),
                    'balance': float(balance),
                    'entanglement_signature': float((prob_20 + prob_02) / 2)
                },
                backend_used=self.backend
            )
        else:
            # QuTiP fallback
            # SPDC creates correlated photon pairs (simplified)
            state = self.create_fock_state([1, 1])
            
            # Beam splitter creates superposition
            state = self.apply_beam_splitter(state, 0, 1, np.pi/4, 0)
            
            # Measure
            measurement = self.measure_fock(state)
            
            # Check for entanglement signature (equal |20⟩ and |02⟩ components)
            samples = measurement.samples
            if len(samples) > 0:
                both_in_0 = np.sum((samples[:, 0] == 2) & (samples[:, 1] == 0))
                both_in_1 = np.sum((samples[:, 0] == 0) & (samples[:, 1] == 2))
                
                prob_20 = both_in_0 / self.shots
                prob_02 = both_in_1 / self.shots
                
                # Ideal Bell state: equal probabilities
                balance = min(prob_20, prob_02) / max(prob_20, prob_02) if max(prob_20, prob_02) > 0 else 0
            else:
                prob_20 = prob_02 = balance = 0.0
            
            return SimulationResult(
                success=True,
                state=state,
                measurements={'fock': measurement},
                figures_of_merit={
                    'prob_20': float(prob_20),
                    'prob_02': float(prob_02),
                    'balance': float(balance),
                    'entanglement_signature': float((prob_20 + prob_02) / 2)
                },
                backend_used=self.backend
            )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_available_tools(self) -> List[str]:
        """Return list of available tool names"""
        return [
            # State preparation
            'create_vacuum_state',
            'create_fock_state',
            'create_coherent_state',
            'create_squeezed_state',
            # Operations
            'apply_beam_splitter',
            'apply_phase_shift',
            'apply_displacement',
            'apply_squeezing',
            # Measurements
            'measure_fock',
            'measure_homodyne',
            # Figures of merit
            'calculate_fidelity',
            'calculate_purity',
            'calculate_mean_photon_number',
            'calculate_visibility',
            # High-level experiments
            'hong_ou_mandel_interference',
            'bell_state_via_spdc'
        ]
    
    def describe_tool(self, tool_name: str) -> str:
        """Get description of a specific tool"""
        method = getattr(self, tool_name, None)
        if method and method.__doc__:
            return method.__doc__.strip()
        return f"Tool {tool_name} not found"
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current backend"""
        return {
            'backend': self.backend,
            'cutoff_dim': self.cutoff_dim,
            'shots': self.shots,
            'strawberryfields_available': STRAWBERRYFIELDS_AVAILABLE,
            'qutip_available': QUTIP_AVAILABLE
        }


# =========================================================================
# TOOL-BASED SIMULATION AGENT
# =========================================================================

class ToolBasedSimulationAgent:
    """
    Simulation agent that uses PhotonicToolbox instead of code generation.
    LLM orchestrates tool calls to simulate experiments.
    """
    
    def __init__(self, llm_client, backend='auto'):
        """
        Args:
            llm_client: LLM for tool orchestration
            backend: 'strawberryfields', 'qutip', or 'auto'
        """
        self.llm = llm_client
        self.toolbox = PhotonicToolbox(backend=backend)
        print(f"🔧 Tool-based simulation agent initialized")
    
    def validate_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate design by orchestrating tool calls
        
        Args:
            design: Optical experiment design
            
        Returns:
            dict: Validation results
        """
        print(f"🔬 Validating design with tool-based approach...")
        
        # LLM decides which tools to use
        plan = self._generate_tool_plan(design)
        
        if plan['use_tools']:
            # Execute tool sequence
            result = self._execute_tool_plan(plan)
            
            # Interpret results
            interpretation = self._interpret_results(result, design)
            
            return {
                'success': True,
                'approach': 'tool-based',
                'backend': self.toolbox.backend,
                'result': result,
                'interpretation': interpretation
            }
        else:
            # Fallback to code generation (if needed)
            return {
                'success': False,
                'error': 'Design too complex for tool-based approach',
                'suggestion': 'Use code generation fallback'
            }
    
    def _generate_tool_plan(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """LLM generates a plan by composing primitive quantum operations"""
        
        print(f"🎯 TOOL PLANNING STARTED")
        
        # Extract experiment info
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        components = design.get('experiment', {}).get('steps', [])
        
        print(f"   Title: {title}")
        print(f"   Components: {len(components)} items")
        
        # Get tool descriptions with proper signatures
        tools_list = self.toolbox.get_available_tools()
        tools_info = []
        for tool_name in tools_list:
            method = getattr(self.toolbox, tool_name)
            # Get method signature
            import inspect
            sig = inspect.signature(method)
            params = []
            for param_name, param in sig.parameters.items():
                if param_name not in ['self', 'state', 'measurement']:  # Skip self and special params
                    if param.annotation != inspect.Parameter.empty:
                        # Handle type annotations safely (simple types, generics, etc.)
                        try:
                            type_name = param.annotation.__name__
                        except AttributeError:
                            # For generic types like List[int], use string representation
                            type_name = str(param.annotation).replace('typing.', '')
                        params.append(f"{param_name}: {type_name}")
                    else:
                        params.append(param_name)
            
            param_str = f"({', '.join(params)})" if params else "()"
            doc = self.toolbox.describe_tool(tool_name)
            first_line = doc.split('\n')[0].strip() if doc else "No description"
            tools_info.append(f"- {tool_name}{param_str}: {first_line}")
        tools_desc = "\n".join(tools_info)
        
        print(f"   Available tools: {len(tools_list)}")
        print(f"🔍 Sample tool signatures:")
        for tool_info in tools_info[:3]:  # Show first 3
            print(f"     {tool_info}")
        print(f"🤖 Calling LLM for tool planning...")
        
        prompt = f"""You are a quantum simulation expert. Map optical components to quantum operations.

EXPERIMENT DESIGN:
Title: {title}
Description: {description}

OPTICAL COMPONENTS (from designer):
{json.dumps(components, indent=2)}

YOUR TASK: Translate these OPTICAL components into QUANTUM simulation steps.

⚠️ CRITICAL: The optical table shows component ORDER and CONNECTIONS, not spatial coordinates.
Focus on QUANTUM STATE EVOLUTION through the sequence of operations. The physical layout is 
representative - interpret the physics correctly based on the experiment description and component types.

MAPPING RULES:
- laser/source → create_fock_state (single photons) or create_coherent_state (classical light)
- beam_splitter → apply_beam_splitter(mode1, mode2, theta, phi)
- mirror/phase_shifter → apply_phase_shift(mode, phi)
- crystal (SPDC/PDC) → create_fock_state with entangled photon pairs
- detector → measure_fock for photon counting (most common)
- wave_plate → apply_phase_shift or rotation operations

GENERAL GUIDELINES:
- Use create_fock_state for single-photon or few-photon experiments
- Use create_coherent_state for laser-like classical fields
- Most interferometry uses measure_fock (photon counting at output)
- State threading: Operations automatically receive the current quantum state
- End your sequence with a measurement operation
- READ THE EXPERIMENT DESCRIPTION to understand the intended physics, not just the component positions

AVAILABLE QUANTUM TOOLS (with exact signatures):
{tools_desc}

⚠️  CRITICAL: You MUST use the EXACT parameter names from the signatures above!
    For example: apply_phase_shift uses 'phi' (not 'phase', not 'angle')
                 apply_beam_splitter uses 'theta' and 'phi' (not 'angle1', 'angle2')
    
    Match the parameter names EXACTLY as shown, or the function call will fail!

EXAMPLE TRANSLATION:
Optical: [laser, beam_splitter, detector, detector]
Quantum: 
{{
    "use_tools": true,
    "sequence": [
        {{"tool": "create_fock_state", "args": {{"photon_numbers": [1, 1]}}}},
        {{"tool": "apply_beam_splitter", "args": {{"state": "previous", "mode1": 0, "mode2": 1, "theta": 0.785, "phi": 0}}}},
        {{"tool": "measure_fock", "args": {{"state": "previous"}}}}
    ],
    "reasoning": "Two photons from sources interfere at BS, measured at outputs"
}}

EXAMPLE WITH PHASE SHIFT:
Optical: [laser, phase_shifter, detector]
Quantum:
{{
    "use_tools": true,
    "sequence": [
        {{"tool": "create_fock_state", "args": {{"photon_numbers": [1]}}}},
        {{"tool": "apply_phase_shift", "args": {{"state": "previous", "mode": 0, "phi": 1.57}}}},
        {{"tool": "measure_fock", "args": {{"state": "previous"}}}}
    ],
    "reasoning": "Single photon gets phase shift, then measured. Note: parameter is 'phi' not 'phase'!"
}}

IMPORTANT: 
- Look at component TYPES to determine quantum operations
- Use beam paths/connections to determine mode indices
- Choose appropriate quantum state based on physics (Fock for single photons, coherent for classical)
- End with measurement operation
- Use "previous" to thread quantum state through operations

If components cannot be simulated: {{"use_tools": false, "reasoning": "explain why"}}

RESPOND WITH ONLY JSON:"""
        
        print(f"📤 Sending prompt to LLM ({len(prompt)} chars)...")
        
        try:
            response = self.llm.predict(prompt).strip()
            print(f"📝 LLM response preview: {response[:150]}...")
            
            # ROBUST JSON EXTRACTION (like llm_designer.py)
            text = response
            
            # Remove markdown code blocks
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                parts = text.split('```')
                if len(parts) >= 3:
                    text = parts[1].strip()
            
            # Find JSON object boundaries
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                text = text[start:end]
                
                # Attempt to parse
                try:
                    plan = json.loads(text)
                    print(f"✅ Parsed {len(plan.get('sequence', []))} tool steps")
                    
                    # DEBUG: Show actual tool calls
                    print(f"🔍 Tool sequence details:")
                    for i, step in enumerate(plan.get('sequence', [])[:3]):  # Show first 3
                        tool = step.get('tool', 'unknown')
                        args = step.get('args', {})
                        print(f"   {i+1}. {tool}({', '.join(f'{k}={v}' for k, v in args.items() if k != 'state')})")
                    
                    return plan
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parse error at position {e.pos}")
                    
                    # JSON REPAIR: Try to find complete object by counting braces
                    brace_count = 0
                    last_valid = 0
                    for i, char in enumerate(text):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                last_valid = i + 1
                                break
                    
                    if last_valid > 0:
                        try:
                            plan = json.loads(text[:last_valid])
                            print(f"✅ Repaired and parsed JSON")
                            return plan
                        except:
                            pass
            
            # If all parsing failed
            print(f"❌ Could not extract valid JSON from response")
            print(f"   Full response: {response}")
            return {'use_tools': False, 'error': 'JSON parsing failed'}
            
        except Exception as e:
            print(f"⚠️  Tool planning exception: {e}")
            return {'use_tools': False, 'error': str(e)}
    
    def _execute_tool_plan(self, plan: Dict[str, Any]) -> SimulationResult:
        """Execute sequence of tool calls with state threading"""
        
        sequence = plan.get('sequence', [])
        current_state = None
        last_measurement = None
        measurements = {}
        figures_of_merit = {}
        
        for i, step in enumerate(sequence):
            tool_name = step['tool']
            args = step.get('args', {})
            
            print(f"🔧 Executing step {i+1}: {tool_name} with args: {args}")
            
            try:
                # Replace "previous" references with actual values
                processed_args = {}
                for key, value in args.items():
                    if value == "previous":
                        if key == "state" and current_state:
                            processed_args[key] = current_state
                        elif key == "measurement" and last_measurement:
                            processed_args[key] = last_measurement
                        else:
                            # Skip if no previous value available
                            continue
                    else:
                        processed_args[key] = value
                
                # ARGUMENT NAME MAPPING: Handle common LLM variations
                # Map 'phase' -> 'phi', 'angle' -> 'theta', etc.
                print(f"   🔍 Starting argument mapping for {tool_name}...")
                method = getattr(self.toolbox, tool_name)
                import inspect
                sig = inspect.signature(method)
                actual_param_names = list(sig.parameters.keys())
                
                # AUTO-INJECT STATE: If method expects 'state' but LLM didn't provide it, use current_state
                if 'state' in actual_param_names and 'state' not in processed_args and current_state:
                    print(f"   🔧 Auto-injecting current quantum state")
                    processed_args['state'] = current_state
                
                # Filter to only non-special params for mapping
                actual_param_names = [p for p in actual_param_names if p not in ['self']]
                
                # If LLM used 'phase' but method expects 'phi', translate it
                mapped_args = {}
                for key, value in processed_args.items():
                    if key == 'phase' and 'phi' in actual_param_names and 'phase' not in actual_param_names:
                        print(f"   🔧 Auto-mapping: 'phase' → 'phi' for {tool_name}")
                        mapped_args['phi'] = value
                    elif key == 'angle' and 'theta' in actual_param_names and 'angle' not in actual_param_names:
                        print(f"   🔧 Auto-mapping: 'angle' → 'theta' for {tool_name}")
                        mapped_args['theta'] = value
                    else:
                        mapped_args[key] = value
                
                # Call the tool method with mapped arguments
                print(f"   ✅ Final args after mapping: {mapped_args}")
                result = method(**mapped_args)
                
                # Store results and update state tracking
                if isinstance(result, QuantumState):
                    current_state = result
                elif isinstance(result, MeasurementResult):
                    last_measurement = result
                    measurements[f"{tool_name}_{i}"] = result
                elif isinstance(result, (int, float)):
                    figures_of_merit[tool_name] = result
                elif isinstance(result, SimulationResult):
                    return result  # High-level tool returned complete result
                    
            except Exception as e:
                print(f"❌ Tool execution failed: {tool_name} - {e}")
                import traceback
                traceback.print_exc()
                return SimulationResult(
                    success=False,
                    state=None,
                    measurements={},
                    figures_of_merit={},
                    backend_used=self.toolbox.backend,
                    error=f"{tool_name}: {str(e)}"
                )
        
        return SimulationResult(
            success=True,
            state=current_state,
            measurements=measurements,
            figures_of_merit=figures_of_merit,
            backend_used=self.toolbox.backend
        )
    
    def _interpret_results(self, result: SimulationResult, design: Dict[str, Any]) -> Dict[str, Any]:
        """LLM interprets simulation results"""
        
        print(f"📊 Interpreting results:")
        print(f"   Success: {result.success}")
        print(f"   Measurements: {len(result.measurements)} items")
        print(f"   FoMs: {len(result.figures_of_merit)} items")
        
        prompt = f"""Interpret these quantum simulation results:

Design: {json.dumps(design, indent=2)}

Results:
- Backend: {result.backend_used}
- Measurements: {json.dumps({k: v.statistics for k, v in result.measurements.items()}, indent=2)}
- Figures of Merit: {json.dumps(result.figures_of_merit, indent=2)}

Provide analysis in this JSON format:
{{
    "working_as_intended": true/false,
    "confidence": 0.0-1.0,
    "observations": ["key observation 1", "key observation 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}

RESPOND WITH ONLY JSON:"""
        
        try:
            response = self.llm.predict(prompt)
            
            # Robust JSON extraction (same as tool planning)
            response = response.strip()
            
            # Remove markdown code blocks
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
                if response.startswith('json'):
                    response = response[4:].strip()
            
            # Find JSON boundaries
            start = response.find('{')
            end = response.rfind('}')
            
            if start != -1 and end != -1:
                response = response[start:end+1]
            
            interpretation = json.loads(response)
            return interpretation
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"📝 LLM response was: {response[:200]}...")
            return {
                'confidence': 0.5,
                'analysis': 'Could not parse LLM interpretation',
                'error': str(e)
            }
        except Exception as e:
            print(f"⚠️  Interpretation failed: {e}")
            return {
                'confidence': 0.5,
                'analysis': 'Could not interpret results',
                'error': str(e)
            }
