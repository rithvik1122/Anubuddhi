# REASONING: Fixed broken measurement operators by properly constructing projection operators for coincidence and bunching detection, applied detector efficiency, and used correct probability calculations instead of photon number expectation values

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 3  # For two-photon states
pump_wavelength = 405  # nm
signal_idler_wavelength = 810  # nm (from filters)
filter_bandwidth = 10  # nm
bs_transmittance = 0.5  # 50:50 beam splitter
detector_efficiency = 0.65

# Step 1: Create initial SPDC state (Type-I phase matching produces identical polarizations)
# SPDC creates entangled photon pairs: |0,0⟩ + α|1,1⟩ (signal, idler modes)
# For Hong-Ou-Mandel, we need the two-photon component
vacuum = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 0))
two_photon = qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1))

# SPDC state (simplified): focus on two-photon component for HOM
spdc_amplitude = 0.1  # Small probability amplitude
state = (np.sqrt(1 - spdc_amplitude**2) * vacuum + spdc_amplitude * two_photon).unit()

# Step 2: Apply spectral filtering (reduces amplitude but maintains indistinguishability)
# Bandpass filters with 10nm bandwidth - model as amplitude reduction
filter_transmission = 0.8  # Realistic filter transmission
state = (np.sqrt(filter_transmission) * state).unit()

# Step 3: Variable delay stage - test at zero delay (perfect HOM condition)
# At zero delay, photons are temporally indistinguishable
delay_phase = 0  # Zero delay for maximum interference

# Step 4: Beam splitter operation (50:50 cube beam splitter)
# For HOM: two photons in separate input modes, observe outputs
# Input state: |1,1⟩ (one photon in each input port)
# BS transformation: H = θ(a†b + ab†) where θ = π/4 for 50:50
theta_bs = np.pi/4

# Define operators for two-mode system
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))  # Mode A (signal path)
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))  # Mode B (idler path)

# Beam splitter Hamiltonian and unitary
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()

# Apply beam splitter to the two-photon state
state_after_bs = (U_bs * two_photon).unit()

# Step 5: Detection and coincidence measurement
# Define photon number operators for each output port
n_a = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))  # Detector 1
n_b = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))  # Detector 2

# Calculate average photon numbers
avg_photons_a = float(abs(qt.expect(n_a, state_after_bs)))
avg_photons_b = float(abs(qt.expect(n_b, state_after_bs)))

# Proper measurement operators for discrete detection events
# Coincidence detection: probability of detecting one photon in each detector
coincidence_state = qt.tensor(qt.fock(cutoff_dim, 1), qt.fock(cutoff_dim, 1))
coincidence_op = coincidence_state * coincidence_state.dag()
prob_coincidence = float(abs(qt.expect(coincidence_op, state_after_bs)))

# Bunching probabilities (both photons in same output)
both_a_state = qt.tensor(qt.fock(cutoff_dim, 2), qt.fock(cutoff_dim, 0))
both_b_state = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 2))
both_a_op = both_a_state * both_a_state.dag()
both_b_op = both_b_state * both_b_state.dag()

prob_both_a = float(abs(qt.expect(both_a_op, state_after_bs)))
prob_both_b = float(abs(qt.expect(both_b_op, state_after_bs)))

# Apply detector efficiency to all detection probabilities
prob_coincidence_detected = detector_efficiency**2 * prob_coincidence  # Both detectors must fire
prob_both_a_detected = detector_efficiency * prob_both_a  # Only detector A fires twice
prob_both_b_detected = detector_efficiency * prob_both_b  # Only detector B fires twice

# For ideal HOM: coincidence probability should be 0, bunching probability should be 0.5 each
total_detection_prob = prob_both_a_detected + prob_both_b_detected + prob_coincidence_detected

# HOM visibility: measure at different delays to see interference
# At zero delay (perfect indistinguishability)
visibility_zero_delay = prob_both_a_detected + prob_both_b_detected

# Simulate non-zero delay (distinguishable photons) - no interference
# Classical expectation: 0.25 probability for each outcome
classical_coincidence = 0.25
classical_bunching = 0.5

# HOM dip visibility
hom_visibility = float(abs(classical_coincidence - prob_coincidence_detected) / (classical_coincidence + prob_coincidence_detected + 1e-12))

# Photon number conservation check
total_photons_in = 2.0  # Two input photons
total_photons_out = float(avg_photons_a + avg_photons_b)

# Calculate key HOM metrics
# For perfect HOM interference with indistinguishable photons:
# - Coincidence probability = 0
# - Bunching probability = 1 (split equally between outputs)
coincidence_suppression = float(1.0 - prob_coincidence_detected / (classical_coincidence + 1e-12))

# State analysis
state_norm = float(abs(state_after_bs.norm()))
state_purity = float(abs((state_after_bs * state_after_bs.dag()).tr()))

results = {
    'coincidence_probability': prob_coincidence_detected,
    'bunching_probability_a': prob_both_a_detected,
    'bunching_probability_b': prob_both_b_detected,
    'total_detection_probability': total_detection_prob,
    'hom_visibility': hom_visibility,
    'coincidence_suppression': coincidence_suppression,
    'photon_conservation': total_photons_out / total_photons_in,
    'avg_photons_detector_a': avg_photons_a,
    'avg_photons_detector_b': avg_photons_b,
    'state_normalization': state_norm,
    'state_purity': state_purity,
    'detector_efficiency': detector_efficiency,
    'filter_transmission': filter_transmission
}