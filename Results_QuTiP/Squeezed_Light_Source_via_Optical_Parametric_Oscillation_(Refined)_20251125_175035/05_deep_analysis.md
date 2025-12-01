# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Squeezed Light Source via Optical Parametric Oscillation (Refined)

**Timestamp:** 20251125_175035

**Quality Rating:** 2/10 (POOR)

---

## Overview

**CRITICAL PHYSICS FAILURE: Nonsensical Results from Fundamental Modeling Errors**

**1. What the Designer Wanted:**
The designer aims to create a squeezed light source using a sub-threshold optical parametric oscillator (OPO). Key physics:
- A 1064nm seed laser is frequency-doubled to 532nm pump
- The 532nm pump drives a PPLN crystal in a cavity, performing degenerate parametric down-conversion (532nm → 1064nm + 1064nm)
- Operating below threshold produces squeezed vacuum at 1064nm with reduced quantum noise in one quadrature
- A phase-coherent 1064nm local oscillator (LO) from the same seed laser interferes with the squeezed output at a 50:50 beam splitter
- Balanced homodyne detection measures quadrature noise, expecting ~3-10 dB squeezing below shot noise
- PDH locking and temperature control ensure stability

**2. What the Code Actually Modeled:**
The simulation attempts to model squeezed vacuum generation and homodyne detection, but contains CATASTROPHIC errors:

**ERROR 1: Photon Conservation Violation (99.99% error)**
- Input: LO has ~0.306 photons (from lo_alpha²)
- Output: Total photons = 0.306
- Conservation error = 99.99% indicates the LO photon number is WRONG by a factor of ~10⁶
- The code sets `lo_photon_rate = (power_seed * lo_power_fraction) / (h*c/λ)` then `lo_alpha = sqrt(lo_photon_rate * 1e-9)` - this arbitrary 1e-9 factor makes no physical sense

**ERROR 2: Unphysical Squeezing (68.8 dB)**
- Real OPO squeezing at 80% threshold with realistic losses: ~3-6 dB
- Simulation reports 68.8 dB (variance reduction factor of 7.6 million!)
- This is **physically impossible** - it would require:
  - Perfect quantum efficiency (simulation uses 98%)
  - Zero cavity losses (simulation has 0.2%)
  - Zero detection losses (simulation has 5%)
  - Operating at threshold (not 80%)
- Even with perfect conditions, ~15-20 dB is theoretical maximum for realistic systems

**ERROR 3: Homodyne Detection Broken**
- Homodyne visibility = 1.4% (should be >90% for good mode matching)
- This indicates the LO and signal are NOT interfering properly
- The photocurrent difference shows almost no phase dependence
- Real homodyne detection requires strong LO (10⁶-10⁹ photons), but simulation has only 0.306 photons

**ERROR 4: Negative Antisqueezing**
- Antisqueezing_dB = -68.1 dB (variance REDUCTION in orthogonal quadrature)
- This violates Heisenberg uncertainty: ΔX² · ΔP² ≥ 1/4
- If X quadrature is squeezed by 7.6×10⁶, P quadrature MUST be antisqueezed by same factor
- Negative antisqueezing is thermodynamically impossible

**ERROR 5: Min/Max Variance Nearly Equal**
- Min variance = 1.32×10⁻⁷
- Max variance = 1.55×10⁻⁷ (only 18% larger)
- For r=0.045 squeezing, expect: Var_min = e^(-2r) ≈ 0.91, Var_max = e^(2r) ≈ 1.09
- Both being ~10⁻⁷ suggests the normalization is completely wrong

**3. Root Cause Analysis:**

The code attempts to normalize homodyne photocurrent variance to quadrature variance:
```python
var_quadrature = var_I / (4 * lo_photon_number)
```

But `lo_photon_number = |alpha|² ≈ 0.306` is ~10⁶ times too small! This causes:
- Division by tiny number → artificially huge variance reduction
- The factor of 4 is correct for homodyne gain, but applied to wrong photon number
- The normalization assumes strong LO limit (|α| >> 1), which is violated

**4. What Results Actually Mean:**
- The 68.8 dB squeezing is a **numerical artifact**, not physics
- The photon conservation error confirms LO power is miscalculated
- The low homodyne visibility confirms LO is too weak for proper homodyne detection
- The squeezed state itself (purity=1.0) is correctly generated, but measurement is broken

**5. Missing Physics:**

