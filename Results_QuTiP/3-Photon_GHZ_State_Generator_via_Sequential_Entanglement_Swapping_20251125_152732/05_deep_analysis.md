# Deep Analysis: Design vs Simulation vs Results

**Experiment:** 3-Photon GHZ State Generator via Sequential Entanglement Swapping

**Timestamp:** 20251125_152732

**Quality Rating:** 2/10 (POOR)

---

## Overview

The designer wants to create a 3-photon GHZ state |GHZ⟩ = (|HHH⟩ + |VVV⟩)/√2 using sequential entanglement swapping. Three SPDC sources create polarization Bell pairs, then Bell measurements on shared photons perform entanglement swapping to project the remaining photons into a GHZ state. The simulation code attempts to model this in polarization basis, which is correct, but has a critical structural flaw. The code applies Bell measurement projectors to a 6-mode tensor product state, but the projector construction is fundamentally wrong. The Bell measurement projector 'proj_A2B1' is defined as a 5-mode operator (qt.tensor with 5 arguments) but applied to a 6-mode state, which is mathematically inconsistent. This causes the Bell measurements to fail completely - they don't actually project onto Bell states as intended. The zero fidelity with GHZ state confirms this failure. The high success probability (≈1.0) is meaningless because the projectors aren't working correctly. The final state has entropy 0.693 (log 2), indicating it's a maximally mixed 2-level system, not an entangled 3-photon state. The simulation completely fails to capture the entanglement swapping physics.

## Key Insight

Bell measurement projectors must match the dimensionality of the full state space - this simulation fails due to basic tensor algebra errors.

## Design Intent

**Components:**
- Three 405nm pump lasers for SPDC sources
- Three BBO crystals for type-II SPDC creating Bell pairs (A1,A2), (B1,B2), (C1,C2)
- Bell state measurements on (A2,B1) and (B2,C1) for entanglement swapping
- Polarization analysis on remaining photons A1, B2, C2 to verify GHZ state

**Physics Goal:** Generate genuine 3-photon GHZ state |GHZ⟩ = (|HHH⟩ + |VVV⟩)/√2 via sequential entanglement swapping

**Key Parameters:**
- wavelength: 810nm (SPDC output)
- type-II phase matching for polarization entanglement
- Sequential Bell measurements for swapping

## QuTiP Implementation

### State Init

```python
# Creates three separate Bell pairs
bell_state_single = (qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 1)) + 
                    qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 0))).unit()
psi_initial = qt.tensor(bell_state_single, bell_state_single, bell_state_single)
```

### Operations

```python
# Bell measurement projectors (INCORRECT DIMENSIONALITY)
proj_A2B1 = qt.tensor(qt.qeye(cutoff_dim),           # mode 0 (A1)
                     phi_plus.proj(),                 # modes 1,2 (A2,B1) 
                     qt.qeye(cutoff_dim),           # mode 3 (B2)
                     qt.qeye(cutoff_dim),           # mode 4 (C1)
                     qt.qeye(cutoff_dim))           # mode 5 (C2)
psi_after_bell1 = proj_A2B1 * psi_initial
```

### Measurements

```python
# Fidelity calculation with target GHZ
target_ghz = (qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 0)) + 
             qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1))).unit()
fidelity = float(abs(qt.fidelity(rho_final, target_rho)))
```

## How Design Maps to Code

The design intent is physically sound - entanglement swapping can indeed create GHZ states. However, the code implementation has a fatal flaw: Bell measurement projectors are constructed as 5-mode operators but applied to 6-mode states. The projector 'proj_A2B1' should project modes 1 and 2 onto a Bell state while leaving other modes untouched, but the tensor product structure is wrong. This causes the Bell measurements to fail completely, explaining why the final fidelity with GHZ is zero. The simulation doesn't validate the design because it doesn't correctly implement the core physics operation (Bell state measurements).

## Identified Limitations

- Incorrect tensor product structure for Bell measurement projectors
- No modeling of spatial mode matching required for Bell measurements
- No temporal synchronization between photons from different sources
- Missing wavepacket indistinguishability requirements for interference
- No modeling of collection efficiency and mode overlap
- Ignores phase relationships between different SPDC sources

## Recommendations

1. Debug the entanglement swapping protocol - the Bell measurement outcomes may not be properly conditioning the final state
2. Verify the initial SPDC states are correctly prepared and that photon routing between sources is implemented correctly
3. Check phase relationships and timing synchronization between the three SPDC sources, as phase mismatches can destroy GHZ state coherence

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
