# REASONING: Fixed homodyne detection measurement to use balanced photocurrent difference operator instead of single-mode quadrature. The original code measured mode A quadrature variance which is dominated by LO shot noise. Corrected to measure (n_a - n_b) difference operator which cancels LO noise and reveals squeezing. Also fixed shot noise reference to 1.0 (not 0.5) for normalized quadrature variance, added proper photon conservation check, and corrected normalization of difference photocurrent to quadrature variance using homodyne gain factor.

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 15  # Higher cutoff for squeezed states (non-classical photon statistics)

# Physical parameters from components
wavelength_seed = 1064e-9  # meters
wavelength_pump = 532e-9   # meters
power_seed = 10e-3  # 10 mW seed laser
shg_efficiency = 0.7  # Estimated SHG conversion efficiency
pump_power = power_seed * shg_efficiency  # ~7 mW pump after SHG

# OPO cavity parameters
R_ic = 0.998  # Input coupler reflectivity at 1064nm
R_m1 = 0.998  # End mirror reflectivity
cavity_losses = 0.002  # Total round-trip losses (impedance matching condition)
cavity_length = 1.0  # meters (estimated from mirror separation)
ppln_length = 10e-3  # 10mm PPLN crystal

# Calculate OPO parameters
finesse = np.pi * np.sqrt(R_ic * R_m1) / (1 - R_ic * R_m1)
fsr = 3e8 / (2 * cavity_length)  # Free spectral range
cavity_linewidth = fsr / finesse

# Nonlinear coupling strength (chi^(2) interaction)
# For PPLN at 1064nm degenerate OPO with 532nm pump
chi2_eff = 15e-12  # m/V (effective nonlinearity for PPLN)
pump_photon_flux = pump_power / (6.626e-34 * 3e8 / wavelength_pump)
coupling_strength = 0.05  # Normalized coupling (sub-threshold regime)

# Squeezing parameter (sub-threshold OPO)
pump_threshold_ratio = 0.8  # Operating at 80% of threshold (sub-threshold)
squeezing_param = coupling_strength * np.sqrt(pump_threshold_ratio)  # r parameter

# Step 1: Generate squeezed vacuum state at 1064nm from OPO
# Degenerate OPO produces single-mode squeezed vacuum
squeeze_r = squeezing_param
squeeze_phi = 0  # Squeeze phase quadrature (X quadrature)

# Create squeezed vacuum state
S = qt.squeeze(cutoff_dim, squeeze_r * np.exp(1j * squeeze_phi))
vacuum = qt.fock(cutoff_dim, 0)
squeezed_vacuum = S * vacuum
squeezed_vacuum = squeezed_vacuum.unit()

# Step 2: Local oscillator preparation
# Phase-coherent LO derived from same 1064nm seed (reflected from dichroic)
lo_power_fraction = 0.01  # 1% of seed power goes to LO path
lo_photon_rate = (power_seed * lo_power_fraction) / (6.626e-34 * 3e8 / wavelength_seed)
lo_coherent_amplitude = np.sqrt(lo_photon_rate * 1e-9)  # Normalized for coherent state

# LO coherent state (strong local oscillator)
lo_alpha = lo_coherent_amplitude
lo_state = qt.coherent(cutoff_dim, lo_alpha)
lo_state = lo_state.unit()

# Step 3: Mode matching and beam splitter interference
# Two-mode state: squeezed vacuum + LO
# Mode 0: Squeezed vacuum, Mode 1: LO
psi_combined = qt.tensor(squeezed_vacuum, lo_state)
psi_combined = psi_combined.unit()

# 50:50 beam splitter (homodyne BS)
theta_bs = np.pi / 4  # 50:50 beam splitter
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()

# Step 4: Balanced homodyne detection
# Measure difference photocurrent at different LO phases
# In strong LO limit, I_diff ∝ signal quadrature

n_a = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_b = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))

# Measure quadratures at different phases (rotate LO phase)
phases = np.linspace(0, 2*np.pi, 180)
quadrature_variances = []

