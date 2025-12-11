# Dual Simulation System - Integration Complete

## Overview

The Aṇubuddhi system now supports **two parallel simulation approaches**:

1. **QuTiP Simulation** (🔬) - Fast, Fock state-based validation using QuTiP framework
2. **Free-Form Simulation** (🚀) - Physics-aware code generation for experiments beyond Fock states

## Motivation

Analysis of 19 completed experiments revealed:
- 40% of simulation failures due to **fundamental physics mismatch** (temporal, continuous variable, atomic systems)
- 40% due to **implementation bugs** (wrong Bell states, tensor errors, parameter mistakes)
- 20% due to **missing experimental details**

QuTiP is excellent for discrete photonic systems but fundamentally limited for:
- **Temporal physics**: Time-bin entanglement, pulse shaping (Fock states have zero temporal structure)
- **Continuous variables**: Quadrature measurements, homodyne detection (need CV formalism)
- **Atomic systems**: EIT, Rydberg atoms (need atomic master equations)

## Architecture

### Free-Form Simulation Agent (`freeform_simulation_agent.py`)

**Physics Domain Classification:**
- `discrete_photonic` - QuTiP Fock states appropriate
- `temporal` - Requires Gaussian wavepackets, overlap integrals
- `continuous_variable` - Requires displacement/squeeze operators, quadratures
- `atomic` - Requires density matrices, Lindblad master equations
- `hybrid` - Combination of above

**Guided Code Generation:**
- LLM generates Python code based on physics domain
- Includes examples from simulation toolbox (learns over time)
- Built-in warnings from analyzing 19 QuTiP failures:
  - Wrong Bell states: |Φ+⟩ = (|HH⟩+|VV⟩)/√2 NOT (|HH⟩+|VV⟩)/√2
  - Tensor dimension errors
  - Energy non-conservation
  - Unphysical parameter values (e.g., 0.3 photon LO, 68 dB squeezing)
  - Incorrect atomic densities

**Execution & Analysis:**
- Runs generated code in subprocess (30s timeout)
- LLM analyzes results and rates quality 1-10
- Saves successful simulations (rating ≥6) to toolbox for future learning

### UI Integration (`app.py`)

**Dual Button System:**
```
[🔬 QuTiP Sim]  [🚀 Free-Form Sim]  [📦 Download]
```

- **QuTiP button**: Runs traditional Fock state simulation
  - Fast (~5-10 seconds)
  - Limited to discrete photonic systems
  - Stores results in `result['simulation_results']`

- **Free-Form button**: Generates physics-aware code
  - Slower (~20-30 seconds including LLM calls)
  - Handles all physics domains
  - Stores results in `result['freeform_simulation_results']`

**Results Display:**

Both simulation types shown separately with clear labels:

**Free-Form Results:**
- Physics domain classification
- Rating (1-10) with quality label
- Generated code (expandable)
- Execution output or error
- Detailed analysis (physics correctness, limitations, recommendations)

**QuTiP Results:**
- Rating (1-10) with quality label
- Independent assessment (if rating < 7)
- AI interpretation & analysis
- Quantitative metrics
- Improvement recommendations

## Usage

### For Users

1. Design an experiment using the AI designer
2. Click **🔬 QuTiP Sim** for fast Fock state validation
3. If QuTiP gives poor rating, try **🚀 Free-Form Sim** for physics-appropriate code
4. Compare results to understand which approach better captures the physics

### For Developers

**Initialize both agents:**
```python
# In initialize_designer()
llm = SimpleLLM(model="anthropic/claude-sonnet-4.5")
st.session_state.designer = LLMDesigner(llm_client=llm)
st.session_state.freeform_agent = FreeFormSimulationAgent(llm_client=llm)
```

**Run free-form simulation:**
```python
def run_freeform_simulation(design_result):
    agent = st.session_state.freeform_agent
    design = {
        'title': design_result.get('title'),
        'description': design_result.get('description'),
        'physics_explanation': design_result.get('physics_explanation'),
        'components': design_result.get('components_sent_to_renderer'),
    }
    return agent.validate_design(design)
```

