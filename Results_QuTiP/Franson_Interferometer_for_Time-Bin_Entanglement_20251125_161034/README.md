# Quantum Experiment Package

**Experiment:** Franson Interferometer for Time-Bin Entanglement

**Generated:** 20251125_161034

**Description:** Demonstrates energy-time entanglement using unbalanced Mach-Zehnder interferometers in both photon paths with time-bin encoded states

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

SPDC creates entangled photon pairs in a superposition of being created at early or late times. The PBS separates orthogonally polarized signal and idler photons into different spatial paths. Each photon passes through an unbalanced Mach-Zehnder interferometer with path length difference ΔL much longer than the coherence length, erasing individual photon interference. However, the time-bin entangled state |ψ⟩ = (|early,early⟩ + e^(iφ)|late,late⟩)/√2 produces two-photon interference visible only in coincidence measurements when both interferometer phase differences are scanned. The narrow-band filters (coherence time > ΔL/c) ensure indistinguishability of the early and late emission times, enabling violation of Bell inequalities and demonstrating energy-time entanglement through the Franson interference pattern.

## Expected Outcome

When scanning both phase shifters, coincidence counts show sinusoidal interference pattern with visibility V > 70% (ideally approaching 1/√2 ≈ 71% for maximally entangled state). Single detector counts show no interference (flat). Maximum coincidences occur when φ_S + φ_I = 0, minimum at φ_S + φ_I = π. Violation of Bell inequality (S > 2) confirms energy-time entanglement. The path length difference should be ~30cm (1ns delay), much longer than pump coherence length (~300μm) but shorter than filtered photon coherence length (~100mm with 3nm filter).
