# Quantum Experiment Package

**Experiment:** Bell State Generator using Spontaneous Parametric Down-Conversion

**Generated:** 20251124_184403

**Description:** Generates maximally entangled photon pairs in Bell states using Type-II SPDC in a BBO crystal with proper beam separation and polarization analysis.

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

A 405nm pump laser undergoes Type-II SPDC in a BBO crystal, generating entangled photon pairs at 810nm where one photon has horizontal polarization and the other vertical. The crystal creates the Bell state |ψ⟩ = (|H⟩A|V⟩B + |V⟩A|H⟩B)/√2 due to conservation laws. Mirrors separate the SPDC cone into distinct spatial paths, and polarizers at 45° project both photons onto the same diagonal basis, enabling violation of Bell inequalities through coincidence measurements.

## Expected Outcome

Coincidence detection rates will show strong correlations violating classical limits, with visibility >70% confirming Bell state entanglement when polarizers are rotated through different angles for Bell inequality tests.
