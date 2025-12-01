# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Electromagnetically Induced Transparency (EIT) in Warm Rubidium Vapor

**Timestamp:** 20251126_124851

**Quality Rating:** 4/10 (FAIR)

---

## Overview

**1. DESIGNER'S INTENT:**
The designer wants to demonstrate Electromagnetically Induced Transparency (EIT) - a quantum interference phenomenon where a strong coupling laser creates a 'dark state' that makes an otherwise opaque atomic medium transparent to a weak probe laser. The key physics: when both lasers satisfy the two-photon resonance condition (probe detuning + coupling detuning = hyperfine splitting ~6.8 GHz), quantum interference between two excitation pathways prevents absorption. This should produce: (a) a narrow transparency window in the absorption spectrum, (b) high transmission at resonance vs. strong absorption off-resonance, (c) population trapped in a coherent superposition of ground states, and (d) steep dispersion enabling slow light.

**2. WHAT THE SIMULATION ACTUALLY MODELED:**
The code implements a three-level Lambda system using density matrix formalism with Lindblad master equation - this is actually a CORRECT approach for EIT. However, there are catastrophic parameter mismatches:

- **CRITICAL FLAW #1 - Optical Depth**: The simulation calculates optical_depth = 0.00035, meaning the vapor is essentially TRANSPARENT even without EIT. Real EIT experiments require optical depth ~10-100 to see dramatic transparency enhancement. With OD=0.0003, background transmission is already 99.97% - there's no opacity to overcome!

- **CRITICAL FLAW #2 - Rabi Frequencies**: The code calculates Ω_probe = 26.5 MHz and Ω_coupling = 265 MHz. For a Lambda system with natural linewidth γ = 6 MHz, the strong coupling regime requires Ω_coupling >> γ (satisfied), but the probe should be weak: Ω_probe << γ. Here Ω_probe ≈ 4.4γ, violating the perturbative limit. The 'weak probe' approximation breaks down.

- **CRITICAL FLAW #3 - Temperature/Density Mismatch**: At 50°C, the code calculates atomic density = 16,030 atoms/cm³. This is ~6 orders of magnitude too LOW for warm vapor EIT. Real Rb vapor at 50°C has density ~10^11 atoms/cm³. The exponential formula appears incorrect (missing a multiplicative factor).

- **PHYSICS CORRECTLY CAPTURED**: The Hamiltonian structure, decay operators, ground-state coherence dephasing, and dark state calculation are all physically sound. The simulation COULD validate EIT if parameters were realistic.

**3. ACTUAL RESULTS:**
The simulation shows:
- Background absorption: 0.0026% (essentially transparent)
- Resonance absorption: 0.0026% (unchanged)
- EIT contrast: 0.0006% (negligible)
- Transparency enhancement: 1.0 (no enhancement)
- EIT linewidth: 0 MHz (no detectable window)
- Dark state fidelity: 99.997% (excellent coherence)
- Ground coherence: 0.099 (weak but present)

The results show NO EIT SIGNATURE. The medium is completely transparent at all detunings because the optical depth is ~10,000× too small.

**4. WHY THE MISMATCH:**

**Root Cause Analysis:**
```python
# Designer specified:
temperature = 50  # Celsius
cell_length = 75  # mm

# Code calculated:
atomic_density = 1e10 * np.exp(-(4312 / T_kelvin))  # atoms/cm³
# At T=323K: density ≈ 16,030 atoms/cm³

# Then optical depth:
cross_section_cm2 = 3 * wavelength_m**2 / (2 * np.pi) * 1e4  # cm²
optical_depth = atomic_density * cross_section_cm2 * (cell_length / 10)
# Result: OD = 0.00035
```

The atomic density formula is off by ~10^6. The correct Rb-87 vapor pressure formula gives:
- At 50°C: n ≈ 10^11 atoms/cm³ → OD ≈ 35 (strong absorption)
- At 20°C: n ≈ 10^9 atoms/cm³ → OD ≈ 0.35 (weak absorption)

With correct density, we'd see:
- Background transmission: ~10^-15 (opaque)
- EIT transmission: ~50-90% (dramatic transparency)
- Contrast: ~90%

**5. HONEST ASSESSMENT:**

