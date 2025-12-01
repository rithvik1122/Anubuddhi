# Quantum Experiment Package

**Experiment:** Quantum Teleportation Experiment

**Generated:** 20251125_155500

**Description:** Demonstrates quantum teleportation by transferring an unknown quantum state from one photon to another using entanglement and classical communication.

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

An unknown quantum state |ψ⟩ = α|H⟩ + β|V⟩ is prepared on photon A using the state preparation laser and wave plate. Simultaneously, entangled photons B and C are created via SPDC in the |Φ+⟩ = (|HH⟩ + |VV⟩)/√2 Bell state. A Bell state measurement on photons A and B at the polarizing beam splitter projects their joint state, which instantaneously transforms photon C into the original state |ψ⟩ up to a known Pauli operation. Classical communication of the Bell measurement outcome enables real-time correction of photon C using programmable wave plates, completing the faithful teleportation of the unknown quantum state.

## Expected Outcome

Triple coincidence events between the Bell state detectors and teleportation detector will demonstrate quantum teleportation with fidelity exceeding the classical limit of 2/3. The correction operations ensure that regardless of which Bell state was measured, the teleported photon C faithfully reproduces the original unknown state |ψ⟩, confirming genuine quantum state transfer without classical information about the original state.
