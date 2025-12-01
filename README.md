# Aṇubuddhi (अणुबुद्धि)

**AI-Powered Quantum Optics Experiment Designer**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

## 🌟 Overview

**Aṇubuddhi** (Sanskrit: अणुबुद्धि, "Atomic Intelligence") is an LLM-powered system that designs quantum optics experiments through natural conversation. Using Large Language Models with physics knowledge, it generates complete optical setups, validates designs through simulation, and learns from each experiment.

### What Makes It Unique

- **💬 Conversational Design**: Describe your experiment in plain English - the AI translates it into optical components
- **🎨 Intelligent Layout**: Automatically generates 2D optical table layouts with proper beam routing
- **🔬 Dual-Mode Simulation**: Validates designs using both QuTiP (Fock states) and FreeSim (full physics freedom)
- **🧠 Learning System**: Builds a toolbox of reusable composite components from successful designs
- **🔄 Self-Refinement**: Iteratively improves designs through validation loops (up to 3 cycles)
- **🔍 Web-Enhanced**: Can search for quantum optics papers and protocols when needed

## 🏗️ System Architecture

The system uses a **cognitive pipeline** with specialized components:

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│          (Streamlit Chat + Optical Table Viewer)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    LLM Designer Agent                        │
│  • Conversational routing (chat vs. design mode)            │
│  • Memory-augmented design generation                       │
│  • Self-refinement loop (validation → critique → improve)   │
│  • Toolbox integration (primitives + learned composites)    │
└───────────┬───────────────────┬─────────────────────────────┘
            │                   │
┌───────────▼──────┐  ┌────────▼──────────────────────────────┐
│  Toolbox System  │  │  FreeForm Simulation Agent            │
│  • Primitives    │  │  • Physics-aware code generation      │
│  • Composites    │  │  • Learns from successful simulations │
│  • Custom blocks │  │  • Full scientific Python freedom     │
└──────────────────┘  └───────────────────────────────────────┘
            │                   │
┌───────────▼──────┐  ┌────────▼──────────────────────────────┐
│ Embedding Search │  │  Optical Table Renderer               │
│ • BGE-M3 model   │  │  • Component positioning              │
│ • Semantic       │  │  • Beam path calculation              │
│   retrieval      │  │  • Matplotlib visualization           │
└──────────────────┘  └───────────────────────────────────────┘
```

### Core Components

1. **`app.py`** - Streamlit web interface with dual-column chat/design layout
2. **`llm_designer.py`** - Main LLM agent with self-refinement and memory
3. **`freeform_simulation_agent.py`** - Physics-aware simulation code generator
4. **`toolbox_loader.py`** - Manages primitives and learned composite components
5. **`simple_optical_table.py`** - 2D optical table renderer with beam routing
6. **`embedding_retriever.py`** - Semantic search using BGE-M3 embeddings
7. **`src/agentic_quantum/`** - Lightweight quantum primitives library (states, operations, LLM client)

### Design Philosophy

The system combines **three cognitive layers**:

1. **Conversational Layer**: Natural language understanding for experiment descriptions
2. **Design Layer**: Component selection, layout generation, and beam path planning
3. **Validation Layer**: Physics simulation and iterative refinement

Unlike traditional CAD tools, Aṇubuddhi understands physics intent and automatically handles:
- Component placement and orientation
- Beam routing and path calculation
- Physics validation and error detection
- Design improvement suggestions

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- API key from OpenRouter, OpenAI, or Anthropic

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rithvik1122/Anubuddhi.git
   cd Anubuddhi
   ```

2. **Run the automated setup:**
   ```bash
   bash install.sh
   ```
   
   This will:
   - Create a conda environment with Python 3.9
   - Install all dependencies (numpy, qutip, streamlit, etc.)
   - Set up the project structure

3. **Configure API key:**
   ```bash
   cp .env.example .env
   nano .env  # Add your API key
   ```
   
   Required in `.env`:
   ```env
   OPENAI_API_KEY=your_openrouter_or_openai_key_here
   ```

4. **Launch the application:**
   ```bash
   bash launch.sh
   ```
   
   Or manually:
   ```bash
   conda activate anubuddhi
   streamlit run app.py
   ```

5. **Open browser** to `http://localhost:8501`

