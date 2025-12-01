# REASONING: Fixed critical issues - added missing data collection in phase loop, corrected theoretical visibility formula for coherent states, completed energy conservation check, and ensured all results are properly stored

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 5  # Adequate for coherent state simulation
wavelength = 632.8  # nm (He-Ne laser)
power = 5  # mW
transmittance = 0.5  # 50:50 beam splitters
detector_efficiency = 0.85
phase_range = 6.28  # 2π radians

# Calculate coherent state amplitude from laser power
# For demonstration, use moderate coherent amplitude
alpha = 2.0  # Coherent state parameter

# Step 1: Create initial coherent laser state in two-mode system
# Mode 0: input beam, Mode 1: initially vacuum (for beam splitter operation)
coherent_state = qt.coherent(cutoff_dim, alpha)
vacuum_state = qt.fock(cutoff_dim, 0)
initial_state = qt.tensor(coherent_state, vacuum_state)
initial_state = initial_state.unit()

# Step 2: First beam splitter (Input BS) - 50:50 splitting
theta_bs = np.pi/4  # 50:50 beam splitter angle
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))  # Mode 0 annihilation
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))  # Mode 1 annihilation
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
state_after_bs1 = U_bs1 * initial_state
state_after_bs1 = state_after_bs1.unit()

# Step 3: Apply phase shifter to upper path (mode 1)
# Test multiple phases to calculate visibility
phases = [0, np.pi/2, np.pi, 3*np.pi/2]
detector1_outputs = []
detector2_outputs = []

for phi in phases:
    # Phase shift on mode 1 (upper path)
    phase_op = qt.tensor(qt.qeye(cutoff_dim), (1j * phi * qt.num(cutoff_dim)).expm())
    state_with_phase = phase_op * state_after_bs1
    state_with_phase = state_with_phase.unit()
    
    # Step 4: Second beam splitter (Output BS) - recombination
    U_bs2 = (-1j * H_bs).expm()
    final_state = U_bs2 * state_with_phase
    final_state = final_state.unit()
    
    # Step 5: Measure photon numbers at detectors
    n_mode0 = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))  # Detector 1
    n_mode1 = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))  # Detector 2
    
    output1 = float(abs(qt.expect(n_mode0, final_state))) * detector_efficiency
    output2 = float(abs(qt.expect(n_mode1, final_state))) * detector_efficiency
    
    # FIXED: Actually store the calculated outputs
    detector1_outputs.append(output1)
    detector2_outputs.append(output2)

# Calculate visibility for interference verification
I_max_det1 = max(detector1_outputs)
I_min_det1 = min(detector1_outputs)
visibility_det1 = float((I_max_det1 - I_min_det1) / (I_max_det1 + I_min_det1 + 1e-12))

I_max_det2 = max(detector2_outputs)
I_min_det2 = min(detector2_outputs)
visibility_det2 = float((I_max_det2 - I_min_det2) / (I_max_det2 + I_min_det2 + 1e-12))

# Verify energy conservation
total_energy_initial = float(abs(qt.expect(qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim)) + qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim)), initial_state)))
total_energy_final = detector1_outputs[0] + detector2_outputs[0]  # At phase = 0

# FIXED: Correct theoretical expectation for coherent state interference
# For coherent states in Mach-Zehnder, visibility approaches 1 for ideal conditions
theoretical_visibility = 1.0

# Verify superposition by checking state purity after first beam splitter
rho_after_bs1 = state_after_bs1 * state_after_bs1.dag()
purity = float(abs((rho_after_bs1 * rho_after_bs1).tr()))

# Store results
results = {
    'detector1_outputs': detector1_outputs,
    'detector2_outputs': detector2_outputs,
    'visibility_detector1': visibility_det1,
    'visibility_detector2': visibility_det2,
    'theoretical_visibility': theoretical_visibility,
    'energy_initial': total_energy_initial,
    'energy_final': total_energy_final,
    'energy_conservation_error': float(abs(total_energy_initial - total_energy_final)),
    'state_purity_after_bs1': purity,
    'coherent_amplitude': float(abs(alpha)),
    'phases_tested': phases,
    'beam_splitter_angle': float(theta_bs),
    'detector_efficiency': detector_efficiency
}