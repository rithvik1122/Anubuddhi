"""
Quantum measurements for quantum experiment design.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod
from enum import Enum
import qutip as qt

from .states import QuantumState


class MeasurementType(Enum):
    """Enumeration of measurement types."""
    PHOTON_NUMBER = "photon_number"
    HOMODYNE = "homodyne"
    HETERODYNE = "heterodyne"
    BUCKET = "bucket"
    POVM = "povm"


class MeasurementResult:
    """Container for measurement results."""
    
    def __init__(self, outcome: Any, probability: float, post_measurement_state: Optional[QuantumState] = None):
        """
        Initialize measurement result.
        
        Args:
            outcome: Measurement outcome value
            probability: Probability of this outcome
            post_measurement_state: State after measurement (if applicable)
        """
        self.outcome = outcome
        self.probability = probability
        self.post_measurement_state = post_measurement_state
        self.metadata: Dict[str, Any] = {}


class Measurement(ABC):
    """
    Abstract base class for quantum measurements.
    
    Measurements extract classical information from quantum states
    and potentially change the state (projective measurements).
    """
    
    def __init__(self, measurement_type: MeasurementType, target_modes: List[int], 
                 parameters: Dict[str, Any], description: str = ""):
        """
        Initialize a quantum measurement.
        
        Args:
            measurement_type: Type of measurement
            target_modes: Modes being measured
            parameters: Measurement parameters
            description: Human-readable description
        """
        self.measurement_type = measurement_type
        self.target_modes = target_modes
        self.parameters = parameters
        self.description = description
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def measure(self, state: QuantumState) -> List[MeasurementResult]:
        """
        Perform the measurement on a quantum state.
        
        Args:
            state: Input quantum state
        
        Returns:
            List of possible measurement results with probabilities
        """
        pass
    
    @abstractmethod
    def get_operators(self, dimensions: List[int]) -> List[qt.Qobj]:
        """
        Get the measurement operators (POVM elements).
        
        Args:
            dimensions: Dimensions of each mode
        
        Returns:
            List of measurement operators
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary representation."""
        return {
            "type": self.measurement_type.value,
            "target_modes": self.target_modes,
            "parameters": self.parameters,
            "description": self.description,
            "metadata": self.metadata
        }


class PhotonNumberMeasurement(Measurement):
    """Photon number measurement (Fock state projection)."""
    
    def __init__(self, mode: int, max_photons: Optional[int] = None):
        """
        Initialize photon number measurement.
        
        Args:
            mode: Mode to measure
            max_photons: Maximum photon number to consider (None for all)
        """
        self.mode = mode
        self.max_photons = max_photons
        
        parameters = {"max_photons": max_photons}
        
        super().__init__(
            MeasurementType.PHOTON_NUMBER,
            [mode],
            parameters,
            f"Photon number measurement mode {mode}"
        )
    
    def get_operators(self, dimensions: List[int]) -> List[qt.Qobj]:
        """Get photon number measurement operators."""
        dim = dimensions[self.mode]
        max_n = self.max_photons if self.max_photons is not None else dim
        max_n = min(max_n, dim)
        
        operators = []
        
        # Create projection operators |n⟩⟨n| for each photon number
        for n in range(max_n):
            proj = qt.basis(dim, n) * qt.basis(dim, n).dag()
            
            # If multi-mode system, tensor with identity on other modes
            if len(dimensions) > 1:
                full_operators = []
                for i, d in enumerate(dimensions):
                    if i == self.mode:
                        full_operators.append(proj)
                    else:
                        full_operators.append(qt.qeye(d))
                proj = qt.tensor(*full_operators)
            
            operators.append(proj)
        
        # Add projector for all higher photon numbers (if truncated)
        if max_n < dim:
            higher_proj = sum(qt.basis(dim, n) * qt.basis(dim, n).dag() 
                            for n in range(max_n, dim))
            
            if len(dimensions) > 1:
                full_operators = []
                for i, d in enumerate(dimensions):
                    if i == self.mode:
                        full_operators.append(higher_proj)
                    else:
                        full_operators.append(qt.qeye(d))
                higher_proj = qt.tensor(*full_operators)
            
            operators.append(higher_proj)
        
        return operators
    
    def measure(self, state: QuantumState) -> List[MeasurementResult]:
        """Perform photon number measurement."""
        rho = state.to_density_matrix()
        operators = self.get_operators(state.dimensions)
        
        results = []
        
        for n, proj in enumerate(operators):
            # Calculate probability
            prob = qt.expect(proj, rho).real
            
            if prob > 1e-10:  # Only include non-zero probabilities
                # Post-measurement state
                if prob > 0:
                    post_state_rho = (proj * rho * proj) / prob
                    
                    # Create post-measurement state
                    class PostMeasurementState(QuantumState):
                        def __init__(self, rho_post, original_state, outcome):
                            super().__init__(
                                original_state.state_type,
                                original_state.dimensions,
                                f"Post-measurement n={outcome} {original_state.description}"
                            )
                            self._density_matrix = rho_post
                        
                        def to_qobj(self):
                            return self._density_matrix
                        
                        def to_density_matrix(self):
                            return self._density_matrix
                    
                    post_state = PostMeasurementState(post_state_rho, state, n)
                else:
                    post_state = None
                
                # Outcome value
                outcome = n if n < len(operators) - 1 else f">={len(operators)-1}"
                
                results.append(MeasurementResult(outcome, prob, post_state))
        
        return results


class HomodyneMeasurement(Measurement):
    """Homodyne measurement (quadrature measurement)."""
    
    def __init__(self, mode: int, phase: float = 0, bins: int = 50, x_range: Tuple[float, float] = (-10, 10)):
        """
        Initialize homodyne measurement.
        
        Args:
            mode: Mode to measure
            phase: Local oscillator phase (0 for x quadrature, π/2 for p quadrature)
            bins: Number of bins for discretization
            x_range: Range of quadrature values
        """
        self.mode = mode
        self.phase = phase
        self.bins = bins
        self.x_range = x_range
        
        parameters = {
            "phase": phase,
            "bins": bins,
            "x_range": x_range
        }
        
        super().__init__(
            MeasurementType.HOMODYNE,
            [mode],
            parameters,
            f"Homodyne measurement mode {mode} phase={phase:.3f}"
        )
    
    def get_operators(self, dimensions: List[int]) -> List[qt.Qobj]:
        """Get homodyne measurement operators (quadrature eigenstates)."""
        dim = dimensions[self.mode]
        x_min, x_max = self.x_range
        x_values = np.linspace(x_min, x_max, self.bins)
        dx = x_values[1] - x_values[0]
        
        operators = []
        
        for x in x_values:
            # Create quadrature eigenstate |x⟩ for given phase
            # This is an approximation using coherent state basis
            x_state = qt.coherent(dim, x * np.exp(1j * self.phase))
            proj = x_state * x_state.dag() * dx  # Include measure
            
            # If multi-mode system, tensor with identity on other modes
            if len(dimensions) > 1:
                full_operators = []
                for i, d in enumerate(dimensions):
                    if i == self.mode:
                        full_operators.append(proj)
                    else:
                        full_operators.append(qt.qeye(d))
                proj = qt.tensor(*full_operators)
            
            operators.append(proj)
        
        return operators
    
    def measure(self, state: QuantumState) -> List[MeasurementResult]:
        """Perform homodyne measurement."""
        rho = state.to_density_matrix()
        operators = self.get_operators(state.dimensions)
        x_min, x_max = self.x_range
        x_values = np.linspace(x_min, x_max, self.bins)
        
        results = []
        
        for i, (x, proj) in enumerate(zip(x_values, operators)):
            # Calculate probability
            prob = qt.expect(proj, rho).real
            
            if prob > 1e-10:
                results.append(MeasurementResult(x, prob))
        
        return results


class BucketMeasurement(Measurement):
    """Bucket detector (click/no-click measurement)."""
    
    def __init__(self, mode: int, efficiency: float = 1.0):
        """
        Initialize bucket measurement.
        
        Args:
            mode: Mode to measure
            efficiency: Detection efficiency (0 to 1)
        """
        self.mode = mode
        self.efficiency = efficiency
        
        parameters = {"efficiency": efficiency}
        
        super().__init__(
            MeasurementType.BUCKET,
            [mode],
            parameters,
            f"Bucket measurement mode {mode} η={efficiency:.3f}"
        )
    
    def get_operators(self, dimensions: List[int]) -> List[qt.Qobj]:
        """Get bucket measurement operators."""
        dim = dimensions[self.mode]
        
        # No-click operator (vacuum projection)
        no_click = qt.basis(dim, 0) * qt.basis(dim, 0).dag()
        
        # Click operator (anything else)
        click = qt.qeye(dim) - no_click
        
        # Include detection efficiency
        if self.efficiency < 1.0:
            # Inefficient detector: some photons might not be detected
            click = self.efficiency * click + (1 - self.efficiency) * no_click
        
        # If multi-mode system, tensor with identity on other modes
        if len(dimensions) > 1:
            no_click_full = []
            click_full = []
            
            for i, d in enumerate(dimensions):
                if i == self.mode:
                    no_click_full.append(no_click)
                    click_full.append(click)
                else:
                    no_click_full.append(qt.qeye(d))
                    click_full.append(qt.qeye(d))
            
            no_click = qt.tensor(*no_click_full)
            click = qt.tensor(*click_full)
        
        return [no_click, click]
    
    def measure(self, state: QuantumState) -> List[MeasurementResult]:
        """Perform bucket measurement."""
        rho = state.to_density_matrix()
        no_click_op, click_op = self.get_operators(state.dimensions)
        
        # Calculate probabilities
        p_no_click = qt.expect(no_click_op, rho).real
        p_click = qt.expect(click_op, rho).real
        
        results = []
        
        if p_no_click > 1e-10:
            results.append(MeasurementResult("no_click", p_no_click))
        
        if p_click > 1e-10:
            results.append(MeasurementResult("click", p_click))
        
        return results


class POVMMeasurement(Measurement):
    """General POVM measurement."""
    
    def __init__(self, mode: int, povm_elements: List[qt.Qobj], outcomes: List[Any]):
        """
        Initialize POVM measurement.
        
        Args:
            mode: Mode to measure
            povm_elements: List of POVM operators
            outcomes: Corresponding measurement outcomes
        """
        if len(povm_elements) != len(outcomes):
            raise ValueError("Number of POVM elements must match number of outcomes")
        
        self.mode = mode
        self.povm_elements = povm_elements
        self.outcomes = outcomes
        
        parameters = {
            "num_elements": len(povm_elements),
            "outcomes": outcomes
        }
        
        super().__init__(
            MeasurementType.POVM,
            [mode],
            parameters,
            f"POVM measurement mode {mode} ({len(povm_elements)} elements)"
        )
    
    def get_operators(self, dimensions: List[int]) -> List[qt.Qobj]:
        """Get POVM operators."""
        # If multi-mode system, tensor with identity on other modes
        if len(dimensions) > 1:
            full_operators = []
            
            for povm_op in self.povm_elements:
                ops = []
                for i, d in enumerate(dimensions):
                    if i == self.mode:
                        ops.append(povm_op)
                    else:
                        ops.append(qt.qeye(d))
                full_operators.append(qt.tensor(*ops))
            
            return full_operators
        else:
            return self.povm_elements
    
    def measure(self, state: QuantumState) -> List[MeasurementResult]:
        """Perform POVM measurement."""
        rho = state.to_density_matrix()
        operators = self.get_operators(state.dimensions)
        
        results = []
        
        for outcome, povm_op in zip(self.outcomes, operators):
            # Calculate probability
            prob = qt.expect(povm_op, rho).real
            
            if prob > 1e-10:
                results.append(MeasurementResult(outcome, prob))
        
        return results