This simulation is **FUNDAMENTALLY SOUND** in its physics implementation but **COMPLETELY INVALID** for validating the design due to parameter errors. The density matrix approach with Lindblad operators is the gold standard for EIT simulation - it correctly captures:
- Quantum coherence between ground states
- Dark state formation
- Destructive interference of excitation pathways
- Spontaneous emission and dephasing

However, the simulation cannot be trusted because:
1. Atomic density is 10^6× too low (formula error)
2. Resulting optical depth makes EIT unobservable
3. Probe Rabi frequency violates weak-probe assumption
4. No verification that two-photon resonance condition is satisfied (probe + coupling detuning should equal 6.8 GHz hyperfine splitting, but both are scanned identically from -50 to +50 MHz)

**What's MISSING from Fock/density matrix approach:**
- Slow light propagation (requires spatiotemporal dynamics, not steady-state)
- Pulse delay and compression (needs time-dependent Schrödinger equation with propagation)
- Doppler broadening effects (requires velocity distribution integration)
- Beam geometry and alignment (assumes perfect overlap)
- Transverse spatial profiles (1D approximation)

These are NOT fundamental limitations of density matrices - they just require more sophisticated treatment (Maxwell-Bloch equations, propagation models).

**VERDICT:** The code is 'correct physics, wrong numbers.' With proper atomic density (~10^11 cm^-3), this simulation would show textbook EIT with ~90% transparency enhancement. As-is, it's like trying to observe ocean waves in a teaspoon - the physics is right, but the scale is wrong.

## Key Insight

Simulation uses correct quantum optics formalism for EIT but catastrophic parameter errors (atomic density 10^6× too low) make the medium transparent without EIT, rendering validation meaningless despite sound theoretical framework.

## Design Intent

**Components:**
- Probe laser (795nm, 0.5mW): weak beam on |1⟩→|3⟩ transition, normally absorbed
- Coupling laser (780nm, 50mW): strong beam on |2⟩→|3⟩ transition, creates dark state
- Rb-87 vapor cell (50°C, 75mm): three-level Lambda system with hyperfine ground states
- Photodiode + lock-in: detect transmission spectrum showing transparency window

**Physics Goal:** Demonstrate quantum interference creating transparency window: coupling laser induces coherent population trapping in dark state |D⟩ = (Ω_c|1⟩ - Ω_p|2⟩)/√(Ω_c² + Ω_p²), eliminating probe absorption when two-photon resonance satisfied, enabling 50-90% transmission enhancement and slow light propagation

**Key Parameters:**
- Optical depth: should be 10-100 for observable EIT (requires n~10^11 atoms/cm³)
- Coupling Rabi frequency: 50-500 MHz (strong field regime)
- Probe Rabi frequency: 0.1-1 MHz (weak probe limit)
- Two-photon detuning: scan ±50 MHz around hyperfine splitting (6.8 GHz)
- Expected EIT linewidth: ~1-10 MHz (depends on Ω_c²/γ)

## QuTiP Implementation

### State Init

```python
# Three-level Lambda system basis states
ground1 = qt.basis(3, 0)  # |1⟩ (F=1)
ground2 = qt.basis(3, 1)  # |2⟩ (F=2)
excited = qt.basis(3, 2)  # |3⟩ (F'=2)

# Temperature-dependent atomic density (INCORRECT FORMULA)
T_kelvin = temperature + 273.15
atomic_density = 1e10 * np.exp(-(4312 / T_kelvin))  # atoms/cm³
# Result: 16,030 atoms/cm³ (should be ~10^11)

# Rabi frequencies from laser intensities
beam_waist = 0.5  # mm
beam_area_cm2 = np.pi * (beam_waist / 10)**2
intensity_probe = probe_power / beam_area_cm2  # mW/cm²
E_probe = np.sqrt(2 * intensity_probe_SI / (epsilon_0 * c))
omega_probe_SI = dipole_moment * E_probe / hbar
omega_probe = omega_probe_SI / (2 * np.pi * 1e6)  # MHz
# Result: 26.5 MHz (too strong for 'weak probe')
```

### Operations

