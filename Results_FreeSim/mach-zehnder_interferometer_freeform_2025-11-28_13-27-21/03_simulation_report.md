# Simulation Report: Mach-Zehnder Interferometer

## Overall Assessment
**Quality Rating:** 6/10 | **Verdict:** FAIR

---

## Simulation Output

### Console Output
```
============================================================
MACH-ZEHNDER INTERFEROMETER SIMULATION
============================================================

Input Parameters:
  Wavelength: 632.8 nm
  Laser power: 5.0 mW
  Photon flux: 1.59e+16 photons/s
  Photon energy: 3.14e-19 J

After BS1:
  Upper arm amplitude: 8.92e+07
  Lower arm amplitude: 8.92e+07
  Upper arm phase: 0.000 rad
  Lower arm phase: 1.571 rad

============================================================
INTERFERENCE RESULTS
============================================================

Detector 1 (Transmission Port):
  Maximum intensity: 1.34e+16 photons/s
  Minimum intensity: 0.00e+00 photons/s
  Visibility: 1.0000

Detector 2 (Reflection Port):
  Maximum intensity: 1.34e+16 photons/s
  Minimum intensity: 3.37e+12 photons/s
  Visibility: 0.9995

Complementarity Check:
  Total intensity variation: 5.03e-16
  (Should be ~0 for ideal complementary outputs)

Theoretical vs Simulated (Detector 1):
  Expected max (approx): 6.70e+15 photons/s
  Simulated max: 1.34e+16 photons/s

Interference Pattern Analysis:
  At φ=0: D1=0.00e+00, D2=1.34e+16
  At φ=π: D1=1.34e+16, D2=3.37e+12
  Ratio D1(0)/D1(π): 0.00

Energy Conservation:
  Input photon rate: 1.59e+16 photons/s
  Average output rate: 1.34e+16 photons/s
  Expected (with losses): 6.63e+15 photons/s
  Conservation ratio: 0.8415

============================================================
PHYSICAL VALIDITY CHECKS
============================================================
  Visibility in valid range [0,1]: True
  Intensities non-negative: True
  Complementary behavior: True
  Energy conserved (within losses): False

Plot saved as 'mach_zehnder_interference.png'

============================================================
SIMULATION COMPLETE
============================================================
```

### Generated Figures
This simulation produced 1 figure(s). See visualizations below.

---

## Physics Analysis

### Physics Correctness
The simulation correctly models quantum interference in a Mach-Zehnder interferometer with proper beam splitter matrices and phase evolution. However, there's a critical error: the beam splitter matrix convention is inconsistent. The code uses a symmetric matrix [[1, i], [i, 1]]/√2, but applies it twice (at BS1 and BS2) which doesn't preserve the standard MZI behavior. A 50/50 beam splitter should map input state [a,b] to [(a+ib)/√2, (ia+b)/√2]. The double application with the same matrix creates unexpected phase relationships. The visibility of 1.0 at detector 1 with minimum intensity exactly zero suggests perfect destructive interference, which is correct for an ideal lossless MZI, but the energy conservation check fails because the code doesn't properly account for how losses should be applied.

### Implementation Quality
Code is well-structured with clear sections, good documentation, and comprehensive output. The use of numpy for quantum state operations is appropriate. However, there are logical issues: (1) Mirror losses are applied to amplitudes before the phase scan loop, but this creates a single fixed loss rather than properly modeling the interferometer, (2) The 'expected_max' calculation is incorrect - it doesn't match the actual beam splitter transformation, (3) Energy conservation validation uses wrong expected values, (4) No error handling for division by zero in visibility calculation when intensities might be zero.

### Results Validity
The complementary interference patterns are physically correct (I1 + I2 = constant), and visibility values are in the valid [0,1] range. However, several red flags: (1) The energy conservation ratio of 0.8415 fails the simulation's own validity check (0.3-0.6 range), suggesting the expected value calculation is wrong, (2) Detector 1 shows minimum intensity of exactly 0.00e+00, which is suspicious - with 2% mirror losses, perfect destructive interference shouldn't occur, (3) The 'expected_max' value (6.70e+15) is exactly half the simulated max (1.34e+16), indicating a factor-of-2 error in the theoretical prediction, (4) At φ=0, D1 should be maximum for the standard MZI convention, but the simulation shows it's zero - this suggests the phase convention or beam splitter matrix needs review.

### Key Findings
- Correctly implements quantum interference with complex amplitudes and proper visibility calculation
- Successfully demonstrates complementary behavior with total intensity variation ~5e-16
- Achieves near-perfect visibility (>0.999) consistent with low-loss interferometer
- Properly uses beam splitter transformation matrices for quantum state evolution

### Limitations
- Energy conservation check fails due to incorrect theoretical prediction formula
- Mirror losses applied incorrectly - should account for both mirrors in each arm and the round-trip
- Perfect destructive interference (I_min = 0) is unphysical given 1% mirror losses per reflection
- Beam splitter convention may not match standard MZI textbook treatment
- No consideration of coherence length or temporal effects despite linewidth parameter being defined
- Detector efficiency applied inconsistently - should affect energy conservation calculation

### Recommendations for Improvement
- Verify beam splitter matrix convention against standard quantum optics references (e.g., Gerry & Knight)
- Recalculate expected output intensities accounting for all losses: 2 mirrors × 2 beam splitters × detector efficiency
- Add validation that minimum intensity with realistic losses should be small but non-zero
- Include uncertainty analysis or shot noise effects given the photon flux is calculated

---

## Design Alignment

This simulation was designed to model:
> A coherent laser beam is split into two paths by BS1, creating a superposition state |ψ⟩ = (|upper⟩ + |lower⟩)/√2. The upper arm includes a phase shifter that introduces a relative phase φ between the arms. At BS2, the paths recombine and interfere, with the output intensities at the two detectors varying as I₁ ∝ (1 + cos φ) and I₂ ∝ (1 - cos φ), demonstrating complementary interference patterns. This setup is fundamental for testing quantum coherence, measuring refractive indices, and implementing quantum gates.

The simulation partially captures the intended quantum physics.

---

*Report generated by Anubuddhi Free-Form Simulation System*
