# Quantum Experiment Package

**Experiment:** Hong-Ou-Mandel Interference Setup

**Generated:** 20251124_182846

**Description:** Demonstrates quantum interference of indistinguishable photons at a beam splitter, showing the quantum bunching effect.

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

A pump laser generates orthogonally polarized photon pairs via type-II SPDC in a PPLN crystal. The PBS separates the pairs by polarization into upper and lower interferometer arms. Half-wave plates rotate both photons to the same polarization, making them indistinguishable. When these indistinguishable photons interfere at the 50:50 beam splitter, quantum interference causes photon bunching - they preferentially exit together from the same output port rather than separating.

## Expected Outcome

When the delay stages achieve perfect temporal overlap and the half-wave plates make photons indistinguishable, coincidence counts between detectors drop to near zero (HOM dip), demonstrating quantum interference. The visibility of this dip depends on photon indistinguishability. Scanning the delay reveals the characteristic dip width related to photon coherence time, typically showing >90% visibility for high-quality SPDC sources.
