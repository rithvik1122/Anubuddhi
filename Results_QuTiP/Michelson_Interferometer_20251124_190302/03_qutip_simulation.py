# REASONING: Fixed beam splitter recombination physics - returning beams must use adjoint operation U_bs.dag() since they interact with beam splitter from opposite direction

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 8  # Sufficient for coherent state simulation
wavelength = 632.8e-9  # HeNe laser wavelength in meters
power = 5e-3  # 5 mW laser power
beam_expansion = 3  # Beam expander magnification
transmittance = 0.5  # 50:50 beam splitter
reflectivity = 0.99  # Mirror reflectivity

# Calculate coherent state amplitude from laser power
# Approximate photon number from power: n ≈ P*λ/(h*c) * time_scale
h_bar = 1.055e-34
c = 3e8
photon_energy = h_bar * 2 * np.pi * c / wavelength
# Use normalized amplitude for coherent state
alpha = 2.0  # Coherent state amplitude (reasonable for mW laser)

# Step 1: Create initial coherent state from HeNe laser
# Two-mode system: transmission arm (mode 0) and reflection arm (mode 1)
coherent_input = qt.coherent(cutoff_dim, alpha)
vacuum_mode = qt.fock(cutoff_dim, 0)
initial_state = qt.tensor(coherent_input, vacuum_mode)
initial_state = initial_state.unit()

# Step 2: Beam expander (affects beam size but not quantum state significantly)
# In quantum simulation, this mainly affects mode matching - no change to state
state_after_expander = initial_state

# Step 3: 50:50 beam splitter at 45 degrees
# Split coherent beam between transmission (to M1) and reflection (to M2) arms
theta_bs = np.pi/4  # 50:50 beam splitter angle
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))  # Mode 0 (transmission arm)
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))  # Mode 1 (reflection arm)
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()

state_after_bs = U_bs * state_after_expander
state_after_bs = state_after_bs.unit()

# Step 4: Propagation to mirrors and back (include losses from imperfect reflectivity)
# Fixed mirror M1 (transmission arm) - reflectivity 0.99
loss_m1 = np.sqrt(reflectivity)
# Movable mirror M2 (reflection arm) - reflectivity 0.99  
loss_m2 = np.sqrt(reflectivity)

# Apply mirror losses
loss_op = qt.tensor(loss_m1 * qt.qeye(cutoff_dim), loss_m2 * qt.qeye(cutoff_dim))
state_after_mirrors = loss_op * state_after_bs
state_after_mirrors = state_after_mirrors.unit()

# Step 5: Phase shift from movable mirror M2 (piezo mirror)
# Test two different positions to demonstrate fringe shifting
phase_shift_0 = 0  # Reference position
phase_shift_pi = np.pi  # Shifted position (λ/2 displacement)

# Phase shift applied only to reflection arm (mode 1)
phase_op_0 = qt.tensor(qt.qeye(cutoff_dim), (1j * phase_shift_0 * qt.num(cutoff_dim)).expm())
phase_op_pi = qt.tensor(qt.qeye(cutoff_dim), (1j * phase_shift_pi * qt.num(cutoff_dim)).expm())

# Step 6: Recombination at beam splitter
# CRITICAL FIX: Use adjoint operation for returning beams from opposite direction
state_phase_0 = U_bs.dag() * (phase_op_0 * state_after_mirrors)
state_phase_0 = state_phase_0.unit()

state_phase_pi = U_bs.dag() * (phase_op_pi * state_after_mirrors)
state_phase_pi = state_phase_pi.unit()

# Step 7: Detection at interference screen
# Measure photon number in output mode (mode 0 goes to screen)
n_screen = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_other = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))

# Intensity measurements at two phase positions
intensity_phase_0 = float(abs(qt.expect(n_screen, state_phase_0)))
intensity_phase_pi = float(abs(qt.expect(n_screen, state_phase_pi)))

# Also measure the other output for energy conservation check
intensity_other_0 = float(abs(qt.expect(n_other, state_phase_0)))
intensity_other_pi = float(abs(qt.expect(n_other, state_phase_pi)))

# Step 8: Calculate interference metrics
# Visibility (fringe contrast) - key metric for interferometer performance
I_max = max(intensity_phase_0, intensity_phase_pi)
I_min = min(intensity_phase_0, intensity_phase_pi)
visibility = float((I_max - I_min) / (I_max + I_min + 1e-12))

# Energy conservation check
total_energy_0 = intensity_phase_0 + intensity_other_0
total_energy_pi = intensity_phase_pi + intensity_other_pi
energy_conservation = float(abs(total_energy_0 - total_energy_pi) / (total_energy_0 + 1e-12))

# Phase sensitivity - how much intensity changes with phase
phase_sensitivity = float(abs(intensity_phase_pi - intensity_phase_0) / (np.pi + 1e-12))

# Coherence measure - purity of the output states
purity_0 = float(abs(((state_phase_0 * state_phase_0.dag()).tr()).real))
purity_pi = float(abs(((state_phase_pi * state_phase_pi.dag()).tr()).real))

# Store results validating designer's claims
results = {
    'fringe_contrast_achieved': float(visibility > 0.1),  # Boolean metric for success
    'visibility': visibility,
    'phase_sensitivity': phase_sensitivity,
    'energy_conservation_error': energy_conservation,
    'output_purity_average': float((purity_0 + purity_pi) / 2),
    'intensity_contrast_ratio': float(I_max / (I_min + 1e-12)),
    'total_detected_photons': float(total_energy_0)
}