for phi in phases:
    # Rotate LO phase
    phase_op = qt.tensor(qt.qeye(cutoff_dim), (1j * phi * qt.num(cutoff_dim)).expm())
    psi_phase = phase_op * psi_combined
    psi_phase = psi_phase.unit()
    psi_phase_bs = U_bs * psi_phase
    psi_phase_bs = psi_phase_bs.unit()
    
    # Balanced homodyne: difference photocurrent
    I_diff = n_a - n_b
    mean_I = qt.expect(I_diff, psi_phase_bs)
    mean_I2 = qt.expect(I_diff * I_diff, psi_phase_bs)
    var_I = abs(mean_I2 - mean_I**2)
    
    # Normalize by LO photon number for quadrature variance
    # Homodyne gain factor: 4 * |alpha|^2 for difference photocurrent
    lo_photon_number = abs(lo_alpha)**2
    if lo_photon_number > 1e-10:
        var_quadrature = var_I / (4 * lo_photon_number)
    else:
        var_quadrature = var_I
    
    quadrature_variances.append(var_quadrature)

quadrature_variances = np.array(quadrature_variances)

# Shot noise level (vacuum state variance in normalized quadrature units)
vacuum_var = 1.0  # Standard quantum limit

# Find minimum and maximum variances
min_variance = float(np.min(quadrature_variances))
max_variance = float(np.max(quadrature_variances))

# Squeezing in dB
squeezing_dB = float(-10 * np.log10(max(min_variance / vacuum_var, 1e-10)))
antisqueezing_dB = float(10 * np.log10(max(max_variance / vacuum_var, 1e-10)))

# Step 5: Calculate validation metrics
# Photon number statistics (after BS, no phase shift)
psi_after_bs = U_bs * psi_combined
psi_after_bs = psi_after_bs.unit()

mean_photons_a = float(abs(qt.expect(n_a, psi_after_bs)))
mean_photons_b = float(abs(qt.expect(n_b, psi_after_bs)))
total_photons = float(mean_photons_a + mean_photons_b)

# Input photon number (LO dominates, squeezed vacuum has ~0 mean)
input_photons = abs(lo_alpha)**2
photon_conservation_error = float(abs(total_photons - input_photons) / (input_photons + 1e-10))

# Purity of squeezed state
rho_squeezed = squeezed_vacuum * squeezed_vacuum.dag()
purity_squeezed = float(abs((rho_squeezed * rho_squeezed).tr()))

# Homodyne visibility (interference contrast)
# Measure photocurrent difference at different phases
photocurrents = []
for phi in [0, np.pi/2, np.pi, 3*np.pi/2]:
    phase_op = qt.tensor(qt.qeye(cutoff_dim), (1j * phi * qt.num(cutoff_dim)).expm())
    psi_phase = phase_op * psi_combined
    psi_phase = psi_phase.unit()
    psi_phase_bs = U_bs * psi_phase
    psi_phase_bs = psi_phase_bs.unit()
    
    I_a = abs(qt.expect(n_a, psi_phase_bs))
    I_b = abs(qt.expect(n_b, psi_phase_bs))
    photocurrents.append(I_a - I_b)

I_max = float(np.max(photocurrents))
I_min = float(np.min(photocurrents))
homodyne_visibility = float(abs((I_max - I_min) / (I_max + I_min + 1e-12)))

# Quantum efficiency and detection metrics
quantum_efficiency = 0.98  # From homodyne detector specs
detection_efficiency = 0.95  # Overall detection efficiency
effective_squeezing_dB = float(squeezing_dB - 10 * np.log10(quantum_efficiency * detection_efficiency))

# Verify impedance matching (cavity should be critically coupled)
impedance_match_ratio = float(R_ic / (R_m1 * (1 - cavity_losses)))

# Store validation results
results = {
    'squeezing_dB': squeezing_dB,
    'antisqueezing_dB': antisqueezing_dB,
    'effective_squeezing_dB': effective_squeezing_dB,
    'min_quadrature_variance': min_variance,
    'max_quadrature_variance': max_variance,
    'shot_noise_level': float(vacuum_var),
    'variance_reduction_factor': float(vacuum_var / max(min_variance, 1e-10)),
    'mean_photons_output_a': mean_photons_a,
    'mean_photons_output_b': mean_photons_b,
    'total_photon_conservation': total_photons,
    'photon_conservation_error': photon_conservation_error,
    'purity_squeezed_state': purity_squeezed,
    'homodyne_visibility': homodyne_visibility,
    'impedance_match_ratio': impedance_match_ratio,
    'pump_threshold_ratio': float(pump_threshold_ratio),
    'cavity_finesse': float(finesse),
    'squeezing_parameter_r': float(squeeze_r),
    'below_shot_noise': float(min_variance < vacuum_var)
}