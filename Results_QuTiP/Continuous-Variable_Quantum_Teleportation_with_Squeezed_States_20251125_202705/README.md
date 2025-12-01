# Quantum Experiment Package

**Experiment:** Continuous-Variable Quantum Teleportation with Squeezed States

**Generated:** 20251125_202705

**Description:** Teleports coherent state quantum information using EPR-entangled squeezed vacuum beams and homodyne detection with feedforward correction

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

Two OPA crystals pumped by the same laser with a 90-degree phase difference generate EPR-entangled squeezed vacuum modes with orthogonal squeezing orientations, creating quantum correlations in position and momentum quadratures. Alice performs a joint Bell measurement on the input coherent state and her EPR mode using two homodyne detectors measuring X and P quadratures. The measurement results are processed by classical feedforward electronics and sent to Bob, who applies displacement operations to his EPR mode. This reconstructs the input state at Bob's location with fidelity exceeding the classical limit of 0.5, demonstrating quantum teleportation of continuous-variable states.

## Expected Outcome

Teleportation fidelity F > 0.5 (classical limit) is achieved, with F approaching 2/3 for infinite squeezing. With 10dB squeezing, expect F ≈ 0.58-0.62. Quadrature correlation measurements show X_out = X_in and P_out = P_in within quantum noise limits determined by EPR entanglement quality. The EPR variance V_EPR = ΔX_A·ΔP_B < 1 confirms entanglement resource. Scanning the output homodyne phase reconstructs the Wigner function of the teleported state, demonstrating faithful transfer of quantum coherence and verifying that Bob's output state matches Alice's input state.