### First Experiment

Try these example prompts:

```
"Design a Hong-Ou-Mandel interference experiment"

"Create a Mach-Zehnder interferometer with two detectors"

"Build a Bell state generator using SPDC"

"I want to measure photon correlations between two outputs"
```

The AI will:
1. Generate an optical table layout
2. Place and orient all components
3. Calculate beam paths
4. Validate the design through simulation
5. Refine if issues are found

## 📁 Project Structure

```
Anubuddhi/
├── app.py                          # Main Streamlit application
├── llm_designer.py                 # LLM agent with self-refinement
├── freeform_simulation_agent.py    # Physics simulation generator
├── toolbox_loader.py               # Component toolbox manager
├── simple_optical_table.py         # Optical table renderer
├── embedding_retriever.py          # Semantic search engine
├── install.sh                      # Automated installation script
├── launch.sh                       # Application launcher
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
├── .gitignore                      # Git exclusions
│
├── src/agentic_quantum/           # Quantum primitives library
│   ├── quantum/                   # Quantum states and operations
│   │   ├── states.py              # Fock, coherent, squeezed states
│   │   ├── operations.py          # Beam splitters, phase shifts
│   │   ├── measurements.py        # Detection and measurement
│   │   ├── experiment.py          # Experiment construction
│   │   └── simulator.py           # QuTiP-based simulator
│   ├── llm/                       # LLM client wrapper
│   │   └── simple_client.py       # SimpleLLM class
│   └── visualization/             # Plotting utilities
│       └── optical_table.py       # Optical table rendering
│
├── toolbox/                       # Component definitions
│   ├── primitives.json            # Basic optical components
│   ├── learned_composites.json    # User-approved building blocks
│   ├── custom_components.json     # Custom user components
│   └── simulation_toolbox.json    # Simulation patterns
│
├── Results_FreeSim/               # Freeform simulation results
│   └── [experiment_folders]/      # Complete experimental data
│       ├── 01_freeform_simulation.py
│       ├── 03_simulation_report.md
│       ├── 04_analysis_results.json
│       ├── 06_design_specification.json
│       ├── 07_optical_setup.png
│       └── figures/
│
└── Results_QuTiP/                 # QuTiP-constrained results
    └── [experiment_folders]/      # QuTiP validation runs
        ├── 03_qutip_simulation.py
        ├── 04_design_components.json
        ├── 05_deep_analysis.md
        └── 01_optical_setup.png
```

## 🔧 How It Works

### 1. Conversational Routing

The system first determines your intent:
- **Chat mode**: Questions, explanations, physics discussions
- **Design mode**: "Create", "design", "build" trigger design generation

### 2. Design Generation

The LLM Designer:
1. Retrieves similar past experiments from memory
2. Selects appropriate optical components from toolbox
3. Generates component positions and orientations
4. Calculates beam paths between components
5. Provides physics justification for each choice

### 3. Validation & Refinement

Automated quality checks:
- Component overlap detection
- Beam path feasibility
- Physics consistency validation
- Simulation-based verification

If issues are found, the system automatically refines the design (up to 3 cycles).

### 4. Simulation

Two simulation modes:

**QuTiP Mode** (Fock space):
- Best for: Interferometry, beam splitters, phase shifts
- Constraints: Discrete photon numbers, limited Hilbert space
- Speed: Fast, numerically stable

**FreeSim Mode** (full freedom):
- Best for: Temporal effects, continuous variables, atomic physics
- Freedom: Any Python library (NumPy, SciPy, custom models)
- Flexibility: Chooses appropriate formalism per experiment

### 5. Learning

The system learns by:
- Storing successful designs in toolbox as "learned composites"
- Building embedding index for semantic component search
- Tracking simulation patterns for different experiment types
- Accumulating physics knowledge from validated designs

## 🧪 Experimental Results

This repository includes **15 complete quantum experiments** designed by the system:

### Tier 1: Foundational Experiments (5)
- Mach-Zehnder Interferometer
- Hong-Ou-Mandel Interference
- Michelson Interferometer
- Bell State Generator (SPDC)
- Delayed Choice Quantum Eraser

