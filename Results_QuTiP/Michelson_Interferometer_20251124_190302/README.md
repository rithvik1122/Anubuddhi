# Quantum Experiment Package

**Experiment:** Michelson Interferometer

**Generated:** 20251124_190302

**Description:** Creates interference fringes by splitting a coherent beam into two perpendicular arms and recombining them to measure phase differences.

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

Coherent laser light is split into two perpendicular arms by a 50:50 beam splitter. Each beam reflects from a mirror and returns to the beam splitter where they interfere. The relative phase between the arms depends on the optical path difference, creating constructive or destructive interference patterns. Moving one mirror changes the path length and shifts the fringe pattern.

## Expected Outcome

Circular or linear interference fringes appear on the screen, with fringe spacing λ/2 per mirror displacement. Moving the piezo mirror causes fringes to shift, demonstrating phase sensitivity to path length changes on the order of the wavelength.
