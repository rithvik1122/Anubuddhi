# Quantum Experiment Package

**Experiment:** Electromagnetically Induced Transparency (EIT) in Warm Rubidium Vapor

**Generated:** 20251126_124851

**Description:** Demonstrates quantum interference effect where a strong coupling laser makes an opaque atomic vapor transparent to a weak probe laser through coherent population trapping

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

EIT occurs in a Lambda-type three-level system where two ground hyperfine states (|1⟩ and |2⟩) couple to an excited state (|3⟩) in Rb-87. The weak probe laser (795nm, |1⟩→|3⟩ transition) is normally absorbed, but a strong coupling laser (780nm, |2⟩→|3⟩ transition) creates quantum interference between excitation pathways, inducing coherent population trapping in a dark state |D⟩ = (Ω_c|1⟩ - Ω_p|2⟩)/√(Ω_c² + Ω_p²). When the two-photon resonance condition is satisfied (probe detuning plus coupling detuning equals ground state hyperfine splitting), destructive interference eliminates absorption, creating a narrow transparency window with steep dispersion that enables slow light propagation.

## Expected Outcome

As probe frequency is scanned across the atomic resonance, transmission initially shows strong absorption (optical depth 2-4). When two-photon resonance condition is satisfied (probe-coupling detuning matches 6.8 GHz ground state hyperfine splitting), a narrow transparency window appears with transmission increasing to 60-90% of incident probe power. The EIT linewidth is typically 1-10 MHz (much narrower than natural linewidth of 6 MHz), determined by coupling laser Rabi frequency Ω_c and decoherence rates. The transparency window is accompanied by steep normal dispersion, reducing group velocity to ~1000 m/s or less. Varying coupling laser power shows EIT width scales as √(I_coupling), confirming Autler-Townes splitting interpretation and demonstrating quantum coherence and interference in atomic systems.
