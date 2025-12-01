"""
Quantum state representations and manipulations.
"""

import numpy as np
from typing import Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod
from enum import Enum
import qutip as qt


class StateType(Enum):
    """Enumeration of quantum state types."""
    FOCK = "fock"
    COHERENT = "coherent"
    SQUEEZED = "squeezed"
    THERMAL = "thermal"
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"


class QuantumState(ABC):
    """
    Abstract base class for quantum states in the AgenticQuantum system.
    
    This class provides a unified interface for different types of quantum states
    used in quantum optics experiments.
    """
    
    def __init__(self, state_type: StateType, dimensions: List[int], description: str = ""):
        """
        Initialize a quantum state.
        
        Args:
            state_type: Type of the quantum state
            dimensions: Dimensions of each mode
            description: Human-readable description
        """
        self.state_type = state_type
        self.dimensions = dimensions
        self.num_modes = len(dimensions)
        self.description = description
        self._qobj: Optional[qt.Qobj] = None
        self._density_matrix: Optional[qt.Qobj] = None
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def to_qobj(self) -> qt.Qobj:
        """Convert to QuTiP quantum object."""
        pass
    
    def to_qutip(self) -> qt.Qobj:
        """Alias for to_qobj() for compatibility."""
        return self.to_qobj()
    
    @abstractmethod
    def to_density_matrix(self) -> qt.Qobj:
        """Convert to density matrix representation."""
        pass
    
    def get_photon_number_distribution(self, mode: int = 0) -> np.ndarray:
        """
        Get photon number distribution for a specific mode.
        
        Args:
            mode: Mode index
        
        Returns:
            Array of photon number probabilities
        """
        if self._density_matrix is None:
            self._density_matrix = self.to_density_matrix()
        
        # Calculate photon number probabilities
        dim = self.dimensions[mode]
        probabilities = np.zeros(dim)
        
        for n in range(dim):
            fock_state = qt.basis(dim, n)
            prob = qt.expect(fock_state * fock_state.dag(), self._density_matrix)
            probabilities[n] = prob.real
        
        return probabilities
    
    def get_expectation_value(self, operator: qt.Qobj) -> float:
        """
        Calculate expectation value of an operator.
        
        Args:
            operator: Quantum operator
        
        Returns:
            Expectation value
        """
        if self._density_matrix is None:
            self._density_matrix = self.to_density_matrix()
        
        return qt.expect(operator, self._density_matrix).real
    
    def get_mean_photon_number(self, mode: int = 0) -> float:
        """
        Get mean photon number for a specific mode.
        
        Args:
            mode: Mode index
        
        Returns:
            Mean photon number
        """
        dim = self.dimensions[mode]
        num_op = qt.num(dim)
        
        if self.num_modes > 1:
            # Create tensor product with identity on other modes
            operators = []
            for i in range(self.num_modes):
                if i == mode:
                    operators.append(num_op)
                else:
                    operators.append(qt.qeye(self.dimensions[i]))
            num_op = qt.tensor(*operators)
        
        return self.get_expectation_value(num_op)
    
    def calculate_fidelity(self, other: "QuantumState") -> float:
        """
        Calculate fidelity with another quantum state.
        
        Args:
            other: Another quantum state
        
        Returns:
            Fidelity value between 0 and 1
        """
        rho1 = self.to_density_matrix()
        rho2 = other.to_density_matrix()
        return qt.fidelity(rho1, rho2)
    
    def is_pure(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the state is pure.
        
        Args:
            tolerance: Numerical tolerance
        
        Returns:
            True if state is pure
        """
        rho = self.to_density_matrix()
        purity = qt.expect(rho * rho, rho).real
        return abs(purity - 1.0) < tolerance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary representation."""
        return {
            "type": self.state_type.value,
            "dimensions": self.dimensions,
            "num_modes": self.num_modes,
            "description": self.description,
            "metadata": self.metadata,
            "mean_photon_numbers": [self.get_mean_photon_number(i) for i in range(self.num_modes)],
            "is_pure": self.is_pure()
        }


class FockState(QuantumState):
    """Fock (number) state |n⟩."""
    
    def __init__(self, photon_numbers: Union[int, List[int]], max_dim: int = 50):
        """
        Initialize a Fock state.
        
        Args:
            photon_numbers: Photon number(s) for each mode
            max_dim: Maximum dimension for truncation
        """
        if isinstance(photon_numbers, int):
            photon_numbers = [photon_numbers]
        
        self.photon_numbers = photon_numbers
        self.max_dim = max_dim
        
        dimensions = [max_dim] * len(photon_numbers)
        super().__init__(StateType.FOCK, dimensions, f"Fock state |{','.join(map(str, photon_numbers))}⟩")
        
        self.metadata.update({
            "photon_numbers": photon_numbers,
            "max_dim": max_dim
        })
    
    def to_qobj(self) -> qt.Qobj:
        """Convert to QuTiP quantum object."""
        if self._qobj is None:
            if len(self.photon_numbers) == 1:
                self._qobj = qt.basis(self.max_dim, self.photon_numbers[0])
            else:
                basis_states = [qt.basis(self.max_dim, n) for n in self.photon_numbers]
                self._qobj = qt.tensor(*basis_states)
        return self._qobj
    
    def to_density_matrix(self) -> qt.Qobj:
        """Convert to density matrix representation."""
        if self._density_matrix is None:
            psi = self.to_qobj()
            self._density_matrix = psi * psi.dag()
        return self._density_matrix


class CoherentState(QuantumState):
    """Coherent state |α⟩."""
    
    def __init__(self, alpha: Union[complex, List[complex]], max_dim: int = 50):
        """
        Initialize a coherent state.
        
        Args:
            alpha: Complex amplitude(s) for each mode
            max_dim: Maximum dimension for truncation
        """
        if isinstance(alpha, (int, float, complex)):
            alpha = [alpha]
        
        self.alpha = alpha
        self.max_dim = max_dim
        
        dimensions = [max_dim] * len(alpha)
        alpha_str = ','.join([f"{a:.2f}" for a in alpha])
        super().__init__(StateType.COHERENT, dimensions, f"Coherent state |{alpha_str}⟩")
        
        self.metadata.update({
            "alpha": alpha,
            "max_dim": max_dim
        })
    
    def to_qobj(self) -> qt.Qobj:
        """Convert to QuTiP quantum object."""
        if self._qobj is None:
            if len(self.alpha) == 1:
                self._qobj = qt.coherent(self.max_dim, self.alpha[0])
            else:
                coherent_states = [qt.coherent(self.max_dim, a) for a in self.alpha]
                self._qobj = qt.tensor(*coherent_states)
        return self._qobj
    
    def to_density_matrix(self) -> qt.Qobj:
        """Convert to density matrix representation."""
        if self._density_matrix is None:
            psi = self.to_qobj()
            self._density_matrix = psi * psi.dag()
        return self._density_matrix


class SqueezedState(QuantumState):
    """Squeezed vacuum state."""
    
    def __init__(self, r: Union[float, List[float]], phi: Union[float, List[float]] = 0, max_dim: int = 50):
        """
        Initialize a squeezed state.
        
        Args:
            r: Squeezing parameter(s)
            phi: Squeezing phase(s)
            max_dim: Maximum dimension for truncation
        """
        if isinstance(r, (int, float)):
            r = [r]
        if isinstance(phi, (int, float)):
            phi = [phi]
        
        self.r = r
        self.phi = phi
        self.max_dim = max_dim
        
        dimensions = [max_dim] * len(r)
        super().__init__(StateType.SQUEEZED, dimensions, f"Squeezed state (r={r[0]:.2f})")
        
        self.metadata.update({
            "r": r,
            "phi": phi,
            "max_dim": max_dim
        })
    
    def to_qobj(self) -> qt.Qobj:
        """Convert to QuTiP quantum object."""
        if self._qobj is None:
            if len(self.r) == 1:
                # Single-mode squeezed state
                self._qobj = qt.squeeze(self.max_dim, self.r[0] * np.exp(1j * self.phi[0])) * qt.basis(self.max_dim, 0)
            else:
                # Multi-mode squeezed states
                squeezed_states = []
                for i in range(len(self.r)):
                    sq_state = qt.squeeze(self.max_dim, self.r[i] * np.exp(1j * self.phi[i])) * qt.basis(self.max_dim, 0)
                    squeezed_states.append(sq_state)
                self._qobj = qt.tensor(*squeezed_states)
        return self._qobj
    
    def to_density_matrix(self) -> qt.Qobj:
        """Convert to density matrix representation."""
        if self._density_matrix is None:
            psi = self.to_qobj()
            self._density_matrix = psi * psi.dag()
        return self._density_matrix


class SuperpositionState(QuantumState):
    """Superposition of quantum states."""
    
    def __init__(self, states: List[QuantumState], coefficients: List[complex], description: str = ""):
        """
        Initialize a superposition state.
        
        Args:
            states: List of quantum states
            coefficients: Complex coefficients for each state
            description: Description of the superposition
        """
        if len(states) != len(coefficients):
            raise ValueError("Number of states must match number of coefficients")
        
        self.states = states
        self.coefficients = coefficients
        
        # Use dimensions from the first state (assuming all have same dimensions)
        dimensions = states[0].dimensions
        
        if not description:
            description = f"Superposition of {len(states)} states"
        
        super().__init__(StateType.SUPERPOSITION, dimensions, description)
        
        self.metadata.update({
            "num_components": len(states),
            "coefficients": coefficients
        })
    
    def to_qobj(self) -> qt.Qobj:
        """Convert to QuTiP quantum object."""
        if self._qobj is None:
            # Normalize coefficients
            norm = np.sqrt(sum(abs(c)**2 for c in self.coefficients))
            normalized_coeffs = [c / norm for c in self.coefficients]
            
            # Create superposition
            self._qobj = sum(c * state.to_qobj() for c, state in zip(normalized_coeffs, self.states))
        return self._qobj
    
    def to_density_matrix(self) -> qt.Qobj:
        """Convert to density matrix representation."""
        if self._density_matrix is None:
            psi = self.to_qobj()
            self._density_matrix = psi * psi.dag()
        return self._density_matrix


def create_cat_state(alpha: complex, max_dim: int = 50) -> SuperpositionState:
    """
    Create a Schrödinger cat state |α⟩ + |-α⟩.
    
    Args:
        alpha: Coherent state amplitude
        max_dim: Maximum dimension for truncation
    
    Returns:
        Cat state as a superposition
    """
    state_plus = CoherentState(alpha, max_dim)
    state_minus = CoherentState(-alpha, max_dim)
    
    return SuperpositionState(
        states=[state_plus, state_minus],
        coefficients=[1, 1],
        description=f"Cat state |{alpha:.2f}⟩ + |{-alpha:.2f}⟩"
    )
