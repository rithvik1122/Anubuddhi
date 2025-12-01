# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Quantum Frequency Converter: Telecom to Visible (Corrected)

**Timestamp:** 20251126_132215

**Quality Rating:** 4/10 (FAIR)

---

## Overview

**1. DESIGNER'S INTENT:**
The designer wants to demonstrate quantum frequency conversion - taking single photons at telecom wavelength (1550nm) and upconverting them to visible wavelength (600.4nm) via sum-frequency generation (SFG) in a PPLN crystal. The critical physics claims are: (a) energy conservation (1/λ_out = 1/1550 + 1/980), (b) preservation of quantum coherence and photon statistics during conversion, and (c) efficient detection using silicon APDs which work well at visible wavelengths. This is a real technique used in quantum networks to interface telecom-band quantum states with visible-band detectors.

**2. WHAT THE SIMULATION ACTUALLY MODELED:**
The code implements a three-mode SFG Hamiltonian H = g(a_sfg† a_signal a_pump + h.c.) acting on Fock states. It starts with |1⟩_signal ⊗ |α⟩_pump ⊗ |0⟩_sfg and evolves under unitary time evolution. This is a reasonable first-order model of the nonlinear optical process, BUT it has critical limitations:

- **Missing quasi-phase-matching physics**: The PPLN poling period (19.2μm) and temperature (95°C) are specified in the design but completely ignored in the simulation. Real SFG efficiency depends critically on phase-matching conditions.
- **No spatial mode overlap**: The simulation assumes perfect mode overlap between signal and pump in the crystal. The design has separate focusing lenses (focal_length=100mm) but the simulation doesn't model spatial mode matching.
- **Coupling strength is arbitrary**: The code uses g=0.3 with no justification. Real coupling depends on crystal length, χ(2) nonlinearity, pump power, and mode overlap - none of which are calculated from the physical parameters.
- **Pump depletion ignored**: With 500mW pump power and single photons, pump depletion is negligible (correctly modeled as coherent state), but the interaction time is normalized rather than derived from actual crystal length and beam parameters.

**3. WHAT RESULTS CAME OUT:**
- Energy conservation: ✓ Correctly calculated 600.4nm
- Conversion efficiency: 5.9% (quantum simulation)
- Total system efficiency: 2.8% (including losses)
- SFG single-photon fidelity: **24%** ← THIS IS THE SMOKING GUN
- g2 coherence: 0.0 (sub-Poissonian, good)

**4. WHY THE MISMATCH:**
The **fidelity of 0.24** means the output state is only 24% similar to a pure single-photon state |1⟩. This happens because:

```python
# The Hamiltonian creates entanglement between modes:
H_sfg = coupling_strength * (a_sfg.dag() * a_signal * a_pump + h.c.)
# After evolution, the state is NOT a product state
# It's entangled: approximately |0⟩_s|α⟩_p|0⟩_sfg + √0.06|0⟩_s|α-1⟩_p|1⟩_sfg + ...
```

When we trace out signal and pump modes:
```python
rho_sfg = rho_final.ptrace(2)  # Trace out signal and pump
```

We get a **mixed state**, not a pure single photon. This is actually physically correct for low conversion efficiency! The SFG mode is in a statistical mixture of |0⟩ (no conversion, 94% probability) and |1⟩ (successful conversion, 6% probability). The fidelity of 24% reflects this mixture.

**However**, the simulation is missing crucial physics:

- **Heralding**: The design specifies "heralded single photons" at the input. Real experiments condition on successful conversion (post-selection). The simulation doesn't implement conditional measurement.
- **Temporal modes**: Fock states have no temporal structure. Real photons have finite bandwidth and temporal wavepackets. The conversion efficiency depends on spectral overlap between signal, pump, and phase-matching bandwidth.
- **Classical losses vs quantum effects**: The code multiplies efficiencies (0.85 × 0.059 × 0.75 × 0.75 = 2.8%) but doesn't model where photons are lost (absorption, scattering, mode mismatch).

**5. HONEST ASSESSMENT:**
This simulation validates the **bare minimum**: energy conservation works, and the SFG Hamiltonian produces some photons in the output mode. But it does NOT validate the designer's key claim that "quantum coherence and photon statistics are preserved." 

The low fidelity (24%) actually suggests the opposite - significant degradation of quantum state purity. In reality, with proper heralding and post-selection, you'd measure only the successfully converted photons, which should have high fidelity. The simulation conflates the unconverted vacuum component with the converted photon.

**What this simulation CANNOT capture:**
- Phase-matching bandwidth and spectral filtering effects
- Temporal distinguishability and wavepacket overlap
- Spatial mode matching efficiency
- Noise photons from pump scattering or spontaneous parametric processes
- Realistic coupling strength derived from material parameters
- Post-selection/heralding logic

**What it CAN show:**
- Energy conservation ✓
- Qualitative photon number transfer ✓
- Sub-Poissonian statistics (g2=0) ✓
- Order-of-magnitude efficiency estimates (if coupling is calibrated)

The simulation is a toy model that demonstrates the concept but cannot validate whether this specific design with these specific parameters will work in the lab.

## Key Insight

The simulation shows SFG can transfer photon number between modes while conserving energy, but lacks the temporal, spectral, and spatial mode physics needed to validate whether this specific PPLN design preserves single-photon quantum states.

## Design Intent

