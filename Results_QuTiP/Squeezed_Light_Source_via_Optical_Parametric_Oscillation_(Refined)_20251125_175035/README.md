# Quantum Experiment Package

**Experiment:** Squeezed Light Source via Optical Parametric Oscillation (Refined)

**Generated:** 20251125_175035

**Description:** Generates quadrature-squeezed vacuum states using a sub-threshold optical parametric oscillator with impedance-matched cavity, PDH locking, and phase-coherent local oscillator

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

A 1064nm seed laser is frequency-doubled to 532nm pump, ensuring phase coherence between pump and local oscillator. The pump drives a sub-threshold PPLN-based OPO cavity (impedance-matched with Input Coupler R=99.8% matched to M1 R=99.8% + losses). Degenerate parametric down-conversion generates squeezed vacuum at 1064nm with reduced quantum noise in one quadrature. The phase-coherent LO interferes with squeezed output at a 50:50 beam splitter, and balanced homodyne detection measures quadrature noise below the shot-noise limit. PDH locking stabilizes the OPO cavity resonance, while precision temperature control maintains PPLN phase-matching.

## Expected Outcome

Spectrum analyzer shows noise power reduced 3-10 dB below shot-noise level in the squeezed quadrature (typically amplitude-squeezed), while orthogonal quadrature shows corresponding anti-squeezing. Squeezing bandwidth ~10-100 MHz limited by cavity linewidth. Rotating HWP2 by 45° exchanges squeezed and anti-squeezed quadratures. Temperature drift of PPLN causes loss of squeezing, demonstrating need for active stabilization. PDH lock maintains cavity resonance with <1 Hz linewidth.
