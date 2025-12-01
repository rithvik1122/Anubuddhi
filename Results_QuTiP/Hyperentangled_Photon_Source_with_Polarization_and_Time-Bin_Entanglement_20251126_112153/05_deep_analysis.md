# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Hyperentangled Photon Source with Polarization and Time-Bin Entanglement

**Timestamp:** 20251126_112153

**Quality Rating:** 2/10 (POOR)

---

## Overview

**CRITICAL PHYSICS MISMATCH: Time-bin entanglement fundamentally cannot be modeled in Fock state basis**

**1. What the designer wanted:**
The designer proposed a hyperentangled photon source with entanglement in TWO independent degrees of freedom:
- **Polarization entanglement**: Type-II SPDC creates |ψ⟩_pol = (|HV⟩ + |VH⟩)/√2
- **Time-bin entanglement**: Unbalanced Mach-Zehnder interferometers create |ψ⟩_time = (|early,late⟩ + |late,early⟩)/√2
- **Hyperentangled state**: |Ψ⟩ = |ψ⟩_pol ⊗ |ψ⟩_time

The key physics: After PBS separation, each photon (H or V) enters its own MZ interferometer. The path length difference creates a superposition of arrival times. When the photons are indistinguishable in time, quantum interference creates time-bin entanglement correlating when the two photons arrive.

**2. What the simulation actually modeled:**
The code makes a FUNDAMENTAL ERROR in representing time-bin states. It treats 'early' and 'late' as discrete Fock state modes:
- Mode 0: H_early
- Mode 1: H_late  
- Mode 2: V_early
- Mode 3: V_late

This is **physically incorrect**. Time bins are not orthogonal quantum modes - they represent temporal wavepacket positions. The simulation applies beam splitter operators to mix these 'modes', but this doesn't capture the actual physics of temporal interference.

**The critical flaw**: Fock states have NO temporal structure. A state like |1⟩_early ⊗ |1⟩_late means 'one photon in mode early, one in mode late' - but these aren't different times, they're just different labeled modes. Real time-bin entanglement requires:
- Wavepacket overlap/distinguishability
- Coherence time vs delay time relationships
- Actual temporal correlations in detection events

None of this exists in the Fock state formalism.

**3. What results came out:**
- `state_purity = 1.0` ✓ (pure state, as expected for ideal SPDC)
- `entanglement_entropy_bits ≈ 0` ✗ **CRITICAL FAILURE**
- `polarization_correlation_HV = 1.0` ✓ (but trivial - started with definite |HV⟩)
- `timebin_both_early = 0.25` ✓ (equal superposition)
- `timebin_both_late = 0.25` ✓ (equal superposition)
- `timebin_H_early_V_late = 0.25` ✓ (equal superposition)
- `timebin_H_late_V_early = 0.25` ✓ (equal superposition)
- `timebin_visibility = 0.0` ✗ **CRITICAL FAILURE**
- `hyperentanglement_verified = 0.0` ✗ **DESIGN GOAL FAILED**

**4. Why the mismatch:**

**Entanglement entropy = 0**: The simulation started with a SEPARABLE state |HV⟩ = |1_H⟩ ⊗ |1_V⟩, not the entangled state (|HV⟩ + |VH⟩)/√2. The code says:
```python
state_HV = qt.tensor(one, vac, one, vac)  # |1_H_early, 0_H_late, 1_V_early, 0_V_late⟩
psi_initial = state_HV.unit()
```
This is a product state with ZERO entanglement. Type-II SPDC should create a superposition of |HV⟩ and |VH⟩, but the code only implements one term.

**Time-bin visibility = 0**: The equal probabilities (0.25 each) indicate CLASSICAL mixing, not quantum entanglement. For true time-bin entanglement, you'd expect:
- High probability for correlated arrivals (both early OR both late)
- Low probability for anti-correlated arrivals
- Visibility V = (P_corr - P_anti)/(P_corr + P_anti) >> 0

