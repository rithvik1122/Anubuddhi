# Quantum Experiment Package

**Experiment:** 4-Photon Boson Sampling Experiment

**Generated:** 20251125_185800

**Description:** Demonstrates quantum computational advantage by interfering 4 indistinguishable photons through a 4-mode linear optical network and measuring output statistics

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

Two SPDC sources generate four heralded single photons at 810nm that are coupled into single-mode fibers to ensure spatial and temporal indistinguishability. Each photon pair is split by input beam splitters to populate all four input modes of a linear optical network. The network consists of three layers of beam splitters with programmable phase shifters that implement a random unitary transformation U. Quantum interference causes the photons to evolve according to the permanent of the 4×4 matrix U, a computation that is classically intractable. Superconducting nanowire detectors measure all four output modes, and coincidence logic identifies 4-photon events, producing a probability distribution that validates quantum computational advantage.

## Expected Outcome

The measured 4-photon output distribution will show characteristic boson bunching patterns that match the permanent of the network's 4×4 unitary matrix. Certain output configurations will have enhanced or suppressed probabilities compared to distinguishable particles. The distribution cannot be efficiently simulated classically, demonstrating quantum computational advantage. Validation involves comparing measured statistics with permanent calculations for the implemented unitary transformation.