## Learning System

The free-form agent builds a **simulation toolbox** over time:

- Successful simulations (rating ≥6) automatically saved
- Organized by physics domain
- Future simulations retrieve relevant examples
- System learns best practices for each domain

**Toolbox location:** `toolbox/simulation_toolbox.json`

**Format:**
```json
{
  "discrete_photonic": {
    "sim_001": {
      "title": "HOM Interference",
      "rating": 8,
      "approach": "Used QuTiP tensor products...",
      "code_snippet": "...",
      "date": "2024-01-15"
    }
  },
  "temporal": { ... },
  "continuous_variable": { ... }
}
```

## Testing Plan

### Phase 1: Failed Experiments (High Priority)

Test on experiments that got POOR ratings with QuTiP:

1. **Franson Interferometer** (temporal physics)
   - QuTiP rating: 2/10 (Fock states have no temporal structure)
   - Expected: Free-form uses Gaussian wavepackets, gets rating ≥6

2. **CV Teleportation** (continuous variables)
   - QuTiP rating: 2/10 (photon counting not appropriate)
   - Expected: Free-form uses quadratures, gets rating ≥6

3. **EIT System** (atomic physics)
   - QuTiP rating: 3/10 (parameter calculation errors)
   - Expected: Free-form uses correct atomic density formulas, gets rating ≥6

4. **Squeezed Light OPO** (CV with unphysical LO)
   - QuTiP rating: 2/10 (0.3 photon LO is nonsense)
   - Expected: Free-form uses 10^6-10^9 photon LO, gets rating ≥6

### Phase 2: Bug-Based Failures (Medium Priority)

Test on experiments with implementation bugs:

5. **GHZ State** (wrong Bell state formula)
6. **Quantum Teleportation** (tensor dimension errors)

### Phase 3: Successful Experiments (Low Priority)

Test on experiments that already got GOOD ratings:
- Should produce similar or better results
- Validates that free-form doesn't degrade performance on easy cases

## Future Enhancements

1. **Comparison Mode**: Run both simulations, show side-by-side comparison
2. **Hybrid Execution**: Use QuTiP where appropriate, free-form for complex parts
3. **Interactive Debugging**: Allow user to modify generated code before execution
4. **Performance Optimization**: Cache successful code patterns for faster generation
5. **Domain-Specific Libraries**: Integrate specialized packages (strawberryfields for CV, ARC for atomic)

## Files Modified

### New Files
- `freeform_simulation_agent.py` (400+ lines) - Complete free-form simulation agent

### Modified Files
- `app.py`:
  - Added import for `FreeFormSimulationAgent` (line 21)
  - Added agent initialization in `initialize_designer()` (line 700)
  - Added `run_freeform_simulation()` helper function (lines 1149-1184)
  - Modified simulation UI to dual button system (lines 1792-1826)
  - Added free-form results display (lines 1990-2055)
  - Added QuTiP results header for clarity (line 2059)

### Future Files
- `toolbox/simulation_toolbox.json` - Will be created on first successful simulation

## Completion Status

✅ **Completed:**
- Free-form simulation agent implementation
- Physics domain classification
- Guided code generation with failure lessons
- Subprocess execution with timeout
- LLM-based quality analysis
- Simulation toolbox learning system
- UI integration with dual buttons
- Results display for both simulation types
- Helper functions and initialization

❌ **Pending:**
- Test on failed experiments
- Populate simulation toolbox
- Update download package to include both simulation codes
- Create comparison mode for side-by-side viewing

## Publication Impact

This dual simulation system addresses a key contribution for the journal article:

**"Design vs Validation Gap"** - Demonstrates that low ratings often reflect simulation framework limitations, not design quality. By providing alternative validation methods, we can:

1. Show that designs are physically sound even when QuTiP gives poor ratings
2. Identify when QuTiP is the wrong tool for the job
3. Build a learning system that accumulates domain-specific simulation expertise
4. Provide transparency by showing generated code, not just black-box results

This strengthens the paper's argument for hierarchical learning and agentic self-improvement.
