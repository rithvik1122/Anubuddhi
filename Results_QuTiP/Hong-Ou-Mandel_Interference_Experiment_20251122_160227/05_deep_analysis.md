# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Hong-Ou-Mandel Interference Experiment

**Timestamp:** 20251122_160227

**Quality Rating:** 7/10 (GOOD)

---

## Overview

The designer wants to demonstrate Hong-Ou-Mandel interference where two identical photons from SPDC enter a 50:50 beam splitter and bunch together due to quantum interference, producing zero coincidence counts. The simulation code correctly models the quantum mechanical aspects of HOM interference using Fock states and proper beam splitter operations. However, it makes a critical simplification: it assumes PERFECT indistinguishability by working directly with the two-photon Fock state |1,1⟩ and setting delay_phase = 0. Real HOM interference depends on temporal wavepacket overlap - photons must arrive simultaneously with overlapping temporal profiles. The simulation cannot capture this temporal physics because Fock states have no time dependence. Despite this limitation, the results (zero coincidence probability, equal bunching probabilities of ~0.325 each after detector efficiency, perfect visibility) are exactly what's expected for ideal HOM interference. The simulation validates the quantum interference mechanism but cannot test the experimental parameters (delay stage, spectral filtering) that ensure indistinguishability in practice.

## Key Insight

Simulation correctly predicts ideal HOM interference results but cannot validate the experimental parameters needed to achieve photon indistinguishability.

## Design Intent

**Components:**
- 405nm pump laser for SPDC photon pair generation
- PPLN crystal with type-I phase matching for identical polarizations
- Variable delay stage for temporal control
- 810nm bandpass filters for spectral matching
- 50:50 beam splitter for interference
- Two SPADs for coincidence detection

**Physics Goal:** Demonstrate quantum interference where identical photons bunch together at beam splitter, producing zero coincidence counts and proving bosonic behavior

**Key Parameters:**
- wavelength: 405nm pump → 810nm signal/idler
- filter_bandwidth: 10nm
- bs_transmittance: 0.5
- detector_efficiency: 0.65

## QuTiP Implementation

### State Init

```python
# Creates two-photon Fock state directly
vacuum = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 0))
two_photon = qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1))
state = (np.sqrt(1 - spdc_amplitude**2) * vacuum + spdc_amplitude * two_photon).unit()
```

### Operations

```python
# Beam splitter unitary operation
theta_bs = np.pi/4
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()
state_after_bs = (U_bs * two_photon).unit()
```

### Measurements

```python
# Proper projection operators for detection
coincidence_state = qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1))
coincidence_op = coincidence_state * coincidence_state.dag()
prob_coincidence = float(abs(qt.expect(coincidence_op, state_after_bs)))
both_a_state = qt.tensor(qt.fock(cutoff_dim, 2), qt.fock(cutoff_dim, 0))
both_a_op = both_a_state * both_a_state.dag()
prob_both_a = float(abs(qt.expect(both_a_op, state_after_bs)))
```

## How Design Maps to Code

The design relies on experimental control of photon distinguishability through delay and spectral filtering, but the simulation assumes perfect indistinguishability from the start. The code correctly implements the quantum interference mathematics but skips the physics of how indistinguishability is achieved. The beam splitter operation and detection measurements are properly modeled, giving textbook-perfect HOM results that validate the interference concept but not the experimental implementation.

## Identified Limitations

- Fock states have no temporal structure - cannot model photon arrival time differences
- Delay stage modeled as phase shift has no effect on Fock state distinguishability
- Spectral filtering modeled only as amplitude reduction, not bandwidth effects
- Cannot simulate the transition from distinguishable to indistinguishable photons
- No modeling of pump laser coherence or SPDC bandwidth matching

## Recommendations

1. Consider adding realistic temporal distinguishability effects to model non-ideal photon sources
2. Include detector dark counts and timing jitter for more realistic experimental conditions
3. Implement variable photon distinguishability parameter to study transition from classical to quantum behavior

## Conclusion

✅ Simulation successfully captured the design's intended physics.
