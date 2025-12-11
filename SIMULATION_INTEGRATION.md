# LLM-Driven Quantum Simulation Integration

## Overview
Aṇubuddhi now includes an **LLM-powered simulation agent** that automatically validates designs using QuTiP (Quantum Toolbox in Python). The LLM:
- Generates simulation code based on the optical design
- Executes QuTiP simulations safely
- Interprets results and judges success
- Provides recommendations for improvement

## Installation

### Install QuTiP
```bash
conda activate agentic-quantum
pip install qutip
```

QuTiP is a comprehensive framework for quantum mechanics simulations with support for:
- Fock states, coherent states, squeezed states
- Quantum operators (beam splitters, phase shifts, etc.)
- Time evolution and master equations
- Entanglement measures and fidelity calculations

## How It Works

### 1. **LLM Analyzes Design**
```
User designs: "EIT experiment with rubidium atoms"
      ↓
LLM examines components, physics, parameters
      ↓
Decides what quantum states and operations to simulate
```

### 2. **LLM Generates QuTiP Code**
The LLM writes executable Python code:
```python
import qutip as qt
import numpy as np

# Create quantum states
probe_state = qt.coherent(5, 0.5)  # Weak probe
control_state = qt.coherent(5, 5.0)  # Strong control

# Simulate EIT Hamiltonian
# ... physics simulation ...

# Calculate metrics
fidelity = qt.fidelity(final_state, target_state)
transparency = calculate_transmission(final_state)

results = {
    'fidelity': float(fidelity),
    'transparency': float(transparency),
    'probe_absorption': absorption_coefficient
}
```

### 3. **Safe Execution**
Code runs in isolated environment with:
- Limited scope (only QuTiP, NumPy allowed)
- Timeout protection
- Error handling
- Output capture

### 4. **LLM Interprets Results**
```
Simulation Output: {'fidelity': 0.94, 'transparency': 0.88}
      ↓
LLM Analysis:
"VERDICT: GOOD (85% confidence)
The simulation shows excellent EIT effect with 88% transparency.
Fidelity of 0.94 indicates quantum coherence is well preserved.
Recommendation: Increase control beam power for 95%+ transparency."
```

## UI Integration

### New Simulation Tab
Access simulation results in the **🔬 Simulation** tab:
- **Verdict**: EXCELLENT / GOOD / ACCEPTABLE / POOR / FAILED
- **Confidence**: LLM's confidence in assessment (0-100%)
- **AI Analysis**: Detailed interpretation of results
- **Key Metrics**: Fidelity, purity, visibility, entanglement, etc.
- **Recommendations**: Specific suggestions to improve design
- **Simulation Code**: View the generated QuTiP code
- **Reasoning**: Why the LLM chose this simulation approach

### Example Output
```
🟢 Verdict: GOOD
Confidence: 85%

🧠 AI Analysis:
The simulation demonstrates strong quantum interference with 92% visibility 
in the Hong-Ou-Mandel dip. Fidelity to the target entangled state is 0.91, 
indicating good two-photon interference. The design should work well for 
quantum entanglement demonstrations.

📊 Key Metrics:
- fidelity: 0.910
- visibility: 0.920
- purity: 0.880

💡 Recommendations:
1. Add phase stabilization for long-term visibility
2. Use single-mode fibers to reduce spatial mode mismatch
3. Consider temperature-stabilized mounts for beam splitter
```

## Architecture

```
User Request
     ↓
LLMDesigner.design_experiment()
     ↓
[Generate Design]
     ↓
SimulationAgent.validate_design()
     ↓
┌─────────────────────────┐
│ 1. LLM Generates Code   │
│ 2. Execute Safely       │
│ 3. LLM Interprets       │
└─────────────────────────┘
     ↓
Design + Simulation Results
     ↓
Display in UI (Simulation Tab)
```

## Benefits

### 1. **Automatic Validation**
Every design is checked through actual quantum simulation - catch physics errors before building!

### 2. **LLM as Tool-User**
The LLM knows HOW to use QuTiP - it's not just generating text, it's writing and executing code.

### 3. **Interpretable Results**
Raw simulation numbers are translated into actionable insights by the LLM.

### 4. **Iterative Improvement**
Recommendations feed back into design refinement.

### 5. **Educational**
See the simulation code - learn how professionals model quantum systems.

## Example Scenarios

### Scenario 1: Hong-Ou-Mandel Interferometer
```
Design: Two-photon interference at beam splitter
Simulation: QuTiP models Fock states |1,1⟩ → |2,0⟩ or |0,2⟩
Verdict: EXCELLENT (96% confidence)
Key Metric: visibility = 0.98
```

### Scenario 2: SPDC State Engineering
```
Design: Parametric down-conversion for entangled photons
Simulation: QuTiP models type-II SPDC with crystal parameters
Verdict: GOOD (82% confidence)
Key Metric: concurrence = 0.89
Recommendation: Increase pump power for higher pair rate
```

### Scenario 3: Quantum Teleportation
```
Design: Complete teleportation protocol with Bell measurement
Simulation: QuTiP tracks state evolution through protocol
Verdict: ACCEPTABLE (70% confidence)
Key Metric: teleportation_fidelity = 0.82
Recommendation: Add error correction for >90% fidelity
```

## Limitations

1. **Complex Dynamics**: Very complicated experiments may be hard to simulate accurately
2. **LLM Code Quality**: Generated code may occasionally have bugs (caught by error handling)
3. **Computational Cost**: Large Hilbert spaces slow down simulations
4. **API Calls**: Each simulation requires 2 LLM calls (generation + interpretation)

## Future Enhancements

- [ ] **Visual Plots**: Show Wigner functions, Q-functions, photon statistics
- [ ] **Parameter Sweeps**: Automatically explore design space
- [ ] **Comparison Mode**: Simulate multiple designs side-by-side
- [ ] **Real-Time Feedback**: Stream simulation progress
- [ ] **Cached Simulations**: Store results for similar designs
- [ ] **User Feedback Loop**: "Was this simulation accurate?" → improve LLM

## Technical Details

### Files
- `simulation_agent.py`: Main simulation agent class
- `llm_designer.py`: Integration into design workflow
- `app.py`: UI display of simulation results

### Key Methods
```python
class SimulationAgent:
    def validate_design(design) -> Dict
        # Main entry point - returns full validation results
    
    def _generate_simulation_code(design) -> (code, reasoning)
        # LLM writes QuTiP code
    
    def _execute_simulation(code) -> (success, results, error)
        # Safely run code and extract results
    
    def _interpret_results(design, results) -> Dict
        # LLM judges success and provides analysis
```

### Safety Features
- Sandboxed execution (limited global scope)
- No file I/O allowed
- Timeout protection (prevents infinite loops)
- Exception handling with detailed error messages

## Usage

### Automatic (Default)
Simulations run automatically after every design! Just use Aṇubuddhi normally.

### Manual Check
```python
from simulation_agent import SimulationAgent
from agentic_quantum.llm import SimpleLLM

llm = SimpleLLM()
sim = SimulationAgent(llm)

results = sim.validate_design(my_design)
print(results['verdict'])  # EXCELLENT / GOOD / etc.
```

### Quick Check (No Simulation)
```python
assessment = sim.quick_check(design)
# "Missing: Wavelength filter for pump suppression"
```

## Conclusion

By putting the **LLM in charge of simulations**, Aṇubuddhi can:
- Validate physics automatically
- Provide quantitative performance estimates
- Suggest improvements based on simulation results
- Teach users how to model quantum systems

This is true **agentic AI** - the LLM uses tools (QuTiP) to accomplish goals (validate designs) autonomously!
