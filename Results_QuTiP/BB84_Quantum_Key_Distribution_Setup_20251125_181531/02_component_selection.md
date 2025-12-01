# Component Selection Rationale

**Experiment:** BB84 Quantum Key Distribution Setup

**Timestamp:** 20251125_181531

**Description:** Implements the BB84 protocol for secure quantum key distribution using polarization-encoded single photons

---

## 1. Polarized Laser

810nm laser source provides coherent polarized light that will be attenuated to single-photon level for quantum state preparation

## 2. Alice Input Polarizer

Ensures all photons start in well-defined horizontal polarization state before attenuation and encoding - critical for state preparation fidelity

## 3. Variable Attenuator

Reduces mean photon number to μ < 0.1 per pulse after polarization to approximate single-photon states and prevent photon-number-splitting attacks

## 4. Alice State Encoder

Motorized half-wave plate encodes all four BB84 states - HWP at 0° gives H, 45° gives V, 22.5° gives D, 67.5° gives A polarization

## 5. Alice Fiber Output

Couples prepared single photons into single-mode fiber for quantum channel transmission with high efficiency

## 6. Quantum Channel

10km single-mode fiber transmits quantum states from Alice to Bob with inherent loss but no measurement - the insecure channel where eavesdropping could occur

## 7. Bob Fiber Input

Receives photons from quantum channel and couples them into free-space measurement apparatus for basis selection and detection

## 8. Bob Basis Selector

Motorized HWP randomly switched between 0° (rectilinear basis measurement H/V) and 22.5° (diagonal basis measurement D/A) for random basis choice

## 9. Bob PBS

Polarizing beam splitter performs polarization measurement - transmits one polarization component to Detector 0 and reflects orthogonal component to Detector 1

## 10. Bob Detector 0

SPAD measures transmitted photons (H in rectilinear basis or D in diagonal basis) corresponding to bit 0 with high efficiency and low dark counts

## 11. Bob Detector 1

SPAD measures reflected photons (V in rectilinear basis or A in diagonal basis) corresponding to bit 1 - second detector enables unambiguous bit determination

