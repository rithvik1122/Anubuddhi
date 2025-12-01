# Component Selection Rationale

**Experiment:** Quantum Teleportation Experiment

**Timestamp:** 20251125_155500

**Description:** Demonstrates quantum teleportation by transferring an unknown quantum state from one photon to another using entanglement and classical communication.

---

## 1. State Preparation Laser

Creates photon A in a well-defined polarization state that will be transformed into the unknown state to be teleported

## 2. Initial Polarizer

Establishes a horizontal polarization reference state for subsequent manipulation

## 3. State Preparation QWP

Converts the horizontal state into an arbitrary superposition |ψ⟩ = α|H⟩ + β|V⟩ representing the unknown quantum state

## 4. Entanglement Pump Laser

405nm pump laser provides the energy for SPDC to generate the entangled photon pair B and C

## 5. Entanglement BBO Crystal

Type-II SPDC source creating maximally entangled Bell state |Φ+⟩ = (|HH⟩ + |VV⟩)/√2 between photons B and C

## 6. Idler Steering Mirror

Directs idler photon C toward the teleportation output path for final state analysis

## 7. Signal Steering Mirror

Directs signal photon B toward the Bell state measurement region

## 8. State Redirection Mirror

Redirects photon A from the state preparation path to interfere with photon B at the Bell state analyzer

## 9. BSA HWP

Half-wave plate that enables complete Bell state discrimination by rotating polarization basis before the PBS

## 10. Bell State Analyzer PBS

Polarizing beam splitter that performs the crucial Bell state measurement on photons A and B by separating H and V polarizations

## 11. BSA Detector H

SPAD detector measuring horizontally polarized photons from the Bell state analyzer

## 12. BSA Detector V

SPAD detector measuring vertically polarized photons, completing the Bell measurement to identify which Bell state was projected

## 13. Teleportation Mirror 1

Steers teleported photon C toward the correction optics for Pauli gate application

## 14. Teleportation Mirror 2

Final steering of photon C to align with the correction wave plates

## 15. Correction HWP

Programmable half-wave plate that applies σx or σz Pauli corrections based on Bell measurement outcome

## 16. Correction QWP

Programmable quarter-wave plate that applies σy Pauli correction when combined with HWP rotations

## 17. Analysis Polarizer

Analyzes the final polarization state of the corrected teleported photon to verify successful state transfer

## 18. Teleportation Detector

SPAD detector that measures the successfully teleported and corrected quantum state

## 19. 3-Fold Coincidence Unit

Electronic system that identifies valid teleportation events by detecting three-fold coincidences between both Bell detectors and the teleportation detector

## 20. Classical Communication

Real-time communication system that transmits Bell measurement results to control the correction wave plate orientations within the coherence time