### Tier 2: Advanced Protocols (7)
- 3-Photon GHZ State Generator
- Quantum Teleportation
- Franson Interferometer (Time-Bin Entanglement)
- 4-Photon Boson Sampling
- Squeezed Light via OPO
- BB84 Quantum Key Distribution
- Continuous-Variable Quantum Teleportation

### Tier 3: Frontier Technology (3)
- Electromagnetically Induced Transparency (EIT)
- Hyperentangled Photon Source (Polarization + OAM)
- Quantum Frequency Converter (Telecom to Visible)

Each experiment folder contains:
- Complete Python simulation code
- Design specifications (JSON)
- Analysis results and metrics
- Optical table diagrams
- Performance evaluation

**Key Finding**: 13 out of 15 experiments preferred FreeSim over QuTiP, demonstrating the value of physics-aware formalism selection.

## ⚙️ Configuration

### API Keys

The system supports multiple LLM providers:

```env
# OpenRouter (recommended - access to multiple models)
OPENAI_API_KEY=sk-or-v1-...

# Direct OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
```

### Optional Features

```env
# Enable web search for finding papers/protocols
ENABLE_WEB_SEARCH=false

# Maximum self-refinement cycles
MAX_REFINEMENT_CYCLES=3

# Simulation timeout (seconds)
SIMULATION_TIMEOUT=120

# Vector database directory
CHROMA_PERSIST_DIRECTORY=./chroma_toolbox
```

## 📊 Usage Examples

### Example 1: Basic Interferometer

**Input:**
```
Design a Mach-Zehnder interferometer with phase control
```

**Output:**
- 8-component optical table
- 2 beam splitters (50:50)
- 2 mirrors
- 1 phase shifter
- 2 detectors
- Automatic beam routing
- Simulation showing complementary interference patterns

### Example 2: Photon Source

**Input:**
```
I need an entangled photon source using spontaneous parametric down-conversion
```

**Output:**
- SPDC crystal with type-II phase matching
- Pump laser preparation
- Polarization optics
- Spatial mode filtering
- Coincidence detection setup
- Validation: Bell state fidelity > 0.95

### Example 3: Learning from Experience

**Input:**
```
Design a Hong-Ou-Mandel setup similar to the previous Bell state generator
```

**Output:**
- System retrieves Bell state design from memory
- Adapts it for HOM geometry
- Reuses validated SPDC configuration
- Adds delay stage for temporal overlap
- Simulates HOM dip visibility

## 🤝 Contributing

Contributions welcome! Areas of interest:

- **New optical components**: Add to `toolbox/primitives.json`
- **Simulation methods**: Extend `freeform_simulation_agent.py`
- **Physics domains**: Beyond photonics (atoms, ions, superconductors)
- **Optimization algorithms**: Genetic algorithms, Bayesian optimization
- **Visualization**: 3D rendering, interactive diagrams

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

This software is provided for research and educational purposes with proper attribution required.

## 🙏 Acknowledgments

**Designed and Developed by S. K. Rithvik**

Built with:
- **OpenAI/Anthropic LLMs** - Natural language understanding
- **QuTiP** - Quantum optics simulation
- **ChromaDB** - Vector storage and semantic search
- **Streamlit** - Interactive web interface
- **BGE-M3** - Multilingual embedding model

Inspired by:
- The quantum optics community
- Open-source scientific computing
- The vision of AI-human collaboration in physics

## 📚 Citation

If you use Aṇubuddhi in your research, please cite:

```bibtex
@software{anubuddhi2025,
  title={Aṇubuddhi: LLM-Powered Quantum Optics Experiment Designer},
  author={Rithvik, S. K.},
  year={2025},
  url={https://github.com/rithvik1122/Anubuddhi},
  note={AI-driven system for conversational quantum experiment design}
}
```

## 📧 Contact

For questions, suggestions, or collaboration:
- GitHub Issues: [https://github.com/rithvik1122/Anubuddhi/issues](https://github.com/rithvik1122/Anubuddhi/issues)
- Discussions: [https://github.com/rithvik1122/Anubuddhi/discussions](https://github.com/rithvik1122/Anubuddhi/discussions)

---

<div align="center">

**Aṇubuddhi** (अणुबुद्धि)  
*Atomic Intelligence for Quantum Discovery*

© 2025 S. K. Rithvik. All rights reserved.

</div>
