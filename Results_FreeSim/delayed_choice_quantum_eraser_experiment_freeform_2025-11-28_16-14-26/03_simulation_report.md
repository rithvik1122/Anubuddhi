# Simulation Report: Delayed Choice Quantum Eraser Experiment

## Overall Assessment
**Quality Rating:** 6/10 | **Verdict:** FAIR

---

## Simulation Output

### Console Output
```
======================================================================
DELAYED CHOICE QUANTUM ERASER SIMULATION
======================================================================

Simulating 10000 entangled photon pairs...
  Processed 2000/10000 pairs...
  Processed 4000/10000 pairs...
  Processed 6000/10000 pairs...
  Processed 8000/10000 pairs...
  Processed 10000/10000 pairs...

Simulation complete!

======================================================================
RESULTS
======================================================================

Total Counts:
  D0 (signal detector): 4286
  D0-D1 coincidences (which-path A): 1129
  D0-D2 coincidences (which-path B): 1047
  D0-D3 coincidences (erased): 1045
  D0-D4 coincidences (erased): 1065

Interference Visibility:
  D0-D1 (which-path A): 0.3267
  D0-D2 (which-path B): 0.2619
  D0-D3 (erased): 0.9698
  D0-D4 (erased): 0.9754
  D0 total (no post-selection): 0.1567

Plot saved as 'delayed_choice_quantum_eraser.png'

Simulation complete.
```

---

## Physics Analysis

### Physics Correctness
The simulation captures the conceptual framework of the delayed choice quantum eraser but has critical physics errors. The main issue is in how which-path information is handled: D0-D1 and D0-D2 coincidences show non-zero visibility (0.33 and 0.26) when they should show NO interference pattern at all - these represent cases where which-path information is available. The code incorrectly uses single-slit diffraction patterns (signal_prob_a and signal_prob_b) for which-path cases, when it should use the incoherent sum of probabilities from both slits since entanglement correlation doesn't preserve coherence at the individual detector level. The erased cases (D3/D4) correctly show high visibility (~0.97), which is physically appropriate. The beam splitter logic is conceptually reasonable but the phase relationships at the eraser BS need more careful treatment.

### Implementation Quality
Code structure is well-organized with clear class hierarchy and separation of concerns. Good use of dataclasses for parameters and precomputation for efficiency. The single-slit diffraction calculation using sinc functions is properly implemented. However, there are issues: (1) No validation that BS transmittance + reflectance = 1, (2) Normalization of amplitudes is done independently for each slit which loses relative phase information needed for proper interference, (3) The visibility calculation uses Gaussian smoothing which may artificially enhance or reduce measured visibility, (4) No error bars or statistical uncertainty quantification despite being a Monte Carlo simulation.

### Results Validity
The count statistics are reasonable - approximately equal distribution across the four idler detectors as expected from the 50/50 beam splitters. Total detection efficiency (~43%) is consistent with the 0.65 detector efficiency and beam splitter losses. However, the key physics signature is wrong: D0-D1 and D0-D2 should show visibility ≈ 0 (no fringes), not 0.33 and 0.26. The high visibility for D3/D4 (>0.96) is correct. The D0 total visibility of 0.16 makes sense as the incoherent sum of all cases. The numbers are self-consistent but don't match the actual quantum eraser physics for which-path cases.

### Key Findings
- Critical error: Which-path cases (D0-D1, D0-D2) show interference visibility of 0.33 and 0.26 when they should be near zero
- Erased cases (D0-D3, D0-D4) correctly show high visibility (~0.97) with complementary phase relationships
- Total D0 pattern correctly shows low visibility (0.16) representing incoherent mixture
- Detection statistics and count distributions are internally consistent with beam splitter probabilities
- The fundamental issue is using coherent single-slit amplitudes for which-path cases instead of incoherent probability distributions

### Limitations
- Does not properly model the loss of coherence when which-path information is available - uses wrong probability distributions for D1/D2 cases
- Amplitude normalization is performed independently for each slit, losing the relative phase needed for proper two-slit interference
- No treatment of spatial coherence length or temporal coherence effects from the SPDC source
- Visibility calculation uses smoothing which may not reflect true experimental visibility
- No statistical error analysis or confidence intervals on measured visibilities
- Assumes perfect momentum correlation without modeling realistic SPDC phase matching bandwidth
- Does not account for potential timing jitter effects beyond the coincidence window parameter

### Recommendations for Improvement
- Study the Kim et al. (2000) Physical Review Letters paper on the quantum eraser to understand the correct probability distributions
- Implement proper density matrix formalism to handle mixed states when which-path information is available
- Add statistical error bars using sqrt(N) counting statistics and bootstrap methods for visibility uncertainty
- Consider validating against analytical predictions for fringe spacing and visibility in each coincidence channel

---

## Design Alignment

This simulation was designed to model:
> Type-II SPDC creates momentum-entangled signal-idler photon pairs. Signal photons pass through a double slit creating spatial superposition, while idler photons propagate along two distinct paths (A or B) correlated with which slit the signal photon passed through due to momentum conservation. Each idler path encounters a beam splitter: BS_A and BS_B allow direct transmission to D1 and D2 (preserving which-path information), or reflection toward BS_Eraser where paths A and B interfere quantum mechanically before detection at D3 or D4 (erasing which-path information). Coincidence counting between D0 and idler detectors retroactively determines whether interference appears at D0, demonstrating complementarity and delayed choice since the erasure decision occurs after signal detection.

The simulation partially captures the intended quantum physics.

---

*Report generated by Anubuddhi Free-Form Simulation System*
