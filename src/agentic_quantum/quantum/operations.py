"""
Quantum operations for quantum experiment design.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
import qutip as qt

from .states import QuantumState


class OperationType(Enum):
    """Enumeration of quantum operation types."""
    BEAM_SPLITTER = "beam_splitter"
    PHASE_SHIFT = "phase_shift"
    DISPLACEMENT = "displacement"
    SQUEEZING = "squeezing"
    ROTATION = "rotation"
    LOSS = "loss"
    AMPLIFICATION = "amplification"


class QuantumOperation(ABC):
    """
    Abstract base class for quantum operations.
    
    Quantum operations represent unitary and non-unitary transformations
    that can be applied to quantum states in experiments.
    """
    
    def __init__(self, operation_type: OperationType, target_modes: List[int], 
                 parameters: Dict[str, Any], description: str = ""):
        """
        Initialize a quantum operation.
        
        Args:
            operation_type: Type of the operation
            target_modes: Modes that the operation acts on
            parameters: Operation parameters
            description: Human-readable description
        """
        self.operation_type = operation_type
        self.target_modes = target_modes
        self.parameters = parameters
        self.description = description
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """
        Get the quantum operator for this operation.
        
        Args:
            dimensions: Dimensions of each mode in the system
        
        Returns:
            QuTiP quantum operator
        """
        pass
    
    def to_qutip(self, dimensions: List[int] = None) -> qt.Qobj:
        """Alias for get_operator() for compatibility."""
        if dimensions is None:
            raise ValueError("dimensions required for to_qutip()")
        return self.get_operator(dimensions)
    
    @abstractmethod
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """
        Apply the operation to a quantum state.
        
        Args:
            state: Input quantum state
        
        Returns:
            Transformed quantum state
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary representation."""
        return {
            "type": self.operation_type.value,
            "target_modes": self.target_modes,
            "parameters": self.parameters,
            "description": self.description,
            "metadata": self.metadata
        }


class BeamSplitter(QuantumOperation):
    """
    Beam splitter operation between two modes.
    
    Implements the transformation:
    a_out1 = t*a_in1 + r*a_in2
    a_out2 = -r*a_in1 + t*a_in2
    """
    
    def __init__(self, mode1: int, mode2: int, transmittance: float, phase: float = 0):
        """
        Initialize a beam splitter.
        
        Args:
            mode1: First mode index
            mode2: Second mode index
            transmittance: Transmittance coefficient (0 to 1)
            phase: Phase difference
        """
        if not 0 <= transmittance <= 1:
            raise ValueError("Transmittance must be between 0 and 1")
        
        self.transmittance = transmittance
        self.reflectance = np.sqrt(1 - transmittance**2)
        self.phase = phase
        
        parameters = {
            "transmittance": transmittance,
            "reflectance": self.reflectance,
            "phase": phase
        }
        
        super().__init__(
            OperationType.BEAM_SPLITTER,
            [mode1, mode2],
            parameters,
            f"Beam splitter ({mode1},{mode2}) T={transmittance:.3f}"
        )
    
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """Get the beam splitter operator."""
        mode1, mode2 = self.target_modes
        dim1, dim2 = dimensions[mode1], dimensions[mode2]
        
        # Create beam splitter operator for two modes
        a1 = qt.destroy(dim1)
        a2 = qt.destroy(dim2)
        
        t = np.sqrt(self.transmittance)
        r = np.sqrt(self.reflectance) * np.exp(1j * self.phase)
        
        # Beam splitter Hamiltonian (interaction picture)
        H_bs = 1j * (r * qt.tensor(a1.dag(), a2) - np.conj(r) * qt.tensor(a1, a2.dag()))
        
        # For small angle approximation or exact evolution
        # For now, use displacement operator approximation
        bs_op = (-1j * H_bs).expm()
        
        return bs_op
    
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """Apply beam splitter to quantum state."""
        from .states import QuantumState
        
        # Get the operator and apply it
        op = self.get_operator(state.dimensions)
        input_qobj = state.to_qobj()
        output_qobj = op * input_qobj
        
        # Create new state with transformed quantum object
        # This is a simplified implementation - in practice, we'd need
        # to create a new state class that wraps the transformed qobj
        class TransformedState(QuantumState):
            def __init__(self, qobj, original_state):
                super().__init__(
                    original_state.state_type,
                    original_state.dimensions,
                    f"BS-transformed {original_state.description}"
                )
                self._qobj = qobj
            
            def to_qobj(self):
                return self._qobj
            
            def to_density_matrix(self):
                if self._density_matrix is None:
                    self._density_matrix = self._qobj * self._qobj.dag()
                return self._density_matrix
        
        return TransformedState(output_qobj, state)


class PhaseShift(QuantumOperation):
    """Phase shift operation exp(i*φ*n) on a single mode."""
    
    def __init__(self, mode: int, phase: float):
        """
        Initialize a phase shift operation.
        
        Args:
            mode: Mode index
            phase: Phase shift angle
        """
        self.phase = phase
        
        parameters = {"phase": phase}
        
        super().__init__(
            OperationType.PHASE_SHIFT,
            [mode],
            parameters,
            f"Phase shift mode {mode} φ={phase:.3f}"
        )
    
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """Get the phase shift operator."""
        mode = self.target_modes[0]
        dim = dimensions[mode]
        
        # Phase shift operator exp(i*φ*n)
        n_op = qt.num(dim)
        phase_op = (1j * self.phase * n_op).expm()
        
        # If multi-mode system, tensor with identity on other modes
        if len(dimensions) > 1:
            operators = []
            for i, d in enumerate(dimensions):
                if i == mode:
                    operators.append(phase_op)
                else:
                    operators.append(qt.qeye(d))
            phase_op = qt.tensor(*operators)
        
        return phase_op
    
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """Apply phase shift to quantum state."""
        op = self.get_operator(state.dimensions)
        input_qobj = state.to_qobj()
        output_qobj = op * input_qobj
        
        # Create transformed state (simplified implementation)
        class TransformedState(QuantumState):
            def __init__(self, qobj, original_state):
                super().__init__(
                    original_state.state_type,
                    original_state.dimensions,
                    f"Phase-shifted {original_state.description}"
                )
                self._qobj = qobj
            
            def to_qobj(self):
                return self._qobj
            
            def to_density_matrix(self):
                if self._density_matrix is None:
                    self._density_matrix = self._qobj * self._qobj.dag()
                return self._density_matrix
        
        return TransformedState(output_qobj, state)


class Displacement(QuantumOperation):
    """Displacement operation D(α) = exp(α*a† - α*a)."""
    
    def __init__(self, mode: int, alpha: complex):
        """
        Initialize a displacement operation.
        
        Args:
            mode: Mode index
            alpha: Complex displacement amplitude
        """
        self.alpha = alpha
        
        parameters = {"alpha": alpha}
        
        super().__init__(
            OperationType.DISPLACEMENT,
            [mode],
            parameters,
            f"Displacement mode {mode} α={alpha:.3f}"
        )
    
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """Get the displacement operator."""
        mode = self.target_modes[0]
        dim = dimensions[mode]
        
        # Displacement operator
        displace_op = qt.displace(dim, self.alpha)
        
        # If multi-mode system, tensor with identity on other modes
        if len(dimensions) > 1:
            operators = []
            for i, d in enumerate(dimensions):
                if i == mode:
                    operators.append(displace_op)
                else:
                    operators.append(qt.qeye(d))
            displace_op = qt.tensor(*operators)
        
        return displace_op
    
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """Apply displacement to quantum state."""
        op = self.get_operator(state.dimensions)
        input_qobj = state.to_qobj()
        output_qobj = op * input_qobj
        
        class TransformedState(QuantumState):
            def __init__(self, qobj, original_state):
                super().__init__(
                    original_state.state_type,
                    original_state.dimensions,
                    f"Displaced {original_state.description}"
                )
                self._qobj = qobj
            
            def to_qobj(self):
                return self._qobj
            
            def to_density_matrix(self):
                if self._density_matrix is None:
                    self._density_matrix = self._qobj * self._qobj.dag()
                return self._density_matrix
        
        return TransformedState(output_qobj, state)


class Squeezing(QuantumOperation):
    """Single-mode squeezing operation S(ξ) = exp(ξ*a†² - ξ*a²)/2."""
    
    def __init__(self, mode: int, r: float, phi: float = 0):
        """
        Initialize a squeezing operation.
        
        Args:
            mode: Mode index
            r: Squeezing strength
            phi: Squeezing phase
        """
        self.r = r
        self.phi = phi
        self.xi = r * np.exp(1j * phi)
        
        parameters = {"r": r, "phi": phi, "xi": self.xi}
        
        super().__init__(
            OperationType.SQUEEZING,
            [mode],
            parameters,
            f"Squeezing mode {mode} r={r:.3f} φ={phi:.3f}"
        )
    
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """Get the squeezing operator."""
        mode = self.target_modes[0]
        dim = dimensions[mode]
        
        # Squeezing operator
        squeeze_op = qt.squeeze(dim, self.xi)
        
        # If multi-mode system, tensor with identity on other modes
        if len(dimensions) > 1:
            operators = []
            for i, d in enumerate(dimensions):
                if i == mode:
                    operators.append(squeeze_op)
                else:
                    operators.append(qt.qeye(d))
            squeeze_op = qt.tensor(*operators)
        
        return squeeze_op
    
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """Apply squeezing to quantum state."""
        op = self.get_operator(state.dimensions)
        input_qobj = state.to_qobj()
        output_qobj = op * input_qobj
        
        class TransformedState(QuantumState):
            def __init__(self, qobj, original_state):
                super().__init__(
                    original_state.state_type,
                    original_state.dimensions,
                    f"Squeezed {original_state.description}"
                )
                self._qobj = qobj
            
            def to_qobj(self):
                return self._qobj
            
            def to_density_matrix(self):
                if self._density_matrix is None:
                    self._density_matrix = self._qobj * self._qobj.dag()
                return self._density_matrix
        
        return TransformedState(output_qobj, state)


class Loss(QuantumOperation):
    """Photon loss channel (amplitude damping)."""
    
    def __init__(self, mode: int, loss_rate: float):
        """
        Initialize a loss channel.
        
        Args:
            mode: Mode index
            loss_rate: Loss rate (0 to 1)
        """
        if not 0 <= loss_rate <= 1:
            raise ValueError("Loss rate must be between 0 and 1")
        
        self.loss_rate = loss_rate
        self.transmission = 1 - loss_rate
        
        parameters = {"loss_rate": loss_rate, "transmission": self.transmission}
        
        super().__init__(
            OperationType.LOSS,
            [mode],
            parameters,
            f"Loss mode {mode} rate={loss_rate:.3f}"
        )
    
    def get_operator(self, dimensions: List[int]) -> qt.Qobj:
        """Get the loss operators (Kraus operators)."""
        # Loss is a non-unitary operation, requires density matrix formalism
        # This would return Kraus operators for the amplitude damping channel
        mode = self.target_modes[0]
        dim = dimensions[mode]
        
        # Kraus operators for amplitude damping
        a = qt.destroy(dim)
        K0 = qt.qeye(dim)  # No loss
        K1 = np.sqrt(self.loss_rate) * a  # Loss
        
        return [K0, K1]
    
    def apply_to_state(self, state: QuantumState) -> QuantumState:
        """Apply loss to quantum state."""
        # For loss, we need to work with density matrices
        rho_in = state.to_density_matrix()
        kraus_ops = self.get_operator(state.dimensions)
        
        # Apply Kraus operators
        rho_out = sum(K * rho_in * K.dag() for K in kraus_ops)
        
        class TransformedState(QuantumState):
            def __init__(self, rho, original_state):
                super().__init__(
                    original_state.state_type,
                    original_state.dimensions,
                    f"Lossy {original_state.description}"
                )
                self._density_matrix = rho
            
            def to_qobj(self):
                # For mixed states, return the density matrix
                return self._density_matrix
            
            def to_density_matrix(self):
                return self._density_matrix
        
        return TransformedState(rho_out, state)
