# Free-Form Simulation Package

**Experiment:** Mach-Zehnder Interferometer
**Generated:** 2025-11-28_13-27-21
**Simulation Mode:** AI-Generated Free-Form Python

---

## Package Contents

1. `01_freeform_simulation.py` - AI-generated Python simulation code
2. `02_execution_output.txt` - Complete simulation output (text)
3. `03_simulation_report.md` - Comprehensive analysis report
4. `04_analysis_results.json` - Full analysis data (JSON format)
5. `05_metrics_summary.md` - Key metrics for paper writing
6. `06_design_specification.json` - Complete design specification with numbered components
7. `07_optical_setup.png` - Optical diagram (300 DPI)
8. `08_iteration_history.md` - Refinement iteration log (if applicable)
9. `figures/` - All generated matplotlib figures from simulation
10. `README.md` - This file

---

## Quick Start

```bash
# Install dependencies (if needed)
pip install numpy scipy qutip matplotlib

# Run the simulation
python 01_freeform_simulation.py
```

---

## Simulation Report

The `03_simulation_report.md` file contains:
- Complete simulation output
- All generated figures (1 figure(s))
- LLM analysis of physics correctness
- Design alignment assessment
- Key findings and recommendations

This report combines the simulation results with AI-powered analysis to help you understand:
- Whether the simulation accurately models the designed experiment
- Physics correctness and validity of results
- Suggestions for improvement

---

## Experiment Description

Two-path interferometer that splits a coherent beam into two arms and recombines them to create interference fringes sensitive to phase differences

---

## Physics Background

A coherent laser beam is split into two paths by BS1, creating a superposition state |ψ⟩ = (|upper⟩ + |lower⟩)/√2. The upper arm includes a phase shifter that introduces a relative phase φ between the arms. At BS2, the paths recombine and interfere, with the output intensities at the two detectors varying as I₁ ∝ (1 + cos φ) and I₂ ∝ (1 - cos φ), demonstrating complementary interference patterns. This setup is fundamental for testing quantum coherence, measuring refractive indices, and implementing quantum gates.

---

## Design Alignment Assessment

**Alignment Score:** 9/10
**Converged:** Yes (in 1 iteration(s))

---

## For Paper Writing

See `04_metrics_summary.md` for:
- Token usage statistics
- Convergence metrics
- Design alignment scores
- Physics correctness assessment
- Missing/incorrect elements analysis

---

## Citation

If you use this in your research, please cite:

```
Anubuddhi: AI-Driven Quantum Experiment Design
[Citation details to be added]
```
