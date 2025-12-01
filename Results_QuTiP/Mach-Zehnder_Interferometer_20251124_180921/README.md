# Quantum Experiment Package

**Experiment:** Mach-Zehnder Interferometer

**Generated:** 20251124_180921

**Description:** Demonstrates quantum superposition and interference by splitting coherent light into two paths and recombining them to create interference fringes.

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

Coherent laser light is split into two paths by the input beam splitter, creating quantum superposition |ψ⟩ = (|upper⟩ + |lower⟩)/√2. The phase shifter introduces controllable phase difference φ between paths. At the output beam splitter, the paths recombine and interfere, producing intensity oscillations I ∝ 1 + cos(φ) that demonstrate wave-particle duality and quantum interference.

## Expected Outcome

Sinusoidal interference fringes as phase is scanned, with 100% visibility for perfect coherence. Detectors show complementary oscillations: when one detector sees maximum intensity, the other sees minimum, demonstrating energy conservation and quantum interference.
