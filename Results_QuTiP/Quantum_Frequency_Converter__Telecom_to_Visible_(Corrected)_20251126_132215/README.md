# Quantum Experiment Package

**Experiment:** Quantum Frequency Converter: Telecom to Visible (Corrected)

**Generated:** 20251126_132215

**Description:** Converts single photons from telecom wavelength (1550nm) to visible wavelength (600.4nm) via sum-frequency generation while preserving quantum properties

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

Single telecom photons at 1550nm are combined with a strong 980nm pump laser in a PPLN crystal where sum-frequency generation occurs. Energy conservation dictates that the output wavelength must be 600.4nm (1/λ_out = 1/1550 + 1/980). The nonlinear interaction preserves quantum coherence and photon statistics while upconverting to a wavelength where silicon detectors have high efficiency. Quasi-phase-matching in PPLN with appropriate poling period (~19.2μm) and temperature control ensures efficient conversion.

## Expected Outcome

Single telecom photons are efficiently converted to 600.4nm orange-light photons with conversion efficiency of 30-60% while preserving quantum statistics (sub-Poissonian photon number distribution, g^(2)(0) < 1). The APD will detect single photons with high signal-to-noise ratio, enabling quantum communication protocols with visible-wavelength detectors. Coincidence measurements between heralding detector and APD will confirm preservation of quantum correlations through the frequency conversion process.