**Temporal/Spectral Mode Matching:**
- Real homodyne detection requires LO and signal to be in same temporal mode
- Fock state simulation has NO temporal structure
- Mode-matching efficiency depends on spatial AND temporal overlap - cannot be captured

**Cavity Dynamics:**
- OPO operates in steady-state with pump continuously driving cavity
- Simulation uses static squeezed state - no cavity dynamics, no pump depletion
- Sub-threshold condition (80% threshold) is input parameter, not emergent from dynamics

**Phase Noise and Locking:**
- PDH locking stabilizes cavity resonance against drifts
- LO phase noise limits squeezing measurement
- Simulation assumes perfect phase stability - no decoherence

**Detection Bandwidth:**
- Real squeezing is frequency-dependent (cavity filtering)
- Spectrum analyzer measures noise at specific frequencies (1-100 MHz)
- Fock state simulation is frequency-independent

**6. Honest Assessment:**
This simulation **FAILS** to validate the design. While it correctly generates a squeezed Fock state, the homodyne detection measurement is fundamentally broken due to:
- Incorrect LO photon number (factor of 10⁶ error)
- Wrong normalization producing unphysical 68 dB squeezing
- Violation of uncertainty principle (negative antisqueezing)
- No temporal mode structure
- No cavity dynamics

The code would need complete rewrite of LO power calculation and homodyne normalization to produce meaningful results. Even then, Fock state approach cannot capture temporal mode matching, cavity dynamics, or frequency-dependent noise - all critical for real OPO squeezing experiments.

## Key Insight

Fock state simulation correctly generates squeezed vacuum but catastrophically fails at homodyne detection due to LO photon number error (factor 10⁶) and missing temporal mode physics, producing impossible 68 dB squeezing that violates uncertainty principle.

## Design Intent

**Components:**
- Seed laser (1064nm, 10mW): Provides phase-coherent source for both pump (via SHG) and local oscillator
- SHG crystal (PPLN, 10mm): Frequency doubles 1064nm → 532nm pump with ~70% efficiency
- OPO cavity (Finesse ~785, R=99.8%): Contains PPLN for degenerate down-conversion 532nm → 1064nm+1064nm, impedance-matched
- Homodyne detector (98% QE, 95% efficiency): Balanced photodetection measuring quadrature noise via interference with strong LO
- PDH lock + temperature control: Stabilizes cavity resonance and PPLN phase-matching

**Physics Goal:** Generate 3-10 dB squeezed vacuum at 1064nm via sub-threshold OPO (80% threshold), measure quadrature noise below shot-noise limit using balanced homodyne detection with phase-coherent LO

**Key Parameters:**
- Pump power: ~7 mW (after SHG)
- OPO threshold ratio: 80% (sub-threshold regime)
- Cavity finesse: ~785 (R_IC=99.8%, R_M1=99.8%, losses=0.2%)
- Expected squeezing: 3-6 dB below shot noise (after detection losses)
- LO power: ~100 μW (1% of seed, strong LO for homodyne)
- Homodyne visibility: >90% (good mode matching)

## QuTiP Implementation

### State Init

```python
# Squeezed vacuum generation (CORRECT)
squeeze_r = squeezing_param  # r = 0.045
squeeze_phi = 0
S = qt.squeeze(cutoff_dim, squeeze_r * np.exp(1j * squeeze_phi))
vacuum = qt.fock(cutoff_dim, 0)
squeezed_vacuum = S * vacuum
squeezed_vacuum = squeezed_vacuum.unit()

# Local oscillator (WRONG - photon number too small by 10^6)
lo_power_fraction = 0.01  # 1% of seed power
lo_photon_rate = (power_seed * lo_power_fraction) / (6.626e-34 * 3e8 / wavelength_seed)
lo_coherent_amplitude = np.sqrt(lo_photon_rate * 1e-9)  # ARBITRARY 1e-9 factor!
lo_alpha = lo_coherent_amplitude  # |alpha|^2 ≈ 0.306 (should be ~10^6)
lo_state = qt.coherent(cutoff_dim, lo_alpha)

# Combined state
psi_combined = qt.tensor(squeezed_vacuum, lo_state)
```

### Operations

```python
# 50:50 beam splitter (CORRECT operator)
theta_bs = np.pi / 4
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()

# LO phase rotation (CORRECT)
for phi in phases:
    phase_op = qt.tensor(qt.qeye(cutoff_dim), (1j * phi * qt.num(cutoff_dim)).expm())
    psi_phase = phase_op * psi_combined
    psi_phase_bs = U_bs * psi_phase
```

