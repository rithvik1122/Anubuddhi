# Quantum Experiment Package

**Experiment:** BB84 Quantum Key Distribution Setup

**Generated:** 20251125_181531

**Description:** Implements the BB84 protocol for secure quantum key distribution using polarization-encoded single photons

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

Alice prepares single photons in one of four polarization states (H, V, D, A) by first ensuring horizontal polarization, then rotating with a motorized half-wave plate to encode both basis choice and bit value. The photons travel through a quantum channel to Bob, who independently randomly selects his measurement basis using his own HWP before the PBS performs polarization measurement. When bases match (50% probability), Bob's measurement perfectly correlates with Alice's bit due to quantum state projection. The no-cloning theorem ensures any eavesdropper introduces detectable errors. After transmission, Alice and Bob publicly compare bases via classical channel, keep matching results (sifted key), estimate QBER to detect eavesdropping, then perform error correction and privacy amplification to generate a provably secure shared key.

## Expected Outcome

After transmitting approximately 1 million photons, Alice and Bob publicly compare their basis choices via authenticated classical channel and retain approximately 50% where bases matched (sifted key of ~500k bits). If QBER < 11%, indicating no significant eavesdropping, they perform error correction to create identical bit strings, then privacy amplification to distill a provably secure shared secret key of ~100k-200k bits. Any eavesdropping attempt increases QBER above threshold, alerting them to abort. The final key achieves information-theoretic security guaranteed by quantum mechanics for one-time-pad encryption or other cryptographic applications.
