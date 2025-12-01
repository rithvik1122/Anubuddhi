# Quantum Experiment Package

**Experiment:** Hong-Ou-Mandel Interference Experiment

**Generated:** 20251122_160227

**Description:** Demonstrates quantum interference between indistinguishable photons at a beam splitter, showing photon bunching.

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

A pump laser creates photon pairs via type-I SPDC in a PPLN crystal with identical polarizations, making them naturally indistinguishable. The photons are separated into two arms with variable delay control and spectral filtering to enhance indistinguishability. When these identical photons arrive simultaneously at the beam splitter, quantum interference causes them to bunch together and exit from the same output port, resulting in zero coincidence counts and demonstrating bosonic behavior.

## Expected Outcome

A characteristic Hong-Ou-Mandel dip in coincidence counts as a function of delay, with minimum coincidences when photons arrive simultaneously. The visibility of the dip indicates the degree of photon indistinguishability, reaching up to 100% for ideal single photons, demonstrating the quantum nature of light and bosonic bunching behavior.
