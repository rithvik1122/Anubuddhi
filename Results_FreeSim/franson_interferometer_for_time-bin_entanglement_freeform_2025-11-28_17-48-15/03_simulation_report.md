# Simulation Report: Franson Interferometer for Time-Bin Entanglement

## Overall Assessment
**Quality Rating:** 6/10 | **Verdict:** FAIR

---

## Simulation Output

### Console Output
```
======================================================================
FRANSON INTERFEROMETER SIMULATION
Energy-Time Entanglement via Time-Bin Encoding
======================================================================

EXPERIMENTAL PARAMETERS:
  Pump wavelength: 405.0 nm
  Signal/Idler wavelength: 810.0 nm
  Pump power: 50.0 mW
  Pump linewidth: 1000.0 Hz
  Path length difference: 30.0 mm
  Time delay: 100.0 ps
  Photon coherence time: 1.0 ps
  Pump coherence time: 1.0 ms
  Coincidence window: 2.0 ns

FRANSON CONDITIONS:
  Δt > τ_photon: True (no single-photon interference)
  Δt < τ_pump: True (entanglement preserved)
  Δt < coincidence window: True (can detect coincidences)

SPDC pair generation rate: 1.02e+06 pairs/s

TIME-BIN STRUCTURE:
  Early time-bin: t = 0
  Late time-bin: t = 100.0 ps
  Temporal separation: 100.0 × τ_photon

SIMULATION: Single-Photon Measurements

Scanning φ_S for signal photon alone:
  Maximum count rate: 2.55e+05 counts/s
  Minimum count rate: 2.55e+05 counts/s
  Visibility: 0.0000
  Expected: ~0 (no single-photon interference)

SIMULATION: Two-Photon Interference

Case 1: Scanning φ_S (signal phase) with φ_I = 0
  Maximum coincidence rate: 2.17e+05 counts/s
  Minimum coincidence rate: 3.75e+04 counts/s
  Visibility: 0.7059

Case 2: Scanning φ_I (idler phase) with φ_S = 0
  Maximum coincidence rate: 2.17e+05 counts/s
  Minimum coincidence rate: 3.75e+04 counts/s
  Visibility: 0.7059

Case 3: Scanning φ_S + φ_I (sum phase)
  Maximum coincidence rate: 2.17e+05 counts/s
  Minimum coincidence rate: 3.75e+04 counts/s
  Visibility: 0.7059

Case 4: 2D scan of (φ_S, φ_I)
  2D scan completed: 25x25 points

BELL INEQUALITY VIOLATION (CHSH Test)

  Measurement settings:
    a = 0.0000, a' = 1.5708
    b = -0.7854, b' = 0.7854

  Correlation values:
    E(a,b) = -0.8839
    E(a,b') = -0.8839
    E(a',b) = -0.8839
    E(a',b') = -1.2374

  CHSH parameter S = 2.1213
  Classical bound: S ≤ 2
  Quantum maximum: S ≤ 2√2 ≈ 2.828
  Violation: True
  Number of standard deviations above classical: 1.2σ

SINGLE-PHOTON INTERFERENCE CHECK:

  Individual photon coherence time: 1.0 ps
  Path delay Δt: 100.0 ps
  Ratio Δt/τ_photon: 100.0

  Single-photon visibility (measured): 0.0000
  Expected single-photon visibility: ~0 (no interference)
  Two-photon visibility (measured): 0.7059
  Expected two-photon visibility: 1/√2 ≈ 0.707

======================================================================
SUMMARY OF RESULTS
======================================================================

Time-bin entangled state: |ψ⟩ = (|EE⟩ + e^(iφ)|LL⟩)/√2

Single-photon visibility: 0.0000
Two-photon interference visibility: 0.7059
Expected visibility (ideal): 1/√2 ≈ 0.707

CHSH parameter S: 2.1213
Bell inequality violated: True

PHYSICAL INTERPRETATION:
  - Individual photons show NO interference (Δt >> τ_photon)
  - Coincidence counts show QUANTUM interference
  - Interference only appears in φ_S + φ_I (sum phase)
  - Violation of Bell inequality confirms energy-time entanglement
  - Cannot be explained by local hidden variable theory

ENTANGLEMENT WITNESS:

  Concurrence: 1.0000
  Entanglement (yes/no): True
  Maximally entangled: True

  Fidelity with |Φ+⟩ = (|EE⟩ + |LL⟩)/√2: 1.0000

======================================================================
EXPERIMENTAL VERIFICATION:
======================================================================

To verify energy-time entanglement experimentally:
  1. Measure single-photon count rates (should be constant vs phase)
  2. Measure coincidence rates vs (φ_S, φ_I)
  3. Extract visibility from coincidence fringes
  4. Verify visibility ≈ 0.707 (Franson limit)
  5. Perform CHSH measurements at optimal angles
  6. Verify S > 2 (Bell inequality violation)

Expected coincidence rate: 1.29e+05 counts/s
Integration time for 3σ violation: ~0.0 s

======================================================================
SIMULATION COMPLETE
======================================================================
```

---

## Physics Analysis

