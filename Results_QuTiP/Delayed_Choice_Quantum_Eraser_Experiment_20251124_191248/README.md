# Quantum Experiment Package

**Experiment:** Delayed Choice Quantum Eraser Experiment

**Generated:** 20251124_191248

**Description:** Demonstrates retroactive erasure of which-path information using entangled photons and delayed measurement choices.

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

Type-II SPDC creates entangled photon pairs with orthogonal polarizations. Signal photons pass through a double-slit with polarizers positioned after each slit aperture that create which-path information by marking photons with distinct polarizations, destroying interference. Idler photons travel through a long delay line to ensure their measurement occurs after signal detection. The delayed choice measurement on the idler photon either preserves path information or erases it using diagonal polarizers that cannot distinguish the original H/V markings, retroactively determining whether interference fringes appear in the signal beam coincidence data.

## Expected Outcome

Coincidence counts between signal detector and either eraser detector will show interference fringes because both eraser measurements use diagonal polarizers that cannot distinguish between the original H/V path markings, effectively erasing the which-path information. The delayed choice of measuring the idler photon in the diagonal basis retroactively restores the interference pattern that was destroyed by the polarizers after the double slit.
