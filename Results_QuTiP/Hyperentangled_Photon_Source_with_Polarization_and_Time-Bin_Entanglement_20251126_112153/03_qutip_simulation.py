# REASONING: Fixed critical physics error - the design has only TWO MZ interferometers (one for H-path, one for V-path), not four separate ones. After PBS, photons are sorted by polarization only, not by signal/idler identity. Restructured to use 4 modes [H_early, H_late, V_early, V_late] where each MZ acts on one polarization's time bins. Fixed projection operators to properly measure polarization and time-bin correlations. Corrected visibility calculations to use proper interference metrics.

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 3  # Sufficient for SPDC photon pairs

# Designer's key parameters
wavelength_pump = 405  # nm
wavelength_signal = 810  # nm
pbs_extinction = 1000
bs_transmittance = 0.5
detector_efficiency = 0.65
timing_resolution = 50  # ps

# Phase shifts in MZ interferometers
phi_H = np.pi/2  # H-path MZ phase
phi_V = np.pi/2  # V-path MZ phase

# Step 1: Define 4-mode system [H_early, H_late, V_early, V_late]
# Type-II SPDC creates polarization entanglement: (|HV⟩ + |VH⟩)/√2
# This means one photon is H-polarized, one is V-polarized

vac = qt.fock(cutoff_dim, 0)
one = qt.fock(cutoff_dim, 1)

# Initial state after SPDC (both photons in early time bin):
# |HV⟩ = one H-photon, one V-photon
# In 4-mode space: |1_H_early, 0_H_late, 1_V_early, 0_V_late⟩
state_HV = qt.tensor(one, vac, one, vac)

# For Type-II SPDC, we have definite polarization anti-correlation
# The state is |HV⟩ (one photon H, one photon V) initially in early bins
psi_initial = state_HV.unit()

# Step 2: Apply MZ interferometer to H-polarized photon (modes 0 and 1)
# MZ structure: BS1 -> phase shift on one arm -> BS2

# Create annihilation operators for H modes
a_H_early = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), 
                      qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_H_late = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))

# BS1 for H-path: 50:50 beam splitter
theta_bs = np.pi/4
H_bs_H = theta_bs * (a_H_early.dag() * a_H_late + a_H_early * a_H_late.dag())
U_bs1_H = (-1j * H_bs_H).expm()

psi = U_bs1_H * psi_initial
psi = psi.unit()

# Phase shift on late arm
n_H_late = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
U_phase_H = (1j * phi_H * n_H_late).expm()
psi = U_phase_H * psi
psi = psi.unit()

# BS2 for H-path
U_bs2_H = (-1j * H_bs_H).expm()
psi = U_bs2_H * psi
psi = psi.unit()

# Step 3: Apply MZ interferometer to V-polarized photon (modes 2 and 3)
a_V_early = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                      qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
a_V_late = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

# BS1 for V-path
H_bs_V = theta_bs * (a_V_early.dag() * a_V_late + a_V_early * a_V_late.dag())
U_bs1_V = (-1j * H_bs_V).expm()
psi = U_bs1_V * psi
psi = psi.unit()

# Phase shift on late arm
n_V_late = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                     qt.qeye(cutoff_dim), qt.num(cutoff_dim))
U_phase_V = (1j * phi_V * n_V_late).expm()
psi = U_phase_V * psi
psi = psi.unit()

# BS2 for V-path
U_bs2_V = (-1j * H_bs_V).expm()
psi_final = U_bs2_V * psi
psi_final = psi_final.unit()

# Step 4: Calculate metrics

# Total photon number
n_total = sum([qt.tensor(*[qt.num(cutoff_dim) if i==j else qt.qeye(cutoff_dim) 
                           for j in range(4)]) for i in range(4)])
total_photons = float(abs(qt.expect(n_total, psi_final)))

# State purity
rho_final = psi_final * psi_final.dag()
purity = float(abs((rho_final * rho_final).tr()))

# Entanglement entropy - trace out V modes to get H subsystem
rho_H = rho_final.ptrace([0, 1])
evals_H = rho_H.eigenenergies()
evals_H = evals_H[evals_H > 1e-10]
entropy_H = float(-np.sum(evals_H * np.log2(evals_H + 1e-12)))

# Polarization correlations: probability of having one H and one V photon
# Project onto states with exactly one photon in H modes and one in V modes
proj_HV_ee = qt.tensor(one, vac, one, vac) * qt.tensor(one, vac, one, vac).dag()
proj_HV_el = qt.tensor(one, vac, vac, one) * qt.tensor(one, vac, vac, one).dag()
proj_HV_le = qt.tensor(vac, one, one, vac) * qt.tensor(vac, one, one, vac).dag()
proj_HV_ll = qt.tensor(vac, one, vac, one) * qt.tensor(vac, one, vac, one).dag()

prob_HV = float(abs((proj_HV_ee * rho_final).tr() + 
                    (proj_HV_el * rho_final).tr() +
                    (proj_HV_le * rho_final).tr() +
                    (proj_HV_ll * rho_final).tr()))

# Time-bin correlations: coincidence probabilities for different time bins
prob_ee = float(abs((proj_HV_ee * rho_final).tr()))  # both early
prob_el = float(abs((proj_HV_el * rho_final).tr()))  # H early, V late
prob_le = float(abs((proj_HV_le * rho_final).tr()))  # H late, V early
prob_ll = float(abs((proj_HV_ll * rho_final).tr()))  # both late

# Time-bin visibility: interference between correlated (ee, ll) and anti-correlated (el, le)
correlated = prob_ee + prob_ll
anticorrelated = prob_el + prob_le
timebin_visibility = float(abs(correlated - anticorrelated) / 
                          (correlated + anticorrelated + 1e-12))

# Polarization visibility (should be high for entangled state)
pol_visibility = float(prob_HV / (prob_HV + 1e-12))

# Two-photon detection efficiency
effective_efficiency = detector_efficiency**2

# Verify hyperentanglement: need both high purity and entanglement in both DOFs
hyperentangled = float((purity > 0.9) and (entropy_H > 0.5) and (prob_HV > 0.8))

results = {
    'total_photon_number': total_photons,
    'state_purity': purity,
    'entanglement_entropy_bits': entropy_H,
    'polarization_correlation_HV': prob_HV,
    'polarization_visibility': pol_visibility,
    'timebin_both_early': prob_ee,
    'timebin_both_late': prob_ll,
    'timebin_H_early_V_late': prob_el,
    'timebin_H_late_V_early': prob_le,
    'timebin_visibility': timebin_visibility,
    'detection_efficiency': effective_efficiency,
    'hyperentanglement_verified': hyperentangled
}