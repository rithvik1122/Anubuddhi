# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Franson Interferometer for Time-Bin Entanglement

**Timestamp:** 20251125_161034

**Quality Rating:** 2/10 (POOR)

---

## Overview

**EDUCATIONAL POST-MORTEM: Franson Interferometer Simulation**

**1. What the designer wanted to achieve:**
The designer aims to demonstrate time-bin entanglement via Franson interference. The key physics: SPDC creates photon pairs entangled in *when* they're created (early vs late time). Each photon enters an unbalanced Mach-Zehnder with path difference ΔL >> coherence length. This erases 'which-path' information for individual photons. The entangled state |ψ⟩ = (|early,early⟩ + e^(iφ)|late,late⟩)/√2 means BOTH photons take the short path OR BOTH take the long path - they're correlated in arrival time. Narrow-band filters (coherence time τ_c > ΔL/c) make the early/late emission times indistinguishable. When scanning both interferometer phases, coincidence counts should show sinusoidal oscillation with high visibility (>70%), proving the photons are entangled in the time domain. This is fundamentally about *temporal correlations* - the photons don't 'know' when they were created, but their creation times are perfectly correlated.

**2. What the simulation code actually modeled:**
The code models spatial mode entanglement using 6 Fock state modes representing different spatial paths through the interferometers. It starts with |1_signal_in, 0, 0, 1_idler_in, 0, 0⟩ and applies beam splitter operators to create path superpositions. The critical issue: **Fock states have ZERO temporal structure**. A state like |1⟩ in mode 'signal_short' represents 'one photon in this spatial mode' but says nothing about WHEN that photon arrives. The code applies phase shifts as φ·n̂ operators, which add phase based on photon number but don't affect temporal distinguishability. The simulation treats this as a purely spatial interference problem - like nested Mach-Zehnder interferometers in space, not time.

**3. What results came out:**
- **visibility_franson = 0.997**: Near-perfect visibility suggests ideal quantum interference
- **purity_reduced_state = 1.0**: Signal photons alone are in a pure state (NOT entangled)
- **entanglement_entropy ≈ 0**: Confirms NO entanglement between signal and idler
- **fidelity_to_ideal_timebin = 0.568**: Poor match to expected time-bin entangled state
- **total_photon_number = 2.0**: Photon number conserved (good)

**4. Why they DON'T match expectations:**

The smoking gun is **purity = 1.0 and entropy ≈ 0**. Real time-bin entanglement requires the signal and idler to be in a mixed state when considered individually - you can't know which 'time bin' one photon is in without measuring the other. The simulation shows pure reduced states, meaning there's NO entanglement between signal and idler photons.

What went wrong? The code creates spatial path superpositions correctly, but **Franson interference fundamentally relies on temporal indistinguishability**, which cannot exist in Fock states:

- **Missing physics #1: Wavepacket temporal structure** - Real photons are wavepackets with finite duration. The narrow-band filter creates long coherence time τ_c, making early/late emission times indistinguishable. Fock states |n⟩ are time-independent - they represent 'n photons exist' with no information about arrival time distributions.

- **Missing physics #2: Time-bin encoding** - The designer's state |early,early⟩ + |late,late⟩ refers to photons created at different times t₀ vs t₀+Δt. This requires modeling the quantum state as a function of time: |ψ(t)⟩. Fock states are snapshots at a single instant.

- **Missing physics #3: Path length difference meaning** - In real Franson setup, ΔL creates time delay Δt = ΔL/c. The narrow filter ensures you can't tell if a coincidence came from (both short paths) or (both long paths) because the arrival time difference equals the emission time uncertainty. The simulation's phase shift φ·n̂ adds phase but doesn't model temporal delay or distinguishability.

- **False positive visibility**: The 99.7% visibility comes from spatial mode interference, not time-bin entanglement. The code accidentally built a spatial Bell state, not a temporal one. The high visibility just means 'beam splitters work correctly in simulation' - it doesn't validate the Franson physics.

**5. Honest assessment:**

This simulation is **fundamentally incapable** of validating Franson interferometer physics. It's like trying to simulate a movie using still photographs - you can show individual frames (spatial modes) but can't capture motion (temporal correlations). The Fock state basis lacks the temporal degrees of freedom needed for time-bin entanglement.

To properly simulate this, you'd need:
- Time-dependent Hamiltonians modeling photon creation at different times
- Wavepacket representations (e.g., continuous-mode Gaussian states)
- Filter transfer functions affecting temporal coherence
- Explicit timing measurements with detector resolution

The current approach gives misleading confidence (99.7% visibility!) while missing the core physics entirely. The zero entanglement entropy proves the simulation doesn't capture what the designer intended.

**Key pedagogical point**: High visibility in simulation ≠ validation of design. Always check if the simulation's degrees of freedom match the physical mechanism. Here, spatial modes can't substitute for temporal correlations.

## Key Insight

Fock states can model spatial interference but fundamentally cannot capture time-bin entanglement - you cannot simulate temporal correlations without temporal degrees of freedom in your quantum state representation.

## Design Intent

**Components:**
- SPDC source: Creates entangled photon pairs in superposition of early/late emission times
- PBS separator: Splits orthogonally polarized signal/idler into separate spatial paths
- Unbalanced MZIs: Path difference ΔL >> coherence length for each photon
- Narrow-band filters (3nm bandwidth): Create coherence time τ_c > ΔL/c to erase temporal distinguishability
- Phase shifters: Scan interferometer phases to reveal two-photon interference
- Coincidence counter: Measure joint detection events, not singles

