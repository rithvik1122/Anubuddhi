# Quantum Experiment Package

**Experiment:** Bell State Generator using SPDC

**Generated:** 20251123_132334

**Description:** Generates polarization-entangled photon pairs in Bell states through type-II spontaneous parametric down-conversion with proper pump blocking and phase control.

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

A 405nm pump laser undergoes type-II SPDC in a BBO crystal, creating entangled photon pairs at 810nm with orthogonal polarizations in the state |ψ⟩ = (|H⟩₁|V⟩₂ + e^(iφ)|V⟩₁|H⟩₂)/√2. The half-wave plate controls the relative phase φ between the two components, enabling generation of different Bell states. The polarizing beam splitter separates the orthogonally polarized photons into different spatial modes, while adjustable polarizers enable measurement in different polarization bases for Bell inequality tests.

## Expected Outcome

Coincidence counts between detectors will show strong correlation when polarizers are parallel and anti-correlation when perpendicular, violating Bell inequalities with visibility >85% confirming quantum entanglement. Half-wave plate rotation enables generation of all four Bell states.
