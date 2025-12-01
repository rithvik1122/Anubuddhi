"""
Quantum simulator for executing experiments and computing figures of merit.
"""

import time
from typing import List, Dict, Any, Optional, Tuple, Callable
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging

try:
    import qutip as qt
    from qutip import Qobj
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False
    Qobj = None

from .states import QuantumState, FockState
from .operations import QuantumOperation
from .measurements import Measurement, MeasurementResult
from .experiment import QuantumExperiment, ExperimentResults


logger = logging.getLogger(__name__)


class SimulationError(Exception):
    """Raised when simulation encounters an error."""
    pass


class QuantumSimulator:
    """
    Quantum simulator for executing experiments and computing results.
    
    This simulator handles:
    - State evolution through operations
    - Measurement simulations
    - Figure of merit calculations
    - Monte Carlo sampling
    - Parallel execution of experiments
    """
    
    def __init__(self, 
                 max_dimension: int = 100,
                 num_samples: int = 1000,
                 parallel: bool = True,
                 max_workers: Optional[int] = None):
        """
        Initialize the quantum simulator.
        
        Args:
            max_dimension: Maximum Hilbert space dimension per mode
            num_samples: Default number of Monte Carlo samples
            parallel: Whether to use parallel execution
            max_workers: Maximum number of worker threads
        """
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP is required for quantum simulation")
        
        self.max_dimension = max_dimension
        self.num_samples = num_samples
        self.parallel = parallel
        self.max_workers = max_workers
        
        # Simulation state
        self.current_state: Optional[Qobj] = None
        self.intermediate_states: List[Qobj] = []
        self.measurement_results: List[MeasurementResult] = []
        
        # Performance tracking
        self.execution_times: Dict[str, float] = {}
        
    def execute_experiment(self, experiment: QuantumExperiment) -> ExperimentResults:
        """
        Execute a complete quantum experiment.
        
        Args:
            experiment: The experiment to execute
        
        Returns:
            Experiment results including figures of merit
        """
        start_time = time.time()
        
        # Validate experiment
        errors = experiment.validate()
        if errors:
            raise SimulationError(f"Invalid experiment: {'; '.join(errors)}")
        
        logger.info(f"Executing experiment {experiment.experiment_id}")
        
        # Initialize results
        results = ExperimentResults(experiment_id=experiment.experiment_id)
        
        try:
            # Prepare initial state
            if experiment.initial_state is None:
                raise SimulationError("No initial state specified")
            
            self.current_state = experiment.initial_state.to_qutip()
            self.intermediate_states = [self.current_state.copy()]
            self.measurement_results = []
            
            # Execute each step
            for step in experiment.steps:
                if step.step_type == "operation":
                    self._apply_operation(step.component)
                elif step.step_type == "measurement":
                    result = self._perform_measurement(step.component)
                    self.measurement_results.append(result)
            
            # Store results
            results.final_state = self._qutip_to_quantum_state(self.current_state)
            results.measurement_results = self.measurement_results.copy()
            results.intermediate_states = [
                self._qutip_to_quantum_state(state) for state in self.intermediate_states
            ]
            
            # Calculate figures of merit
            results.figures_of_merit = self._calculate_figures_of_merit(
                experiment, results
            )
            
            # Calculate success probability (if applicable)
            results.success_probability = self._calculate_success_probability(
                experiment, results
            )
            
            results.execution_time = time.time() - start_time
            
            logger.info(f"Experiment completed in {results.execution_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            results.metadata["error"] = str(e)
            results.execution_time = time.time() - start_time
            raise SimulationError(f"Simulation failed: {str(e)}") from e
        
        return results
    
    def run_monte_carlo(self, 
                       experiment: QuantumExperiment, 
                       num_runs: Optional[int] = None) -> List[ExperimentResults]:
        """
        Run multiple instances of an experiment for statistical analysis.
        
        Args:
            experiment: The experiment to run
            num_runs: Number of runs (uses default if None)
        
        Returns:
            List of experiment results
        """
        num_runs = num_runs or self.num_samples
        
        logger.info(f"Running Monte Carlo simulation with {num_runs} runs")
        
        if self.parallel and num_runs > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.execute_experiment, experiment.clone())
                    for _ in range(num_runs)
                ]
                results = [future.result() for future in futures]
        else:
            results = []
            for i in range(num_runs):
                if i % 100 == 0:
                    logger.info(f"Run {i+1}/{num_runs}")
                results.append(self.execute_experiment(experiment.clone()))
        
        logger.info("Monte Carlo simulation completed")
        return results
    
    def _apply_operation(self, operation: QuantumOperation):
        """Apply a quantum operation to the current state."""
        # Get dimensions from current state
        dimensions = self.current_state.dims[0]
        operation_matrix = operation.get_operator(dimensions)
        
        # Apply as unitary evolution (most quantum optics operations are unitary)
        self.current_state = operation_matrix * self.current_state
        
        self.intermediate_states.append(self.current_state.copy())
    
    def _perform_measurement(self, measurement: Measurement) -> MeasurementResult:
        """Perform a quantum measurement."""
        # Get measurement probabilities
        probabilities = measurement.get_probabilities(self.current_state)
        
        # Sample outcome
        outcomes = list(range(len(probabilities)))
        chosen_outcome = np.random.choice(outcomes, p=probabilities)
        
        # Get post-measurement state
        post_state = measurement.get_post_measurement_state(
            self.current_state, chosen_outcome
        )
        
        # Update current state
        self.current_state = post_state
        self.intermediate_states.append(self.current_state.copy())
        
        # Create result
        result = MeasurementResult(
            measurement_type=measurement.__class__.__name__,
            outcome=chosen_outcome,
            probability=probabilities[chosen_outcome],
            measurement_operator=measurement.get_operators()[chosen_outcome],
            metadata={"target_modes": measurement.target_modes}
        )
        
        return result
    
    def _calculate_figures_of_merit(self, 
                                  experiment: QuantumExperiment,
                                  results: ExperimentResults) -> Dict[str, float]:
        """Calculate various figures of merit for the experiment."""
        foms = {}
        
        # Basic quantum metrics
        if results.final_state and hasattr(results.final_state, 'to_qutip'):
            final_qutip = results.final_state.to_qutip()
            
            # Purity
            rho = final_qutip * final_qutip.dag()
            foms["purity"] = float(np.real((rho * rho).tr()))
            
            # von Neumann entropy
            eigenvals = rho.eigenenergies()
            eigenvals = eigenvals[eigenvals > 1e-12]  # Avoid log(0)
            foms["von_neumann_entropy"] = float(-np.sum(eigenvals * np.log2(eigenvals)))
            
            # Mean photon number (for optical states)
            if hasattr(final_qutip, 'dims') and len(final_qutip.dims[0]) > 0:
                for mode in range(len(final_qutip.dims[0])):
                    n_op = qt.num(final_qutip.dims[0][mode])
                    if mode == 0:
                        n_total = n_op
                    else:
                        # Tensor with identity for other modes
                        ops = [qt.qeye(d) for d in final_qutip.dims[0]]
                        ops[mode] = n_op
                        n_mode = qt.tensor(*ops)
                        n_total = n_total + n_mode if mode > 0 else n_mode
                
                foms[f"mean_photon_number"] = float(np.real(qt.expect(n_total, final_qutip)))
        
        # Measurement-based metrics
        if results.measurement_results:
            # Success probability for projective measurements
            success_outcomes = [r for r in results.measurement_results if r.probability > 0.5]
            foms["measurement_success_rate"] = len(success_outcomes) / len(results.measurement_results)
            
            # Average measurement probability
            avg_prob = np.mean([r.probability for r in results.measurement_results])
            foms["average_measurement_probability"] = float(avg_prob)
        
        # Fidelity with target states (if specified)
        if experiment.target_figures_of_merit:
            for target_name, target_value in experiment.target_figures_of_merit.items():
                if target_name in foms:
                    foms[f"fidelity_to_{target_name}"] = 1.0 - abs(foms[target_name] - target_value)
        
        # Execution efficiency
        foms["execution_time"] = results.execution_time
        foms["steps_per_second"] = len(experiment.steps) / max(results.execution_time, 1e-6)
        
        return foms
    
    def _calculate_success_probability(self,
                                     experiment: QuantumExperiment,
                                     results: ExperimentResults) -> float:
        """Calculate overall success probability for the experiment."""
        # For now, multiply all measurement probabilities
        if results.measurement_results:
            prob = 1.0
            for result in results.measurement_results:
                prob *= result.probability
            return prob
        return 1.0
    
    def _qutip_to_quantum_state(self, qutip_state: Qobj) -> QuantumState:
        """Convert QuTiP state back to QuantumState object."""
        # Create a generic quantum state wrapper that holds the QuTiP object
        # Get number of modes from dimensions
        dims = qutip_state.dims[0]
        
        # Create a simple wrapper state
        from .states import QuantumState, StateType
        
        class GenericState(QuantumState):
            def __init__(self, qobj, dims):
                super().__init__(StateType.FOCK, dims, "Simulated state")
                self._qobj = qobj
                self._density_matrix = qobj * qobj.dag()
            
            def to_qobj(self):
                return self._qobj
            
            def to_density_matrix(self):
                return self._density_matrix
        
        return GenericState(qutip_state, dims)
    
    def calculate_fisher_information(self,
                                   experiment: QuantumExperiment,
                                   parameter: str,
                                   delta: float = 1e-6) -> float:
        """
        Calculate Fisher information for parameter estimation.
        
        Args:
            experiment: The experiment
            parameter: Parameter name to calculate Fisher information for
            delta: Small parameter shift for numerical derivative
        
        Returns:
            Fisher information value
        """
        # Create experiments with parameter shifts
        exp_plus = experiment.clone()
        exp_minus = experiment.clone()
        
        # Modify parameter (this would need to be implemented per parameter type)
        current_value = experiment.parameters.get(parameter, 0.0)
        exp_plus.parameters[parameter] = current_value + delta
        exp_minus.parameters[parameter] = current_value - delta
        
        # Run simulations
        results_plus = self.execute_experiment(exp_plus)
        results_minus = self.execute_experiment(exp_minus)
        
        # Calculate numerical derivative of log-likelihood
        # This is a simplified calculation
        prob_plus = results_plus.success_probability
        prob_minus = results_minus.success_probability
        
        if prob_plus > 0 and prob_minus > 0:
            derivative = (np.log(prob_plus) - np.log(prob_minus)) / (2 * delta)
            return derivative ** 2
        
        return 0.0
    
    def optimize_measurement_settings(self,
                                    experiment: QuantumExperiment,
                                    measurement_index: int,
                                    parameter_ranges: Dict[str, Tuple[float, float]],
                                    num_points: int = 20) -> Dict[str, Any]:
        """
        Optimize measurement settings for maximum information gain.
        
        Args:
            experiment: The experiment
            measurement_index: Index of measurement to optimize
            parameter_ranges: Dictionary of parameter ranges to search
            num_points: Number of points to sample per parameter
        
        Returns:
            Optimization results
        """
        best_settings = {}
        best_fom = -np.inf
        
        # Grid search over parameters
        param_names = list(parameter_ranges.keys())
        param_values = [
            np.linspace(ranges[0], ranges[1], num_points)
            for ranges in parameter_ranges.values()
        ]
        
        # Generate all combinations
        from itertools import product
        
        for values in product(*param_values):
            settings = dict(zip(param_names, values))
            
            # Modify experiment
            test_exp = experiment.clone()
            measurement = test_exp.get_measurements()[measurement_index]
            
            # Update measurement parameters (this would need implementation per measurement type)
            for param, value in settings.items():
                setattr(measurement, param, value)
            
            # Evaluate
            try:
                results = self.execute_experiment(test_exp)
                fom = results.figures_of_merit.get("measurement_success_rate", 0.0)
                
                if fom > best_fom:
                    best_fom = fom
                    best_settings = settings.copy()
            except Exception as e:
                logger.warning(f"Failed to evaluate settings {settings}: {e}")
                continue
        
        return {
            "best_settings": best_settings,
            "best_fom": best_fom,
            "parameter_ranges": parameter_ranges
        }
    
    def benchmark_experiment(self, experiment: QuantumExperiment) -> Dict[str, Any]:
        """
        Benchmark an experiment for performance analysis.
        
        Args:
            experiment: The experiment to benchmark
        
        Returns:
            Benchmark results
        """
        num_runs = min(100, self.num_samples)
        start_time = time.time()
        
        results = self.run_monte_carlo(experiment, num_runs)
        total_time = time.time() - start_time
        
        # Calculate statistics
        fom_stats = {}
        if results:
            all_foms = {}
            for result in results:
                for fom_name, value in result.figures_of_merit.items():
                    if fom_name not in all_foms:
                        all_foms[fom_name] = []
                    all_foms[fom_name].append(value)
            
            for fom_name, values in all_foms.items():
                fom_stats[fom_name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        
        return {
            "num_runs": num_runs,
            "total_time": total_time,
            "time_per_run": total_time / num_runs,
            "fom_statistics": fom_stats,
            "success_rate": len([r for r in results if len(r.figures_of_merit) > 0]) / len(results)
        }


# Convenience functions

def simulate_experiment(experiment: QuantumExperiment,
                       num_samples: int = 1000,
                       parallel: bool = True) -> List[ExperimentResults]:
    """
    Convenience function to simulate an experiment.
    
    Args:
        experiment: The experiment to simulate
        num_samples: Number of Monte Carlo samples
        parallel: Whether to use parallel execution
    
    Returns:
        List of experiment results
    """
    simulator = QuantumSimulator(
        num_samples=num_samples,
        parallel=parallel
    )
    
    return simulator.run_monte_carlo(experiment, num_samples)


def calculate_experiment_fom(experiment: QuantumExperiment,
                           fom_name: str = "measurement_success_rate") -> float:
    """
    Calculate a specific figure of merit for an experiment.
    
    Args:
        experiment: The experiment
        fom_name: Name of the figure of merit
    
    Returns:
        Figure of merit value
    """
    simulator = QuantumSimulator(num_samples=100)
    results = simulator.run_monte_carlo(experiment, 10)
    
    # Average the FOM across runs
    fom_values = []
    for result in results:
        if fom_name in result.figures_of_merit:
            fom_values.append(result.figures_of_merit[fom_name])
    
    return float(np.mean(fom_values)) if fom_values else 0.0
