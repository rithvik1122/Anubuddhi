"""
Quantum experiment representation and management.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from .states import QuantumState
from .operations import QuantumOperation
from .measurements import Measurement, MeasurementResult


@dataclass
class ExperimentStep:
    """Represents a single step in a quantum experiment."""
    step_type: str  # "state", "operation", "measurement"
    component: Union[QuantumState, QuantumOperation, Measurement]
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "description": self.description,
            "component": self.component.to_dict(),
            "metadata": self.metadata
        }


@dataclass
class ExperimentResults:
    """Container for quantum experiment results."""
    experiment_id: str
    final_state: Optional[QuantumState] = None
    measurement_results: List[MeasurementResult] = field(default_factory=list)
    figures_of_merit: Dict[str, float] = field(default_factory=dict)
    intermediate_states: List[QuantumState] = field(default_factory=list)
    execution_time: float = 0.0
    success_probability: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "figures_of_merit": self.figures_of_merit,
            "execution_time": self.execution_time,
            "success_probability": self.success_probability,
            "num_measurement_results": len(self.measurement_results),
            "num_intermediate_states": len(self.intermediate_states),
            "metadata": self.metadata
        }


class QuantumExperiment:
    """
    Represents a complete quantum experiment.
    
    A quantum experiment consists of:
    1. Initial state preparation
    2. Sequence of operations (unitary and non-unitary)
    3. Measurements
    4. Analysis and figures of merit
    """
    
    def __init__(self, description: str = "", experiment_id: Optional[str] = None):
        """
        Initialize a quantum experiment.
        
        Args:
            description: Human-readable description
            experiment_id: Unique identifier (auto-generated if None)
        """
        self.experiment_id = experiment_id or str(uuid.uuid4())
        self.description = description
        self.steps: List[ExperimentStep] = []
        self.initial_state: Optional[QuantumState] = None
        self.num_modes: int = 0
        self.mode_dimensions: List[int] = []
        
        # Experiment metadata
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.tags: List[str] = []
        self.parameters: Dict[str, Any] = {}
        self.constraints: Dict[str, Any] = {}
        self.target_figures_of_merit: Dict[str, float] = {}
        
        # Results (populated after execution)
        self.results: Optional[ExperimentResults] = None
    
    def set_initial_state(self, state: QuantumState) -> "QuantumExperiment":
        """
        Set the initial state of the experiment.
        
        Args:
            state: Initial quantum state
        
        Returns:
            Self for method chaining
        """
        self.initial_state = state
        self.num_modes = state.num_modes
        self.mode_dimensions = state.dimensions
        
        # Add as first step
        step = ExperimentStep(
            step_type="state",
            component=state,
            description=f"Initial state: {state.description}"
        )
        
        if self.steps and self.steps[0].step_type == "state":
            # Replace existing initial state
            self.steps[0] = step
        else:
            # Insert at beginning
            self.steps.insert(0, step)
        
        self.updated_at = datetime.now()
        return self
    
    def add_operation(self, operation: QuantumOperation) -> "QuantumExperiment":
        """
        Add a quantum operation to the experiment.
        
        Args:
            operation: Quantum operation to add
        
        Returns:
            Self for method chaining
        """
        step = ExperimentStep(
            step_type="operation",
            component=operation,
            description=f"Operation: {operation.description}"
        )
        
        self.steps.append(step)
        self.updated_at = datetime.now()
        return self
    
    def add_measurement(self, measurement: Measurement) -> "QuantumExperiment":
        """
        Add a measurement to the experiment.
        
        Args:
            measurement: Measurement to add
        
        Returns:
            Self for method chaining
        """
        step = ExperimentStep(
            step_type="measurement",
            component=measurement,
            description=f"Measurement: {measurement.description}"
        )
        
        self.steps.append(step)
        self.updated_at = datetime.now()
        return self
    
    def set_parameters(self, parameters: Dict[str, Any]) -> "QuantumExperiment":
        """Set experiment parameters."""
        self.parameters.update(parameters)
        self.updated_at = datetime.now()
        return self
    
    def set_constraints(self, constraints: Dict[str, Any]) -> "QuantumExperiment":
        """Set experiment constraints."""
        self.constraints.update(constraints)
        self.updated_at = datetime.now()
        return self
    
    def set_target_fom(self, name: str, value: float) -> "QuantumExperiment":
        """Set target figure of merit."""
        self.target_figures_of_merit[name] = value
        self.updated_at = datetime.now()
        return self
    
    def add_tag(self, tag: str) -> "QuantumExperiment":
        """Add a tag to the experiment."""
        if tag not in self.tags:
            self.tags.append(tag)
        self.updated_at = datetime.now()
        return self
    
    def get_operations(self) -> List[QuantumOperation]:
        """Get all operations in the experiment."""
        return [step.component for step in self.steps if step.step_type == "operation"]
    
    def get_measurements(self) -> List[Measurement]:
        """Get all measurements in the experiment."""
        return [step.component for step in self.steps if step.step_type == "measurement"]
    
    def get_operation_sequence(self) -> List[QuantumOperation]:
        """Get operations in the order they appear."""
        operations = []
        for step in self.steps:
            if step.step_type == "operation":
                operations.append(step.component)
        return operations
    
    def validate(self) -> List[str]:
        """
        Validate the experiment configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for initial state
        if self.initial_state is None:
            errors.append("No initial state specified")
        
        # Check operation modes are valid
        for operation in self.get_operations():
            for mode in operation.target_modes:
                if mode >= self.num_modes:
                    errors.append(f"Operation {operation.description} targets invalid mode {mode}")
        
        # Check measurement modes are valid
        for measurement in self.get_measurements():
            for mode in measurement.target_modes:
                if mode >= self.num_modes:
                    errors.append(f"Measurement {measurement.description} targets invalid mode {mode}")
        
        return errors
    
    def clone(self) -> "QuantumExperiment":
        """Create a copy of the experiment."""
        clone = QuantumExperiment(
            description=f"Copy of {self.description}",
            experiment_id=None  # Generate new ID
        )
        
        # Copy all attributes
        if self.initial_state:
            clone.set_initial_state(self.initial_state)
        
        # Copy steps (excluding initial state which is handled above)
        for step in self.steps[1:]:  # Skip first step if it's the initial state
            if step.step_type == "operation":
                clone.add_operation(step.component)
            elif step.step_type == "measurement":
                clone.add_measurement(step.component)
        
        clone.set_parameters(self.parameters.copy())
        clone.set_constraints(self.constraints.copy())
        clone.target_figures_of_merit = self.target_figures_of_merit.copy()
        clone.tags = self.tags.copy()
        
        return clone
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert experiment to dictionary representation."""
        return {
            "experiment_id": self.experiment_id,
            "description": self.description,
            "num_modes": self.num_modes,
            "mode_dimensions": self.mode_dimensions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "parameters": self.parameters,
            "constraints": self.constraints,
            "target_figures_of_merit": self.target_figures_of_merit,
            "steps": [step.to_dict() for step in self.steps],
            "results": self.results.to_dict() if self.results else None,
            "is_valid": len(self.validate()) == 0
        }
    
    def to_json(self) -> str:
        """Convert experiment to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def save(self, filepath: str):
        """Save experiment to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, filepath: str) -> "QuantumExperiment":
        """Load experiment from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # This would need more complex deserialization logic
        # For now, just create a basic experiment
        experiment = cls(
            description=data.get("description", ""),
            experiment_id=data.get("experiment_id")
        )
        
        return experiment
    
    def __str__(self) -> str:
        """String representation of the experiment."""
        return f"QuantumExperiment(id={self.experiment_id[:8]}, modes={self.num_modes}, steps={len(self.steps)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"QuantumExperiment(id='{self.experiment_id}', "
                f"description='{self.description}', "
                f"num_modes={self.num_modes}, "
                f"num_steps={len(self.steps)})")


