"""
Aṇubuddhi (अणुबुद्धि): LLM-Based Quantum Experiment Design System
Designed by S. K. Rithvik

A sophisticated agentic AI system that uses large language models and vector databases
to automatically design and optimize quantum optics experiments.
"""

from .core.system import AgenticQuantumSystem
from .core.config import Config
from .quantum.states import QuantumState
from .quantum.operations import QuantumOperation
from .quantum.measurements import Measurement
from .agents.designer_agent import DesignerAgent
from .agents.analyzer_agent import AnalyzerAgent
from .agents.optimizer_agent import OptimizerAgent
from .agents.knowledge_agent import KnowledgeAgent
from .agents.coordinator_agent import CoordinatorAgent

__version__ = "0.1.0"
__author__ = "S. K. Rithvik"

__all__ = [
    "AgenticQuantumSystem",
    "Config",
    "QuantumState",
    "QuantumOperation", 
    "Measurement",
    "DesignerAgent",
    "AnalyzerAgent",
    "OptimizerAgent",
    "KnowledgeAgent",
    "CoordinatorAgent",
]