```python
# Hamiltonian in rotating frame (two-photon detuning)
for delta_probe in detuning_range:
    delta_coupling = delta_probe  # ISSUE: both scan together
    
    H = -delta_probe * (excited * excited.dag())
    H += -(delta_probe - delta_coupling) * (ground2 * ground2.dag())
    H += omega_probe / 2 * (excited * ground1.dag() + ground1 * excited.dag())
    H += omega_coupling / 2 * (excited * ground2.dag() + ground2 * excited.dag())
    
    # Decay operators (CORRECT PHYSICS)
    c_ops = []
    c_ops.append(np.sqrt(gamma / 2) * ground1 * excited.dag())
    c_ops.append(np.sqrt(gamma / 2) * ground2 * excited.dag())
    c_ops.append(np.sqrt(gamma_dephase) * (ground1 * ground1.dag() - ground2 * ground2.dag()))
    
    # Steady-state density matrix
    rho_ss = qt.steadystate(H, c_ops)
    rho_ss = rho_ss / rho_ss.tr()
```

### Measurements

```python
# Excited state population (absorption)
excited_population = float(np.abs(qt.expect(excited * excited.dag(), rho_ss)))
absorption_spectrum.append(excited_population)

# Optical depth (CRITICAL ERROR: too small)
wavelength_m = probe_wavelength * 1e-9
cross_section_cm2 = 3 * wavelength_m**2 / (2 * np.pi) * 1e4
optical_depth = atomic_density * cross_section_cm2 * (cell_length / 10)
# Result: OD = 0.00035 (should be ~35)

# Transmission
transmission = np.exp(-optical_depth * excited_population)
transmission_spectrum.append(float(transmission))

# Dark state fidelity at resonance
dark_state = (omega_coupling * ground1 - omega_probe * ground2) / norm_factor
dark_state_fidelity = float(np.abs(qt.fidelity(rho_resonance, dark_state_density)))
# Result: 99.997% (CORRECT - coherence is maintained)
```

## How Design Maps to Code

**DESIGN → CODE MAPPING:**

✓ **CORRECT**: Lambda system Hamiltonian with probe/coupling fields
✓ **CORRECT**: Spontaneous emission and ground-state dephasing operators
✓ **CORRECT**: Dark state calculation and coherence tracking
✓ **CORRECT**: Steady-state density matrix approach for continuous-wave EIT

✗ **WRONG**: Atomic density formula gives 16,030 atoms/cm³ vs. required ~10^11 atoms/cm³
✗ **WRONG**: Optical depth 0.0003 vs. required 10-100 for observable EIT
✗ **WRONG**: Probe Rabi frequency 26.5 MHz violates weak-probe limit (should be <1 MHz)
✗ **WRONG**: Two-photon detuning scanned incorrectly (both lasers move together instead of maintaining 6.8 GHz offset)
✗ **MISSING**: Slow light group velocity (requires susceptibility χ calculation from off-diagonal density matrix elements)
✗ **MISSING**: Wavelength inconsistency (designer specified 795nm probe + 780nm coupling, code uses both at 780nm)

**WHY RESULTS SHOW NO EIT:**
With OD=0.0003, Beer's law gives transmission T = exp(-OD) ≈ 99.97% even with maximum absorption. The medium is already transparent! EIT creates transparency by reducing absorption from ρ₃₃≈0.5 (saturated) to ρ₃₃≈0.001 (dark state). But when OD is tiny, this changes transmission from 99.985% to 99.9997% - an unmeasurable 0.01% improvement instead of the dramatic 10^-15 → 50% jump expected in real experiments.

The simulation is like testing a bulletproof vest against a feather - technically correct methodology, but the test conditions make success/failure indistinguishable.

## Identified Limitations

- Atomic density calculation error: result is ~10^6 times too low for 50°C Rb vapor
- Optical depth of 0.0003 makes medium already transparent - no EIT signature observable
- Probe Rabi frequency (26.5 MHz) violates weak-probe assumption (should be << 6 MHz linewidth)
- Steady-state solution cannot capture slow light propagation or pulse delay (requires time-dependent Maxwell-Bloch)
- Two-photon resonance condition not properly implemented: both lasers scan same detuning range instead of maintaining fixed frequency difference equal to hyperfine splitting
- No Doppler broadening (requires velocity-averaged density matrix)
- 1D model ignores beam geometry and transverse mode structure

## Recommendations

1. Increase atomic density by 6-7 orders of magnitude to ~10^11-10^12 cm^-3 (typical for warm Rb vapor at reasonable temperature)
2. Verify optical depth calculation - should be 10-100 for observable EIT, requiring proper vapor cell length and temperature
3. Reduce probe Rabi frequency significantly (currently 26.5 MHz is too strong) - should be <1 MHz to maintain weak probe regime and observe transparency window

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