**Components:**
- Heralded 1550nm single-photon source (telecom band)
- 500mW 980nm pump laser (strong classical field)
- 20mm PPLN crystal with 19.2μm poling period at 95°C (quasi-phase-matching for 1550+980→600.4nm)
- Dichroic mirrors and bandpass filter (wavelength separation)
- Silicon APD detector (75% efficiency at 600nm)

**Physics Goal:** Upconvert telecom single photons to visible wavelength via sum-frequency generation while preserving quantum coherence and photon statistics, enabling efficient detection with silicon detectors

**Key Parameters:**
- λ_signal = 1550nm (telecom)
- λ_pump = 980nm (strong pump)
- λ_SFG = 600.4nm (energy conservation: 1/1550 + 1/980)
- PPLN: 20mm length, 19.2μm poling, 95°C
- Total efficiency chain: 0.85 × η_conv × 0.75 × 0.75

## QuTiP Implementation

### State Init

```python
# Three-mode Fock/coherent state initialization
signal_state = qt.fock(cutoff_dim, 1)  # Single photon
pump_state = qt.coherent(cutoff_dim, alpha_pump)  # Strong pump (α=10)
sfg_state = qt.fock(cutoff_dim, 0)  # Vacuum
psi_initial = qt.tensor(signal_state, pump_state, sfg_state)
```

### Operations

```python
# SFG Hamiltonian with arbitrary coupling
a_signal = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_pump = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
a_sfg = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

# H = g * (a_sfg^† * a_signal * a_pump + h.c.)
H_sfg = coupling_strength * (a_sfg.dag() * a_signal * a_pump + a_sfg * a_signal.dag() * a_pump.dag())

# Time evolution with normalized time
U = (-1j * H_sfg * interaction_time).expm()
psi_final = U * psi_initial
```

### Measurements

```python
# Photon number expectation values
n_sfg = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.num(cutoff_dim))
sfg_photons_final = qt.expect(n_sfg, psi_final)

# Conversion efficiency
conversion_efficiency = sfg_photons_final / max(signal_photons_initial, 1e-10)

# Fidelity to single-photon state (after tracing out other modes)
rho_final = psi_final * psi_final.dag()
rho_sfg = rho_final.ptrace(2)  # Trace out signal and pump
sfg_single_photon_state = qt.fock(cutoff_dim, 1)
fidelity_sfg = qt.fidelity(rho_sfg, sfg_single_photon_state)

# Total system efficiency (classical loss multiplication)
total_efficiency = (fiber_input_efficiency * conversion_efficiency * 
                   fiber_output_efficiency * detector_efficiency)
```

## How Design Maps to Code

**DESIGN → CODE MAPPING:**

✓ **Energy conservation** (1/λ_out = 1/1550 + 1/980): Correctly verified in code, gives 600.4nm

✗ **PPLN quasi-phase-matching** (19.2μm poling, 95°C): Parameters extracted but never used. Real conversion efficiency depends on sinc²(ΔkL/2) where Δk depends on poling period and temperature. Code uses arbitrary g=0.3 instead.

✗ **Spatial mode matching** (separate 100mm focusing lenses): Design has explicit focusing optics, code assumes perfect overlap with no spatial mode calculation.

✗ **Heralded single photons**: Design specifies heralding (conditional detection), code uses unconditional Fock state |1⟩ with no post-selection logic.

✓ **Strong pump approximation**: Coherent state |α=10⟩ correctly models undepleted pump (500mW >> single photon energy).

✗ **Temporal/spectral modes**: Design uses real photons with finite bandwidth, code uses timeless Fock states. Cannot model phase-matching bandwidth, group velocity mismatch, or spectral filtering.

✗ **Quantum state preservation**: Design claims to preserve quantum coherence. Code shows fidelity=24%, indicating severe state degradation - but this is artifact of not implementing heralding.

✓ **Detection chain losses**: Code multiplies classical efficiencies (0.85 × 0.75 × 0.75) matching design intent, though physical origin of losses not modeled.

**BOTTOM LINE:** The simulation implements a generic three-mode SFG toy model but doesn't use the specific design parameters that would determine real-world performance. It's like simulating "a car" instead of "this specific Tesla Model 3 with these tire specs on this road surface."

## Identified Limitations

- Fock states have no temporal/spectral structure - cannot model wavepacket overlap or phase-matching bandwidth
- Coupling strength g=0.3 is arbitrary, not derived from PPLN crystal parameters (χ(2), length, poling period, temperature)
- No spatial mode overlap calculation - assumes perfect mode matching despite separate focusing optics
- Missing heralding/post-selection logic - conflates vacuum (no conversion) with successful conversion events
- Quasi-phase-matching conditions (19.2μm poling, 95°C temperature) specified but completely unused
- Interaction time normalized to 1.0 rather than calculated from crystal length and group velocities
- Cannot model noise sources: pump scatter, spontaneous parametric downconversion, detector dark counts
- Low single-photon fidelity (24%) indicates mixed state, but simulation doesn't clarify this is pre-heralding

## Recommendations

1. Implement waveguide-based phase matching in periodically-poled lithium niobate (PPLN) to improve conversion efficiency and reduce noise that degrades fidelity
2. Add spectral filtering (narrow bandpass filters) at the output to remove pump photon leakage and parametric fluorescence that contaminate the quantum state
3. Optimize pump power to balance conversion efficiency against nonlinear noise processes - current settings appear to introduce excessive multi-photon contamination reducing fidelity
4. Consider cavity-enhanced sum-frequency generation to achieve higher efficiency at lower pump powers, preserving quantum coherence

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
