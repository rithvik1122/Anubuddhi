# Quantum Experiment Package

**Experiment:** Unbalanced Mach-Zehnder Interferometer with Path Length Control

**Generated:** 20251122_143822

**Description:** Demonstrates quantum interference using asymmetric arm lengths and variable delay for fringe visibility control.

---

## Package Contents

1. `01_optical_setup.png` - High-resolution diagram (300 DPI)
2. `02_component_selection.md` - Component justifications
3. `03_qutip_simulation.py` - Python simulation code
4. `04_design_components.json` - Complete design specification
5. `05_deep_analysis.md` - Detailed analysis report
6. `README.md` - This file

---

## Quick Start

```bash
# Run the simulation
python 03_qutip_simulation.py
```

## Physics

Coherent laser light splits into superposition state at input beam splitter, creating |ψ⟩ = (|upper⟩ + |lower⟩)/√2. The asymmetric path design with longer lower arm and variable delay stage allows precise control of relative phase φ between arms. At recombination, interference produces output intensities I₁,₂ = I₀(1 ± cos(φ))/2, demonstrating wave-particle duality and phase-dependent quantum interference.

## Expected Outcome

Sinusoidal interference fringes as delay stage scans, with complementary intensity oscillations at both detectors and fringe visibility approaching unity for good alignment.
