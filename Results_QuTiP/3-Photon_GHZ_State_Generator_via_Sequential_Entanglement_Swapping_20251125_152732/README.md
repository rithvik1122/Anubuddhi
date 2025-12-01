# Quantum Experiment Package

**Experiment:** 3-Photon GHZ State Generator via Sequential Entanglement Swapping

**Generated:** 20251125_152732

**Description:** Generates genuine 3-photon GHZ states by performing sequential Bell state measurements on shared photons from three independent SPDC sources to create tripartite entanglement through quantum swapping

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

Three independent SPDC sources create Bell pairs (A1,A2), (B1,B2), and (C1,C2). Sequential Bell state measurements on the shared photons (A2,B1) at Bell PBS 1 and (B2,C1) at Bell PBS 2 perform entanglement swapping, projecting the remaining photons A1, B2, C2 into a genuine 3-photon GHZ state |GHZ⟩ = (|HHH⟩ + |VVV⟩)/√2. The Bell measurement outcomes determine which local unitary operations are needed to obtain the desired GHZ state.

## Expected Outcome

Successful Bell state measurements on shared photons herald generation of 3-photon GHZ states. Triple coincidence measurements on the remaining photons show correlations violating Mermin's inequality, confirming genuine tripartite entanglement with visibility >70%.
