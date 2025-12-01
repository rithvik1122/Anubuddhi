# Copilot Instructions for AgenticQuantum

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is an LLM-based agentic AI system for designing quantum experiments. The system uses multiple specialized agents to automatically discover, design, and optimize quantum optics experiments.

## Key Technologies
- **Quantum Computing**: Qiskit, QuTiP, NumPy for quantum state manipulation
- **LLM Integration**: OpenAI API, Anthropic Claude, local models via Ollama
- **Vector Database**: ChromaDB for storing experimental knowledge
- **Agentic Framework**: LangChain/LangGraph for multi-agent workflows
- **Optimization**: Genetic algorithms, reinforcement learning, Bayesian optimization

## Coding Guidelines
1. **Quantum Operations**: Use proper quantum state normalization and error handling
2. **Agent Communication**: Implement clear message passing between agents
3. **Knowledge Storage**: Store all experimental results in vector database with metadata
4. **Error Handling**: Robust error handling for quantum simulations and LLM calls
5. **Modularity**: Keep agents, quantum operations, and optimization algorithms separate
6. **Testing**: Include unit tests for quantum operations and agent behaviors

## Agent Types
- **Designer Agent**: Creates new experimental configurations
- **Analyzer Agent**: Evaluates quantum states and figures of merit
- **Optimizer Agent**: Improves existing experiments using various algorithms
- **Knowledge Agent**: Manages historical data and retrieves relevant information
- **Coordinator Agent**: Orchestrates the overall experimental design process

## Quantum Experiment Structure
- **States**: Fock, coherent, squeezed, entangled states
- **Operations**: Beam splitters, phase shifts, displacement, squeezing
- **Measurements**: Photon counting, homodyne, heterodyne detection
- **Figures of Merit**: Quantum Fisher Information, fidelity, entanglement measures
