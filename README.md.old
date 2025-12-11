# Agentic Quantum: LLM-Based Quantum Experiment Design System

**An intelligent multi-agent system for automated quantum experiment design, optimization, and analysis.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Quantum: QuTiP](https://img.shields.io/badge/Quantum-QuTiP-orange.svg)](http://qutip.org/)
[![AI: LangChain](https://img.shields.io/badge/AI-LangChain-green.svg)](https://www.langchain.com/)

## 🌟 Overview

Agentic Quantum is a cutting-edge AI system that combines Large Language Models (LLMs) with quantum physics expertise to autonomously design, analyze, and optimize quantum optics experiments. The system learns from each experiment, building expertise over time through a sophisticated multi-agent architecture.

### ⚡ Key Features

- **🤖 Multi-Agent Intelligence**: Specialized AI agents for design, analysis, optimization, knowledge management, and coordination
- **🧠 LLM-Powered**: Integration with OpenAI GPT-4, Anthropic Claude, and local models via Ollama
- **📚 Knowledge Evolution**: Vector database storage with ChromaDB for continuous learning
- **🔬 Quantum Simulation**: High-fidelity quantum state and operation simulation using QuTiP
- **🎯 Advanced Optimization**: Genetic algorithms, Bayesian optimization, and reinforcement learning
- **📊 Intelligent Analysis**: Pattern detection, anomaly identification, and insight generation
- **🔄 Adaptive Workflows**: Dynamic workflow orchestration based on experiment complexity and system state

## 🏗️ Architecture

The system consists of five specialized agents working together:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Designer      │    │    Analyzer     │    │   Optimizer     │
│     Agent       │    │     Agent       │    │     Agent       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Experiment    │    │ • Result        │    │ • Genetic       │
│   Design        │    │   Evaluation    │    │   Algorithms    │
│ • State Prep    │    │ • Pattern       │    │ • Bayesian Opt  │
│ • Protocol      │    │   Detection     │    │ • Multi-obj     │
│   Generation    │    │ • Insight Gen   │    │   Optimization  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐
         │   Knowledge     │    │  Coordinator    │
         │     Agent       │    │     Agent       │
         ├─────────────────┤    ├─────────────────┤
         │ • Vector DB     │    │ • Workflow      │
         │ • Learning      │    │   Orchestration │
         │ • Retrieval     │    │ • Task          │
         │ • Pattern       │    │   Scheduling    │
         │   Analysis      │    │ • Performance   │
         └─────────────────┘    │   Monitoring    │
                                └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Anaconda or Miniconda** (recommended for scientific computing)
- **Python 3.9+** (will be installed automatically via conda)
- **API Keys** (at least one):
  - OpenAI API key for GPT-4
  - Anthropic API key for Claude (optional)
  - Or local LLM via Ollama (optional)

### Installation

**Option 1: Automated Installation (Recommended)**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Agentic
   ```

2. **Run the installation script:**
   ```bash
   ./install.sh
   ```

**Option 2: Manual conda setup**

1. **Create conda environment:**
   ```bash
   conda env create -f environment.yml
   ```

2. **Activate environment:**
   ```bash
   conda activate agentic-quantum
   ```

3. **Install package in development mode:**
   ```bash
   pip install -e .
   ```

**Option 3: Traditional pip setup**

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

### Configuration

3. **Configure API keys:**
   ```bash
   # Edit the .env file with your API keys
   nano .env
   ```

4. **Activate the environment:**
   ```bash
   conda activate agentic-quantum
   ```

5. **Run the demo:**
   ```bash
   python examples/complete_workflow_demo.py
   ```

## Configuration

The system can be configured through environment variables:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OLLAMA_BASE_URL=http://localhost:11434

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Quantum Simulation
MAX_HILBERT_SPACE_DIM=200
DEFAULT_TRUNCATION=50
```

## Examples

See the `examples/` directory for:
- Basic quantum state generation
- Multi-agent experiment design
- Knowledge base querying
- Custom fitness function optimization

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black src/
flake8 src/

# Run type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@software{agentic_quantum_2025,
  title={AgenticQuantum: LLM-Based Quantum Experiment Design},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/AgenticQuantum}
}
```
