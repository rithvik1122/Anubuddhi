# Quantum Experiment Package

**Experiment:** Hyperentangled Photon Source with Polarization and Time-Bin Entanglement

**Generated:** 20251126_112153

**Description:** Generates photon pairs entangled in both polarization and time-bin degrees of freedom using Type-II SPDC with independent Mach-Zehnder interferometers for each photon

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

Type-II SPDC creates polarization-entangled photon pairs in the state |ψ⟩_pol = (|HV⟩ + |VH⟩)/√2. A PBS separates H and V photons into distinct spatial channels, each entering its own unbalanced Mach-Zehnder interferometer. The path length difference in each MZ creates time-bin entanglement: |ψ⟩_time = (|early,late⟩ + |late,early⟩)/√2, where photon arrival times are correlated. The total state is hyperentangled: |Ψ⟩ = |ψ⟩_pol ⊗ |ψ⟩_time, providing entanglement in two independent degrees of freedom. Four-fold coincidence measurements with high timing resolution verify both polarization correlations (via PBS analysis) and temporal correlations (via arrival time statistics).

## Expected Outcome

Four-fold coincidence measurements reveal correlations in both polarization and time-bin degrees of freedom. Polarization correlations show anti-correlation (when A detects H, B detects V and vice versa), confirming the |HV⟩ + |VH⟩ entanglement with visibility >90%. Time-bin correlations show bunching when both photons take the same path length (both early or both late), creating the time-bin entangled state |early,late⟩ + |late,early⟩ with high visibility. The hyperentangled state enables violation of Bell inequalities in a 4-dimensional Hilbert space (2×2 from polarization and time-bin), demonstrating quantum correlations stronger than any 2D entanglement alone. Adjusting MZ path lengths allows control over time-bin coherence, while PBS angles control polarization measurement basis.