### Measurements

```python
# Homodyne detection (WRONG normalization)
n_a = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_b = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))
I_diff = n_a - n_b
mean_I = qt.expect(I_diff, psi_phase_bs)
mean_I2 = qt.expect(I_diff * I_diff, psi_phase_bs)
var_I = abs(mean_I2 - mean_I**2)

# CRITICAL ERROR: Dividing by lo_photon_number ≈ 0.306 instead of ~10^6
lo_photon_number = abs(lo_alpha)**2
if lo_photon_number > 1e-10:
    var_quadrature = var_I / (4 * lo_photon_number)  # Division by tiny number!
else:
    var_quadrature = var_I

# This produces var_quadrature ~ 10^-7 (unphysical)
# Squeezing calculation
vacuum_var = 1.0
squeezing_dB = -10 * np.log10(max(min_variance / vacuum_var, 1e-10))  # 68.8 dB!
```

## How Design Maps to Code

**Design → Code Mapping:**

✓ **Squeezed state generation**: Code correctly applies squeeze operator S(r) with r=0.045 to vacuum, producing proper squeezed Fock state (purity=1.0 confirms)

✗ **Local oscillator power**: Design specifies 1% of 10mW seed = 100μW → ~6×10⁵ photons/ns. Code calculates this correctly but then multiplies by arbitrary 1e-9 factor, reducing to 0.306 photons total. This breaks homodyne detection.

✓ **Beam splitter**: Code correctly implements 50:50 BS with H = θ(a†b + ab†), U = exp(-iH)

✓ **Phase scanning**: Code properly rotates LO phase using exp(iφn) operator

✗ **Homodyne measurement**: Design expects strong LO limit where photocurrent difference I∝X_signal (signal quadrature). Code uses I=n_a-n_b (correct) but normalizes by 4|α|² with |α|²≈0.3 instead of ~10⁶. This is like measuring voltage with voltmeter set to wrong scale by factor of million.

✗ **Expected squeezing**: Design expects 3-6 dB (factor 2-4 variance reduction) for 80% threshold with realistic losses. Code reports 68.8 dB (factor 7.6×10⁶) - violates thermodynamics and uncertainty principle.

✗ **Homodyne visibility**: Design expects >90% with good mode matching. Code shows 1.4% - confirms LO too weak to interfere.

**Missing Physics:**
- No cavity dynamics (pump driving, losses, threshold behavior)
- No temporal mode structure (mode matching requires temporal AND spatial overlap)
- No frequency dependence (spectrum analyzer measures specific frequencies)
- No phase noise (PDH lock prevents slow drifts, not quantum phase fluctuations)

**Verdict**: The simulation generates a valid squeezed state but completely fails to simulate homodyne detection due to LO power error. Results are numerically meaningless artifacts, not physics validation.

## Identified Limitations

- Fock states have no temporal structure - cannot model temporal mode matching between LO and squeezed vacuum (critical for homodyne visibility)
- Static squeezed state approximation - no cavity dynamics, pump depletion, or threshold behavior (OPO physics requires solving coupled cavity equations)
- Frequency-independent simulation - real squeezing is frequency-dependent due to cavity filtering (spectrum analyzer measures specific frequencies)
- No phase noise or decoherence - assumes perfect phase stability between pump, LO, and squeezed field (PDH locking prevents drifts but not shot-to-shot phase noise)
- LO photon number miscalculated by factor of 10⁶ - produces unphysical 68 dB squeezing and 99.99% photon conservation error
- Homodyne normalization assumes strong LO limit (|α| >> 1) but simulation has |α|² ≈ 0.3 - violates approximation
- No spatial mode structure - assumes perfect mode matching (real experiments limited by mode overlap integral)
- Static impedance matching check - real cavity coupling changes with intracavity power and thermal effects

## Recommendations

1. Fix the squeezing calculation: For r=0.045, squeezing should be 10*log10(exp(-2r)) ≈ -0.39 dB, not 68 dB. Check for unit errors or incorrect formulas.
2. Correct antisqueezing formula: It must be positive (10*log10(exp(2r))) and satisfy the uncertainty principle. Negative antisqueezing violates quantum mechanics.
3. Improve homodyne detection model: Visibility of 1.4% suggests complete loss of phase coherence. Implement proper local oscillator phase locking and mode matching (target >95% visibility).
4. Debug photon number calculations: Near-100% conservation error indicates the photon counting or normalization is fundamentally broken.

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