The 0.25/0.25/0.25/0.25 distribution is what you get from completely uncorrelated, distinguishable photons randomly choosing paths.

**The deeper issue**: Even if the code were fixed to start with (|HV⟩ + |VH⟩)/√2, Fock states CANNOT represent time-bin entanglement because:
- Time bins require temporal wavepacket formalism (not Fock states)
- Indistinguishability depends on coherence length vs delay
- Detection timing requires continuous-time models
- Interference visibility depends on wavepacket overlap integrals

**5. Honest assessment:**
This simulation is **NOT TRUSTWORTHY** for validating hyperentanglement. Rating: 2/10

**What works:**
- Correctly models beam splitter operations on Fock states
- Preserves photon number (2 photons throughout)
- State purity calculation is correct

**What fails:**
- Initial state is separable, not polarization-entangled
- Time-bin 'modes' don't represent actual temporal physics
- No temporal wavepacket structure
- No coherence/distinguishability modeling
- Entanglement metrics show zero entanglement (design failure)

**What CAN'T be fixed in this framework:**
Fock state simulations are fundamentally incompatible with time-bin entanglement. You need:
- Continuous-time wavepacket models
- Temporal correlation functions
- Coherence time vs interferometer delay relationships
- Time-resolved detection modeling

This requires moving beyond Fock states to temporal mode representations or full field quantization with time-dependent detection operators.

## Key Insight

Time-bin entanglement requires temporal wavepacket formalism that Fock states fundamentally cannot provide - treating 'early' and 'late' as discrete modes completely misses the physics of temporal indistinguishability.

## Design Intent

**Components:**
- Type-II BBO crystal: Creates polarization-entangled pairs (|HV⟩ + |VH⟩)/√2 at 810nm
- PBS separator: Spatially separates H and V photons into independent channels
- Two unbalanced MZ interferometers: Create time-bin superpositions via path length differences
- Four SPADs with 50ps timing resolution: Measure both polarization (via PBS analysis) and arrival times
- Coincidence logic: Identifies 4-fold coincidences to verify hyperentanglement

**Physics Goal:** Create hyperentangled photon pairs with simultaneous entanglement in polarization (H/V) and time-bin (early/late) degrees of freedom, verified by measuring both polarization correlations and temporal coincidence patterns

**Key Parameters:**
- SPDC wavelength: 810nm (degenerate, Type-II)
- MZ path difference: Creates distinguishable time bins (design implies ~ps-ns scale)
- Timing resolution: 50ps (must resolve time-bin separation)
- Coincidence window: 3ns (captures both time bins)
- Expected state: |Ψ⟩ = (|HV⟩ + |VH⟩)/√2 ⊗ (|early,late⟩ + |late,early⟩)/√2

## QuTiP Implementation

### State Init

```python
# WRONG: Creates separable |HV⟩ state, not entangled (|HV⟩ + |VH⟩)/√2
vac = qt.fock(cutoff_dim, 0)
one = qt.fock(cutoff_dim, 1)

# Initial state after SPDC (both photons in early time bin):
# |HV⟩ = one H-photon, one V-photon
# In 4-mode space: |1_H_early, 0_H_late, 1_V_early, 0_V_late⟩
state_HV = qt.tensor(one, vac, one, vac)
psi_initial = state_HV.unit()

# MISSING: Should be (|1_H, 1_V⟩ + |1_V, 1_H⟩)/√2 for Type-II SPDC polarization entanglement
```

### Operations

```python
# Treats time bins as discrete Fock modes (WRONG PHYSICS)
# MZ for H-photon:
a_H_early = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), 
                      qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_H_late = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))

# BS1: Mixes 'early' and 'late' modes
theta_bs = np.pi/4
H_bs_H = theta_bs * (a_H_early.dag() * a_H_late + a_H_early * a_H_late.dag())
U_bs1_H = (-1j * H_bs_H).expm()
psi = U_bs1_H * psi_initial

# Phase shift on 'late' mode
n_H_late = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
U_phase_H = (1j * phi_H * n_H_late).expm()
psi = U_phase_H * psi

# BS2: Second beam splitter
U_bs2_H = (-1j * H_bs_H).expm()
psi = U_bs2_H * psi

# Same for V-photon MZ...
# PROBLEM: This models mode mixing, NOT temporal wavepacket interference
```

