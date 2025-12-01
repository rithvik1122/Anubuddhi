"""
Quantum simulation and experiment design module.
"""

from .states import (
    QuantumState,
    FockState,
    CoherentState,
    SqueezedState,
    SuperpositionState
)

from .operations import (
    QuantumOperation,
    BeamSplitter,
    PhaseShift,
    Displacement,
    Squeezing,
    Loss
)

from .measurements import (
    Measurement,
    MeasurementResult,
    PhotonNumberMeasurement,
    HomodyneMeasurement,
    BucketMeasurement,
    POVMMeasurement
)

from .experiment import (
    QuantumExperiment,
    ExperimentStep,
    ExperimentResults,
    create_interferometry_experiment,
    create_state_preparation_experiment
)

from .simulator import (
    QuantumSimulator,
    SimulationError,
    simulate_experiment,
    calculate_experiment_fom
)

__all__ = [
    # States
    "QuantumState",
    "FockState", 
    "CoherentState",
    "SqueezedState",
    "SuperpositionState",
    
    # Operations
    "QuantumOperation",
    "BeamSplitter",
    "PhaseShift", 
    "Displacement",
    "Squeezing",
    "Loss",
    
    # Measurements
    "Measurement",
    "MeasurementResult",
    "PhotonNumberMeasurement",
    "HomodyneMeasurement", 
    "BucketMeasurement",
    "POVMMeasurement",
    
    # Experiments
    "QuantumExperiment",
    "ExperimentStep",
    "ExperimentResults",
    "create_interferometry_experiment",
    "create_state_preparation_experiment",
    
    # Simulation
    "QuantumSimulator",
    "SimulationError",
    "simulate_experiment",
    "calculate_experiment_fom"
]
