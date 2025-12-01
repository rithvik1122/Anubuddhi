# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Hong-Ou-Mandel Interference Setup

**Timestamp:** 20251124_182846

**Quality Rating:** 4/10 (FAIR)

---

## Overview

The designer wants to demonstrate Hong-Ou-Mandel interference where two indistinguishable photons from Type-II SPDC bunch together at a beam splitter, showing perfect quantum interference. The simulation code attempts to model this but has several critical issues. First, it starts with a proper Type-II SPDC state |HV⟩ + |VV⟩ but then makes a fatal simplification - it assumes the half-wave plates perfectly align both photons to the same polarization without properly modeling the polarization rotation operators. More critically, the code reduces the problem to spatial modes only, completely ignoring that real HOM interference depends on temporal and spectral indistinguishability of photon wavepackets. Fock states |1⟩|1⟩ have no temporal structure, so the simulation cannot capture the key physics of wavepacket overlap that makes HOM interference possible. The results show perfect bunching (100% visibility, zero anti-bunching) which is the idealized textbook result, but this doesn't validate whether the actual experimental setup would achieve this. The coincidence values of ~2 are unphysical (should be probabilities ≤1), indicating normalization issues. While the beam splitter operator is correctly implemented, the simulation fundamentally cannot address whether the photons from the two arms will actually be temporally synchronized and spectrally matched when they reach the beam splitter.

## Key Insight

The simulation shows idealized HOM results but cannot validate the critical temporal synchronization that determines real experimental success.

## Design Intent

**Components:**
- PPLN Crystal: Type-II SPDC generating orthogonally polarized photon pairs
- PBS: Separates photon pairs by polarization into two spatial arms
- HWPs at 22.5°: Rotate polarizations to make photons indistinguishable
- Delay stages: Enable temporal synchronization of photon arrival
- 50:50 BS: Recombine photons for quantum interference measurement

**Physics Goal:** Demonstrate Hong-Ou-Mandel interference showing photon bunching when indistinguishable photons interfere at a beam splitter

**Key Parameters:**
- pump_wavelength: 405nm
- signal/idler_wavelength: 810nm
- hwp_angle: 22.5°
- bs_transmittance: 0.5

## QuTiP Implementation

### State Init

```python
# Type-II SPDC state creation
hv_state = qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 0),
                     qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 1))
vh_state = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 1),
                     qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 0))
spdc_state = (1/np.sqrt(2)) * (hv_state + vh_state)
```

### Operations

```python
# Beam splitter operation
theta_bs = np.pi/4  # 50:50 beam splitter
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()
state_after_bs = U_bs * spatial_state
```

### Measurements

```python
# Detection measurements
n_a = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_b = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))
coincidence_aa = float(abs(qt.expect(n_a * n_a, state_after_bs)))
coincidence_bb = float(abs(qt.expect(n_b * n_b, state_after_bs)))
coincidence_ab = float(abs(qt.expect(n_a * n_b, state_after_bs)))
```

## How Design Maps to Code

The design intent includes sophisticated polarization control and temporal synchronization through delay stages, but the code implementation bypasses these critical elements. The code jumps from SPDC state creation directly to an oversimplified 'both photons are H-polarized' assumption, completely skipping the PBS routing logic and HWP rotation operators. Most critically, the design includes delay stages specifically for temporal synchronization, but the code works in the Fock state basis which has no temporal dimension. The experimental success depends on whether the delay stages can actually synchronize photon arrival times, but the simulation cannot validate this key requirement.

## Identified Limitations

- Fock states have no temporal structure - cannot model wavepacket overlap timing
- Missing proper polarization rotation operators for HWP analysis
- No spectral distinguishability modeling (bandwidth, coherence)
- Oversimplified PBS operation - doesn't track spatial mode routing
- No path length differences or timing synchronization physics
- Unphysical coincidence normalization (values >1)

## Recommendations

1. Introduce realistic experimental imperfections (partial distinguishability, detector efficiency <100%) to make the simulation more representative of actual experiments
2. Add timing jitter and spectral filtering effects to model real-world photon sources and detection systems
3. Implement variable photon distinguishability parameter to study the transition from classical to quantum interference

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