# Convenience functions for creating common experiments

def create_interferometry_experiment(
    input_state: QuantumState,
    phase_shift: float,
    measurement_type: str = "photon_number"
) -> QuantumExperiment:
    """
    Create a basic interferometry experiment.
    
    Args:
        input_state: Input quantum state
        phase_shift: Phase shift to apply
        measurement_type: Type of measurement ("photon_number", "homodyne", "bucket")
    
    Returns:
        Configured experiment
    """
    from .operations import PhaseShift
    from .measurements import PhotonNumberMeasurement, HomodyneMeasurement, BucketMeasurement
    
    experiment = QuantumExperiment("Interferometry experiment")
    experiment.set_initial_state(input_state)
    
    # Add phase shift
    phase_op = PhaseShift(mode=0, phase=phase_shift)
    experiment.add_operation(phase_op)
    
    # Add measurement
    if measurement_type == "photon_number":
        measurement = PhotonNumberMeasurement(mode=0)
    elif measurement_type == "homodyne":
        measurement = HomodyneMeasurement(mode=0)
    elif measurement_type == "bucket":
        measurement = BucketMeasurement(mode=0)
    else:
        raise ValueError(f"Unknown measurement type: {measurement_type}")
    
    experiment.add_measurement(measurement)
    experiment.add_tag("interferometry")
    experiment.add_tag("phase_measurement")
    
    return experiment


def create_state_preparation_experiment(
    target_state_type: str,
    parameters: Dict[str, Any]
) -> QuantumExperiment:
    """
    Create an experiment to prepare a specific quantum state.
    
    Args:
        target_state_type: Type of state to prepare
        parameters: State parameters
    
    Returns:
        Configured experiment template
    """
    experiment = QuantumExperiment(f"State preparation: {target_state_type}")
    
    # This would be expanded to create specific state preparation protocols
    experiment.add_tag("state_preparation")
    experiment.add_tag(target_state_type)
    experiment.set_parameters(parameters)
    
    return experiment