**Physics Goal:** Demonstrate time-bin entanglement via Franson interference - photons entangled in WHEN they're created, with coincidence visibility proving they're in superposition |early,early⟩ + e^(iφ)|late,late⟩ despite individual path information being erased

**Key Parameters:**
- ΔL >> coherence length: Ensures no single-photon interference
- Filter bandwidth 3nm → coherence time ~200fs: Makes early/late times indistinguishable
- Path delay ΔL/c: Must be less than coherence time for indistinguishability
- Expected visibility > 70%: Required for Bell inequality violation

## QuTiP Implementation

### State Init

```python
# Starts with photons in spatial input modes (NO temporal information)
vac = qt.fock(cutoff_dim, 0)
one = qt.fock(cutoff_dim, 1)
psi_initial = qt.tensor(one, vac, vac, one, vac, vac)
# This represents: 1 photon in signal_in mode, 1 in idler_in mode
# Fock states |1⟩ have NO temporal structure - just photon number
```

### Operations

```python
# Beam splitter creates SPATIAL superposition (not temporal)
theta_bs = np.pi/4  # 50:50 beam splitter
H_bs1_signal = theta_bs * (a_sig_short.dag() * a_sig_in + a_sig_short * a_sig_in.dag() +
                           a_sig_long.dag() * a_sig_in + a_sig_long * a_sig_in.dag())
U_bs1_signal = (-1j * H_bs1_signal).expm()

# Phase shift as number operator (adds phase, doesn't affect timing)
phase_signal = qt.tensor(..., (1j * phi_signal * qt.num(cutoff_dim)).expm(), ...)
# Problem: This is e^(iφn̂), which just adds phase based on photon number
# It does NOT model temporal delay or wavepacket distinguishability
```

### Measurements

```python
# Coincidence measurement on spatial modes
n_sig_short = qt.tensor(qt.qeye(...), qt.num(cutoff_dim), ...)
n_idl_short = qt.tensor(..., qt.num(cutoff_dim), ...)
coincidence_op = n_sig_short * n_idl_short
coincidence = float(abs(qt.expect(coincidence_op, psi)))
# This measures: 'probability both photons in short arm spatial modes'
# NOT: 'probability both photons arrive within coincidence window'

# Entanglement check reveals the problem:
rho_signal = rho_full.ptrace([0, 1, 2])  # Trace out idler
purity_signal = float(abs((rho_signal * rho_signal).tr()))
# Result: purity = 1.0 → signal is PURE state → NO entanglement!
# Real time-bin entanglement requires mixed reduced states
```

## How Design Maps to Code

**Design → Code mapping failure:**

| Designer's Intent | Code Implementation | Match? |
|------------------|---------------------|--------|
| Time-bin entangled state \|early,early⟩ + \|late,late⟩ | Spatial mode state \|short,short⟩ + \|long,long⟩ | ❌ Different physics |
| Photons created at different times t₀ vs t₀+Δt | Fock states (no time dependence) | ❌ Missing temporal DOF |
| Path delay ΔL creates temporal offset | Phase shift e^(iφn̂) | ❌ No temporal meaning |
| Narrow filter creates coherence time τ_c | Not modeled | ❌ Critical missing element |
| Temporal indistinguishability when τ_c > ΔL/c | No temporal distinguishability concept | ❌ Cannot exist in Fock basis |
| Signal-idler time correlations (entanglement) | Purity=1.0, entropy=0 (no entanglement) | ❌ Contradicts design |
| Coincidence window timing measurement | Spatial mode number expectation | ❌ Different measurement |

**What the code actually simulates:** Two nested Mach-Zehnder interferometers in SPACE with entangled photons entering them. This creates spatial path entanglement and shows interference, but it's completely different from time-bin entanglement. The 99.7% visibility is real for the spatial problem but irrelevant to the Franson design.

**Bottom line:** The simulation accidentally solved a different quantum optics problem (spatial mode entanglement in nested interferometers) that happens to also show high visibility. But this doesn't validate the designer's time-bin entanglement claim. The zero entanglement entropy is the definitive proof - real Franson interference requires signal-idler entanglement, which this simulation demonstrably lacks.

## Identified Limitations

- Fock states have no temporal structure - cannot represent 'early' vs 'late' photon creation times
- Phase shift operator φ·n̂ adds global phase but doesn't affect temporal distinguishability or wavepacket overlap
- Cannot model narrow-band filter effect on coherence time and temporal indistinguishability
- Path length difference ΔL has no physical meaning without temporal wavepacket propagation
- Reduced state purity = 1.0 proves no signal-idler entanglement, contradicting time-bin entanglement requirement
- Simulation models spatial mode interference (nested MZIs) not time-bin correlations
- Missing detector timing resolution and coincidence window physics - these are critical for Franson measurements

## Recommendations

1. Verify the time-bin encoding basis - the state appears to be in the wrong superposition basis despite showing quantum correlations
2. Check the relative phase settings and path length differences in the unbalanced Mach-Zehnder interferometers to ensure proper time-bin state preparation
3. Implement proper initialization to the |early,early⟩ + |late,late⟩ superposition state rather than what appears to be a different entangled basis

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
