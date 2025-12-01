"""
Aṇubuddhi (अणुबुद्धि): LLM-Based Quantum Experiment Design System
Designed by S. K. Rithvik

Quantum primitives library for optical experiment simulation.
Provides states, operations, measurements, and simulation tools.
"""

from .quantum.states import QuantumState, FockState, CoherentState, SqueezedState
from .quantum.operations import QuantumOperation, BeamSplitter, PhaseShift
from .quantum.measurements import Measurement
from .llm.simple_client import SimpleLLM

__version__ = "0.1.0"
__author__ = "S. K. Rithvik"

__all__ = [
    # Quantum states
    "QuantumState",
    "FockState",
    "CoherentState",
    "SqueezedState",
    # Quantum operations
    "QuantumOperation", 
    "BeamSplitter",
    "PhaseShift",
    # Measurements
    "Measurement",
    # LLM client
    "SimpleLLM",
]
