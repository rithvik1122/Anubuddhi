# REASONING: Validating designer's unbalanced Mach-Zehnder interferometer with asymmetric path lengths and variable delay stage

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 5
wavelength = 632.8e-9  # HeNe laser wavelength in meters
laser_power = 5e-3  # 5 mW
transmittance = 0.5  # 50:50 beam splitters
detector_efficiency = 0.85

# Calculate path lengths from component positions
# Upper path: (1,3) -> (3,3) -> (5,5) -> (7,5) -> (8.5,3) -> (9.5,4)
upper_segments = [
    np.sqrt((3-1)**2 + (3-3)**2),  # Laser to Input BS
    np.sqrt((5-3)**2 + (5-3)**2),  # Input BS to Upper Mirror
    np.sqrt((7-5)**2 + (5-5)**2),  # Upper Mirror to Delay Stage
    np.sqrt((8.5-7)**2 + (3-5)**2),  # Delay Stage to Output BS
    np.sqrt((9.5-8.5)**2 + (4-3)**2)  # Output BS to Detector 1
]
upper_path_length = sum(upper_segments)

# Lower path: (1,3) -> (3,3) -> (4.5,1) -> (6.5,1) -> (8.5,3) -> (8.5,1.5)
lower_segments = [
    np.sqrt((3-1)**2 + (3-3)**2),  # Laser to Input BS
    np.sqrt((4.5-3)**2 + (1-3)**2),  # Input BS to Lower Mirror 1
    np.sqrt((6.5-4.5)**2 + (1-1)**2),  # Lower Mirror 1 to Lower Mirror 2
    np.sqrt((8.5-6.5)**2 + (3-1)**2),  # Lower Mirror 2 to Output BS
    np.sqrt((8.5-8.5)**2 + (1.5-3)**2)  # Output BS to Detector 2
]
lower_path_length = sum(lower_segments)

# Path length difference
path_difference = lower_path_length - upper_path_length
base_phase_diff = 2 * np.pi * path_difference / wavelength

# Step 1: Create initial coherent state (approximating laser)
# Use weak coherent state with mean photon number ~0.1 for quantum regime
alpha = np.sqrt(0.1)
initial_state = qt.tensor(qt.coherent(cutoff_dim, alpha), qt.fock(cutoff_dim, 0))
initial_state = initial_state.unit()

# Step 2: Input beam splitter (50:50, cube type)
theta_bs = np.pi/4  # 50:50 beam splitter angle
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_input_bs = (-1j * H_bs).expm()
state_after_split = U_input_bs * initial_state
state_after_split = state_after_split.unit()

# Step 3: Apply path length difference phase shift to upper arm (mode 0)
# Test multiple delay stage positions to demonstrate interference
delay_positions = [0, 25, 50, 75, 100]  # micrometers
visibilities = []
intensities_det1 = []
intensities_det2 = []

for delay_um in delay_positions:
    delay_m = delay_um * 1e-6  # Convert to meters
    total_phase = base_phase_diff + 2 * np.pi * delay_m / wavelength
    
    # Apply phase shift to upper arm (mode 0)
    phase_op = qt.tensor((1j * total_phase * qt.num(cutoff_dim)).expm(), qt.qeye(cutoff_dim))
    state_with_phase = phase_op * state_after_split
    state_with_phase = state_with_phase.unit()
    
    # Step 4: Output beam splitter (recombination)
    U_output_bs = (-1j * H_bs).expm()
    final_state = U_output_bs * state_with_phase
    final_state = final_state.unit()
    
    # Step 5: Measure at detectors with efficiency
    n_mode0 = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))  # Detector 1 path
    n_mode1 = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))  # Detector 2 path
    
    intensity_1 = float(abs(qt.expect(n_mode0, final_state))) * detector_efficiency
    intensity_2 = float(abs(qt.expect(n_mode1, final_state))) * detector_efficiency
    
    intensities_det1.append(intensity_1)
    intensities_det2.append(intensity_2)

# Calculate visibility from detector 1 measurements
I_max_det1 = max(intensities_det1)
I_min_det1 = min(intensities_det1)
visibility_det1 = float((I_max_det1 - I_min_det1) / (I_max_det1 + I_min_det1 + 1e-12))

# Calculate visibility from detector 2 measurements
I_max_det2 = max(intensities_det2)
I_min_det2 = min(intensities_det2)
visibility_det2 = float((I_max_det2 - I_min_det2) / (I_max_det2 + I_min_det2 + 1e-12))

# Verify energy conservation
total_intensities = [i1 + i2 for i1, i2 in zip(intensities_det1, intensities_det2)]
energy_conservation = float(np.std(total_intensities) / np.mean(total_intensities))

# Test specific phase points for theoretical verification
# Phase = 0 case
phase_0_op = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
state_phase_0 = U_output_bs * (phase_0_op * state_after_split)
state_phase_0 = state_phase_0.unit()
intensity_0_det1 = float(abs(qt.expect(n_mode0, state_phase_0))) * detector_efficiency
intensity_0_det2 = float(abs(qt.expect(n_mode1, state_phase_0))) * detector_efficiency

# Phase = π case
phase_pi_op = qt.tensor((1j * np.pi * qt.num(cutoff_dim)).expm(), qt.qeye(cutoff_dim))
state_phase_pi = U_output_bs * (phase_pi_op * state_after_split)
state_phase_pi = state_phase_pi.unit()
intensity_pi_det1 = float(abs(qt.expect(n_mode0, state_phase_pi))) * detector_efficiency
intensity_pi_det2 = float(abs(qt.expect(n_mode1, state_phase_pi))) * detector_efficiency

# Verify complementary behavior (anti-correlation)
complementarity = float(abs((intensity_0_det1 - intensity_pi_det1) + (intensity_pi_det2 - intensity_0_det2)) / 
                       (intensity_0_det1 + intensity_pi_det1 + 1e-12))

# Calculate theoretical visibility for coherent state
coherence_factor = np.exp(-abs(alpha)**2) * abs(alpha)**2  # |α|²e^(-|α|²) for n=1 term
theoretical_visibility = float(2 * coherence_factor / (1 + coherence_factor))

results = {
    'path_length_difference_um': float(path_difference * 1e6),
    'base_phase_difference_rad': float(base_phase_diff),
    'visibility_detector1': visibility_det1,
    'visibility_detector2': visibility_det2,
    'energy_conservation_error': energy_conservation,
    'intensity_phase0_det1': intensity_0_det1,
    'intensity_phase0_det2': intensity_0_det2,
    'intensity_phasepi_det1': intensity_pi_det1,
    'intensity_phasepi_det2': intensity_pi_det2,
    'complementarity_factor': complementarity,
    'theoretical_visibility': theoretical_visibility,
    'mean_photon_number': float(abs(alpha)**2),
    'detector_efficiency': detector_efficiency,
    'max_intensity_det1': I_max_det1,
    'min_intensity_det1': I_min_det1
}