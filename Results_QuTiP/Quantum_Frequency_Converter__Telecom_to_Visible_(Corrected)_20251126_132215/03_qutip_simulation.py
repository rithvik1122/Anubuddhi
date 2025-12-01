import qutip as qt
import numpy as np

# ═══════════════════════════════════════════════════════════
# EXTRACT PARAMETERS FROM DESIGNER'S SPECIFICATION
# ═══════════════════════════════════════════════════════════

# Wavelengths (nm)
lambda_signal = 1550  # Telecom single photon
lambda_pump = 980     # Strong pump laser
lambda_sfg = 600.4    # Expected SFG output

# Verify energy conservation for SFG
lambda_sfg_calculated = 1 / (1/lambda_signal + 1/lambda_pump)
energy_conservation_check = abs(lambda_sfg_calculated - lambda_sfg) < 1.0

# Component parameters
fiber_input_efficiency = 0.85
pump_power_mw = 500
ppln_length_mm = 20
ppln_poling_period_um = 19.2
ppln_temperature_c = 95
fiber_output_efficiency = 0.75
detector_efficiency = 0.75

# Quantum system parameters
cutoff_dim = 5
alpha_pump = 10.0  # Strong coherent pump amplitude
coupling_strength = 0.3  # SFG coupling (chi^(2) nonlinearity)
interaction_time = 1.0  # Normalized interaction time

# ═══════════════════════════════════════════════════════════
# STEP 1: INITIALIZE QUANTUM STATES
# ═══════════════════════════════════════════════════════════

# Three-mode system: signal (1550nm), pump (980nm), SFG output (600.4nm)
signal_state = qt.fock(cutoff_dim, 1)  # Single photon
pump_state = qt.coherent(cutoff_dim, alpha_pump)  # Strong pump
sfg_state = qt.fock(cutoff_dim, 0)  # Vacuum

# Combined initial state (tensor product)
psi_initial = qt.tensor(signal_state, pump_state, sfg_state)

# ═══════════════════════════════════════════════════════════
# STEP 2: DEFINE SUM-FREQUENCY GENERATION HAMILTONIAN
# ═══════════════════════════════════════════════════════════

# Operators for each mode
a_signal = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_pump = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
a_sfg = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

# SFG Hamiltonian: H = g * (a_sfg^† * a_signal * a_pump + h.c.)
H_sfg = coupling_strength * (a_sfg.dag() * a_signal * a_pump + a_sfg * a_signal.dag() * a_pump.dag())

# ═══════════════════════════════════════════════════════════
# STEP 3: TIME EVOLUTION
# ═══════════════════════════════════════════════════════════

# Evolve under SFG Hamiltonian
U = (-1j * H_sfg * interaction_time).expm()
psi_final = U * psi_initial

# ═══════════════════════════════════════════════════════════
# STEP 4: MEASUREMENTS AND ANALYSIS
# ═══════════════════════════════════════════════════════════

# Number operators
n_signal = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
n_pump = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_sfg = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.num(cutoff_dim))

# Expectation values
signal_photons_initial = qt.expect(n_signal, psi_initial)
sfg_photons_initial = qt.expect(n_sfg, psi_initial)

signal_photons_final = qt.expect(n_signal, psi_final)
pump_photons_final = qt.expect(n_pump, psi_final)
sfg_photons_final = qt.expect(n_sfg, psi_final)

# Conversion efficiency (signal → SFG)
conversion_efficiency = sfg_photons_final / max(signal_photons_initial, 1e-10)

# Account for system losses
total_efficiency = (fiber_input_efficiency * conversion_efficiency * 
                   fiber_output_efficiency * detector_efficiency)

# Fidelity check: probability of single photon in SFG mode
rho_final = psi_final * psi_final.dag()
rho_sfg = rho_final.ptrace(2)  # Trace out signal and pump modes
sfg_single_photon_state = qt.fock(cutoff_dim, 1)
fidelity_sfg = qt.fidelity(rho_sfg, sfg_single_photon_state)

# Photon number variance (quantum statistics preservation)
n_sfg_sq = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.num(cutoff_dim)**2)
sfg_variance = qt.expect(n_sfg_sq, psi_final) - sfg_photons_final**2

# Second-order coherence g2(0) for SFG output
if sfg_photons_final > 1e-6:
    g2_sfg = (qt.expect(n_sfg_sq, psi_final) - sfg_photons_final) / (sfg_photons_final**2)
else:
    g2_sfg = 0.0

results = {
    "energy_conservation_satisfied": float(energy_conservation_check),
    "calculated_sfg_wavelength_nm": float(lambda_sfg_calculated),
    "signal_photons_initial": float(signal_photons_initial.real),
    "signal_photons_final": float(signal_photons_final.real),
    "sfg_photons_final": float(sfg_photons_final.real),
    "conversion_efficiency": float(conversion_efficiency.real),
    "total_system_efficiency": float(total_efficiency.real),
    "sfg_single_photon_fidelity": float(fidelity_sfg.real),
    "sfg_photon_variance": float(sfg_variance.real),
    "sfg_g2_coherence": float(g2_sfg.real),
    "detected_photon_rate": float((total_efficiency * signal_photons_initial).real)
}