### Measurements

```python
# Projects onto 'time-bin' states (actually just mode occupations)
proj_HV_ee = qt.tensor(one, vac, one, vac) * qt.tensor(one, vac, one, vac).dag()
proj_HV_el = qt.tensor(one, vac, vac, one) * qt.tensor(one, vac, vac, one).dag()
proj_HV_le = qt.tensor(vac, one, one, vac) * qt.tensor(vac, one, one, vac).dag()
proj_HV_ll = qt.tensor(vac, one, vac, one) * qt.tensor(vac, one, vac, one).dag()

prob_ee = float(abs((proj_HV_ee * rho_final).tr()))  # both early
prob_ll = float(abs((proj_HV_ll * rho_final).tr()))  # both late

# Visibility calculation
correlated = prob_ee + prob_ll
anticorrelated = prob_el + prob_le
timebin_visibility = float(abs(correlated - anticorrelated) / 
                          (correlated + anticorrelated + 1e-12))

# PROBLEM: These are mode occupations, not temporal detection correlations
```

## How Design Maps to Code

**Design → Code Mapping:**

1. **Type-II SPDC polarization entanglement**: 
   - Design wants: (|HV⟩ + |VH⟩)/√2
   - Code implements: |HV⟩ only (separable, zero entanglement)
   - **MISMATCH**: Missing the superposition that creates entanglement

2. **Time-bin entanglement via MZ interferometers**:
   - Design wants: Temporal wavepacket superposition creating (|early,late⟩ + |late,early⟩)/√2
   - Code implements: Beam splitter mixing of abstract 'time modes'
   - **FUNDAMENTAL MISMATCH**: Time bins aren't Fock modes. Real MZ creates temporal superposition based on path length difference, coherence time, and wavepacket distinguishability. None of this physics exists in Fock state formalism.

3. **Hyperentanglement verification**:
   - Design wants: High visibility in BOTH polarization and time-bin measurements
   - Code measures: Entanglement entropy (should be >0 for entangled states) and time-bin visibility
   - **RESULTS SHOW FAILURE**: Entropy ≈ 0 (no entanglement), visibility = 0 (no temporal correlations)

4. **Four-fold coincidence detection**:
   - Design wants: Time-resolved detection showing correlated arrival times
   - Code implements: Static projectors onto mode occupation states
   - **MISMATCH**: No temporal resolution, no coincidence timing, no wavepacket physics

**The core issue**: The designer's experiment relies on TEMPORAL PHYSICS (wavepacket overlap, coherence times, detection timing) that simply doesn't exist in the Fock state representation. The simulation runs without errors but models a completely different physical scenario - abstract mode mixing rather than temporal interference.

## Identified Limitations

- Fock states have no temporal structure - cannot represent time-bin degrees of freedom
- Initial state is separable |HV⟩, not entangled (|HV⟩ + |VH⟩)/√2 as designed
- Time-bin 'modes' are artificial labels, not actual temporal wavepackets
- No wavepacket overlap/distinguishability physics
- No coherence time vs delay time relationships
- Missing temporal correlation functions needed for time-bin visibility
- Cannot model detection timing resolution or coincidence windows
- Beam splitter mixing of 'time modes' doesn't correspond to physical MZ interference

## Recommendations

1. Debug the Mach-Zehnder interferometer implementation - the uniform time-bin distribution suggests the interferometers are not creating coherent superpositions or phase relationships are incorrect
2. Verify the time-bin encoding scheme ensures proper path length differences and that detection timing can resolve early/late photon arrivals with sufficient precision
3. Implement active phase stabilization in both MZ interferometers and ensure the relative phases between early/early, late/late, and cross terms produce the expected entangled state (e.g., |early,early⟩ + |late,late⟩)/√2

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
