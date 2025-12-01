# Component Selection Rationale

**Experiment:** Continuous-Variable Quantum Teleportation with Squeezed States

**Timestamp:** 20251125_202705

**Description:** Teleports coherent state quantum information using EPR-entangled squeezed vacuum beams and homodyne detection with feedforward correction

---

## 1. 1064nm Master Laser

Provides coherent pump light for both OPA crystals, ensuring the generated squeezed modes share phase coherence necessary for EPR entanglement

## 2. Main BS

Splits pump laser to simultaneously drive both OPA crystals with identical phase reference, crucial for creating correlated squeezed states

## 3. OPA Phase B

Introduces 90-degree phase shift to OPA Crystal B pump beam, creating orthogonal squeezing orientation (P-squeezed) relative to Crystal A (X-squeezed), essential for EPR entanglement with ΔX_A·ΔP_B < 1

## 4. OPA Crystal A

Optical parametric amplifier generating position-squeezed vacuum (Alice's EPR mode) through degenerate down-conversion below threshold

## 5. OPA Crystal B

Second OPA generating momentum-squeezed vacuum (Bob's EPR mode) with 90-degree phase offset from Crystal A, creating orthogonal squeezing for proper EPR correlations

## 6. Mirror A1

Directs Alice's squeezed mode toward EPR beam splitter

## 7. Mirror B1

Directs Bob's squeezed mode toward EPR beam splitter

## 8. EPR BS

Creates EPR entanglement by mixing the two orthogonally-squeezed vacuum modes, producing position-momentum entangled beams with ΔX_A·ΔP_B < 1

## 9. Alice EPR Mirror

Routes Alice's EPR mode toward Bell measurement beam splitter where it will interfere with the input state

## 10. Bob EPR Mirror

Directs Bob's EPR mode to await feedforward displacement corrections based on Alice's measurement results

## 11. Input State Laser

Generates weak coherent state |α⟩ to be teleported, encoding quantum information in quadrature amplitudes

## 12. State Modulator

Encodes information onto the input coherent state by modulating its quadratures to create the unknown state to be teleported

## 13. Bell Measurement BS

Combines Alice's EPR mode with the input state for joint measurement, projecting onto Bell-like basis in continuous-variable phase space

## 14. Homodyne X

Measures position quadrature (X) of the combined Alice-input mode, providing first classical measurement result for feedforward

## 15. Homodyne P

Measures momentum quadrature (P) of the combined Alice-input mode, providing complementary measurement result orthogonal to X

## 16. LO Splitter

Divides local oscillator beam from master laser to provide phase references for all three homodyne detectors

## 17. LO Mirror 1

Routes local oscillator beam along bottom of optical table toward homodyne detection regions

## 18. LO Mirror 2

Continues local oscillator path distribution to all three homodyne detectors

## 19. LO BS X

Mixes local oscillator with signal beam for Homodyne X detector, enabling interference-based quadrature measurement

## 20. LO Phase X

Sets measurement quadrature angle for X measurement (0 degrees) by controlling relative phase between LO and signal

## 21. LO Mirror X

Delivers phase-adjusted local oscillator to Homodyne X detector

## 22. LO BS P

Mixes local oscillator with signal beam for Homodyne P detector

## 23. LO Phase P

Sets measurement quadrature angle for P measurement (90 degrees, orthogonal to X) for complementary quadrature measurement

## 24. LO Mirror P

Delivers phase-adjusted local oscillator to Homodyne P detector

## 25. Bob Mirror 1

Routes Bob's EPR mode to displacement modulators where feedforward corrections will be applied

## 26. Displacement X

Applies position displacement to Bob's mode based on Alice's X measurement result, controlled by classical feedforward electronics

## 27. Displacement P

Applies momentum displacement to Bob's mode based on Alice's P measurement result, completing the teleportation protocol

## 28. Output Verification

Homodyne detector to verify teleportation fidelity by measuring quadratures of the reconstructed state and comparing to input

## 29. LO BS Out

Provides local oscillator for output verification homodyne detector

## 30. LO Phase Out

Allows scanning of measurement quadrature to fully characterize the teleported state and reconstruct its Wigner function