### Physics Correctness
The simulation captures the conceptual framework of Franson interferometry correctly: time-bin entanglement with |ψ⟩ = (|EE⟩ + e^(iφ)|LL⟩)/√2, the key condition that Δt >> τ_photon prevents single-photon interference while Δt << τ_pump preserves entanglement, and the characteristic visibility of 1/√2 ≈ 0.707. However, there are critical physics errors: (1) The coincidence probability formula P = (1/2)[1 + V*cos(φ_S + φ_I)] only depends on the sum phase, which is correct for Franson, but the implementation doesn't properly account for the fact that interference arises from indistinguishable paths (early-early vs late-late). (2) The CHSH calculation has a fundamental flaw: all four correlation values E(a,b), E(a,b'), E(a',b) should depend on DIFFERENT phase combinations, but the code structure suggests they're being computed with the same functional form. (3) The S value of 2.1213 is suspiciously close to √2 * 1.5, suggesting the CHSH optimization isn't finding the maximum S = 2√2 achievable with ideal Franson visibility. (4) The photon coherence time of 1 ps is unrealistically short for 810nm SPDC photons with THz bandwidth—typical values are 100s of fs to few ps depending on phase matching bandwidth.

### Implementation Quality
Code is well-structured with clear sections, good documentation, and appropriate physical constants. The parameter validation checks (Franson conditions) are excellent. However, there are implementation issues: (1) The measure_single_photon() function correctly returns constant P=0.5, but the 'photon' parameter is unused—this is fine but could be cleaner. (2) The create_timebin_state() function creates a 4-element state vector but only uses elements 0 and 3 (|EE⟩ and |LL⟩), with elements 1 and 2 (|EL⟩ and |LE⟩) always zero. This is physically correct for energy conservation but the phi_global parameter is never varied, making the function unnecessarily complex. (3) The measure_coincidences() function hardcodes visibility_franson = 1/√2 inside, which is correct but doesn't allow for imperfections. (4) The CHSH correlation function measure_correlation() performs normalization that may not correctly map coincidence probabilities to the [-1,+1] correlation range required for CHSH. (5) No error handling for division by zero in visibility calculations. (6) The pair_rate calculation divides by '1000' with no explanation—this appears arbitrary.

### Results Validity
Most results are physically reasonable: zero single-photon visibility (0.0000) correctly shows no first-order interference, two-photon visibility of 0.7059 matches the theoretical Franson limit of 1/√2 ≈ 0.7071 within rounding error, and the pair generation rate of ~10^6 pairs/s is plausible for 50mW pump at 10^-6 efficiency. However, critical issues: (1) CHSH parameter S = 2.1213 is below the maximum achievable value of 2√2 ≈ 2.828 for ideal Franson visibility—with V = 0.707, the maximum S should be 2√2 * 0.707 ≈ 2.0, so S = 2.12 actually exceeds what's possible with this visibility, indicating an error in the correlation calculation. (2) The correlation values show E(a,b) = E(a,b') = E(a',b) = -0.8839, meaning three of the four measurements give identical results, which is unphysical—different measurement settings should yield different correlations. (3) Integration time calculation '~0.0 s' is clearly wrong, suggesting a division issue. (4) The claim of '1.2σ' significance for Bell violation is meaningless without proper statistical modeling of photon counting noise.

### Key Findings
- Successfully implements time-bin entanglement concept with correct state structure |ψ⟩ = (|EE⟩ + e^(iφ)|LL⟩)/√2
- Correctly demonstrates zero single-photon interference (visibility = 0.0000) when Δt >> τ_photon
- Achieves correct Franson visibility of 0.7059 ≈ 1/√2 in two-photon coincidences
- Proper validation of Franson conditions: Δt > τ_photon, Δt < τ_pump, Δt < coincidence window
- CHSH calculation shows Bell violation (S = 2.12 > 2) but with incorrect correlation structure

### Limitations
- CHSH correlation function produces identical values for three different measurement settings, indicating fundamental error in how phase-dependent correlations are computed
- CHSH parameter S = 2.1213 exceeds theoretical maximum for V = 0.707, suggesting normalization error in correlation calculation
- No modeling of realistic imperfections: detector dark counts, accidental coincidences, timing jitter, or finite pump coherence effects
- Photon coherence time (1 ps) may be too long for THz-bandwidth SPDC—typical values are 100s of femtoseconds
- Statistical analysis is absent: no photon counting noise, no error bars, no proper significance calculation for Bell violation
- The phi_global parameter in state creation is never varied, missing potential physics of pump phase fluctuations

### Recommendations for Improvement
- Study the original Franson paper (PRL 62, 2205, 1989) and modern implementations to understand how two-photon interference arises from path indistinguishability
- For CHSH tests with energy-time entanglement, review Tapster et al. (PRL 73, 1923, 1994) for proper correlation measurements
- Add realistic noise modeling: Poissonian photon statistics, accidental coincidences ∝ (single rate)² × coincidence window, detector dark counts
- Consider finite pump coherence time effects on visibility degradation when Δt approaches τ_pump

---

## Design Alignment

This simulation was designed to model:
> The 405nm pump creates entangled photon pairs at 810nm via Type-II SPDC in PPLN crystal, with energy-time entanglement where the pair creation time is quantum mechanically uncertain. The PBS separator uses orthogonal polarizations from Type-II SPDC to spatially separate signal and idler photons into upper and lower paths. Each photon enters an unbalanced Mach-Zehnder interferometer with path length difference ΔL creating a time delay Δt = ΔL/c. When Δt exceeds the photon coherence time but is less than the pump coherence time, individual photons show no interference, but coincidence counts exhibit two-photon interference fringes as phases φ_S and φ_I are varied, violating the CHSH inequality and confirming energy-time entanglement in the state |ψ⟩ = (|early,early⟩ + e^(iφ)|late,late⟩)/√2. The detectors convert photon arrivals to electronic signals that feed into the coincidence counter for correlation analysis.

The simulation partially captures the intended quantum physics.

---

*Report generated by AgenticQuantum Free-Form Simulation System*
