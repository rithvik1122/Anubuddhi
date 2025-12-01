# REASONING: Fixed TypeError: 'complex' object is not subscriptable
# Root cause: In pbs_measurement(), the expression (H.dag() * rotated_state).tr() returns a complex scalar
# The code tried to square it with **2, but first attempted to extract real part incorrectly
# Fix: Use proper QuTiP overlap calculation with .overlap() method or extract scalar correctly
# Also ensured all probability calculations use abs() and real parts to avoid complex contamination

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
wavelength = 810  # nm
optical_depth = 10  # Variable attenuator - NOTE: Not used in ideal single-photon model
alice_fiber_efficiency = 0.8
bob_fiber_efficiency = 0.8
channel_loss_db = 10 * 0.2  # 10km * 0.2dB/km = 2dB total
channel_transmission = 10**(-channel_loss_db/10)  # Convert dB to linear
detector_efficiency = 0.65
extinction_ratio = 100000  # For both polarizer and PBS
dark_count_rate = 100  # Hz
timing_resolution = 50e-12  # 50 ps

# Polarization basis states (2-level system for H/V polarization)
# |H> = |0>, |V> = |1>
H = qt.basis(2, 0)  # Horizontal polarization
V = qt.basis(2, 1)  # Vertical polarization
D = (H + V).unit()  # Diagonal (+45°)
A = (H - V).unit()  # Anti-diagonal (-45°)

# BB84 encoding states
alice_states = {
    'H': H,  # Rectilinear basis, bit 0
    'V': V,  # Rectilinear basis, bit 1
    'D': D,  # Diagonal basis, bit 0
    'A': A   # Diagonal basis, bit 1
}

# Half-wave plate rotation operator
# HWP rotates polarization by 2*theta where theta is HWP angle
def hwp_operator(theta):
    """Half-wave plate at angle theta rotates polarization by 2*theta"""
    rotation_angle = 2 * theta
    cos_val = np.cos(rotation_angle)
    sin_val = np.sin(rotation_angle)
    # Rotation matrix in H/V basis
    hwp_matrix = np.array([[cos_val, sin_val],
                           [sin_val, -cos_val]])
    return qt.Qobj(hwp_matrix)

# Polarizing beam splitter measurement operators with finite extinction ratio
def pbs_measurement(state, hwp_angle, extinction_ratio):
    """Apply HWP rotation then measure in H/V basis with finite extinction ratio"""
    # Apply Bob's basis selector HWP
    hwp = hwp_operator(hwp_angle)
    rotated_state = hwp * state
    rotated_state = rotated_state.unit()
    
    # Ideal measurement probabilities for H (detector 0) and V (detector 1)
    # Use overlap method to get proper scalar value
    overlap_H = H.overlap(rotated_state)
    overlap_V = V.overlap(rotated_state)
    
    ideal_prob_H = abs(overlap_H)**2
    ideal_prob_V = abs(overlap_V)**2
    
    # Apply cross-talk from finite extinction ratio
    # PBS with extinction ratio R means orthogonal polarization leaks with probability 1/R
    cross_talk = 1.0 / extinction_ratio
    prob_H = ideal_prob_H * (1.0 - cross_talk) + ideal_prob_V * cross_talk
    prob_V = ideal_prob_V * (1.0 - cross_talk) + ideal_prob_H * cross_talk
    
    return float(prob_H), float(prob_V)

# Simulate BB84 protocol statistics
# Alice prepares each of 4 states, Bob measures in each of 2 bases
alice_encoding_angles = {
    'H': 0,           # HWP at 0° → H polarization
    'V': np.pi/4,     # HWP at 45° → V polarization
    'D': np.pi/8,     # HWP at 22.5° → D polarization
    'A': -np.pi/8     # HWP at -22.5° → A polarization
}

bob_basis_angles = {
    'rectilinear': 0,      # HWP at 0° → measure in H/V basis
    'diagonal': np.pi/8    # HWP at 22.5° → measure in D/A basis
}

# Calculate total transmission efficiency
total_efficiency = (alice_fiber_efficiency * 
                   channel_transmission * 
                   bob_fiber_efficiency * 
                   detector_efficiency)

# Dark count probability per measurement
# Assume measurement gate window of 1 ns (typical for gated SPADs in QKD)
measurement_window = 1e-9  # 1 ns gate window
dark_count_prob = dark_count_rate * measurement_window  # Probability of dark count per gate

# Simulate protocol for all state/basis combinations
results_matrix = {}
matching_basis_correlations = []
mismatched_basis_results = []

for alice_prep, alice_angle in alice_encoding_angles.items():
    # Step 1: Alice prepares state
    # Start with H polarization (after input polarizer with extinction ratio)
    initial_state = H
    
    # Apply Alice's encoding HWP
    alice_hwp = hwp_operator(alice_angle)
    encoded_state = alice_hwp * initial_state
    encoded_state = encoded_state.unit()
    
    # Step 2: Transmission through quantum channel
    # Model as amplitude damping (photon loss)
    # State remains pure but with reduced detection probability
    transmitted_state = encoded_state  # Polarization preserved in single-mode fiber
    
    for bob_basis, bob_angle in bob_basis_angles.items():
        # Step 3: Bob's measurement with finite extinction ratio
        prob_det0, prob_det1 = pbs_measurement(transmitted_state, bob_angle, extinction_ratio)
        
        # Apply detection efficiency and add dark counts
        signal_prob_det0 = prob_det0 * total_efficiency
        signal_prob_det1 = prob_det1 * total_efficiency
        
        # Total detection probability includes signal + dark counts
        # Dark counts occur independently on both detectors
        effective_prob_det0 = signal_prob_det0 + dark_count_prob
        effective_prob_det1 = signal_prob_det1 + dark_count_prob
        
        results_matrix[f'{alice_prep}_{bob_basis}'] = {
            'det0_prob': float(effective_prob_det0),
            'det1_prob': float(effective_prob_det1),
            'total_detection': float(effective_prob_det0 + effective_prob_det1)
        }
        
        # Check if bases match
        alice_basis = 'rectilinear' if alice_prep in ['H', 'V'] else 'diagonal'
        if alice_basis == bob_basis:
            # Matching basis - should have high correlation (limited by imperfections)
            alice_bit = 0 if alice_prep in ['H', 'D'] else 1
            bob_bit_0_prob = effective_prob_det0
            bob_bit_1_prob = effective_prob_det1
            
            # Correlation: probability Bob gets correct bit
            total_prob = bob_bit_0_prob + bob_bit_1_prob
            if total_prob > 1e-12:
                if alice_bit == 0:
                    correlation = bob_bit_0_prob / total_prob
                else:
                    correlation = bob_bit_1_prob / total_prob
            else:
                correlation = 0.5  # No signal, random guess
            
            matching_basis_correlations.append(float(correlation))
        else:
            # Mismatched basis - should be random (50/50)
            mismatched_basis_results.append({
                'det0': float(effective_prob_det0),
                'det1': float(effective_prob_det1)
            })

# Calculate key performance metrics
avg_matching_correlation = float(np.mean(matching_basis_correlations))
std_matching_correlation = float(np.std(matching_basis_correlations))

# QBER estimation (Quantum Bit Error Rate)
# QBER = 1 - correlation in matching bases
qber_estimate = float(1.0 - avg_matching_correlation)

# Verify mismatched bases give ~50/50 (random results)
mismatched_ratios = []
for result in mismatched_basis_results:
    total = result['det0'] + result['det1']
    if total > 1e-12:
        ratio = result['det0'] / total
        mismatched_ratios.append(float(ratio))

avg_mismatched_ratio = float(np.mean(mismatched_ratios)) if mismatched_ratios else 0.5

# Calculate basis matching probability (should be 50%)
basis_match_probability = 0.5  # By design - Alice and Bob choose randomly

# Expected sifted key rate (fraction of transmitted photons that become key bits)
# = P(bases match) * P(detection) * (1 - QBER)
detection_probability = float(total_efficiency)
sifted_key_rate = float(basis_match_probability * detection_probability * (1.0 - qber_estimate))

# Verify extinction ratio effect (cross-talk)
cross_talk = float(1.0 / extinction_ratio)

# Calculate expected QBER contributions
qber_from_extinction = float(cross_talk)  # Direct contribution from PBS leakage
qber_from_dark_counts = float(dark_count_prob / (detection_probability + 2.0 * dark_count_prob + 1e-12))

# Store comprehensive results
results = {
    # Protocol statistics
    'avg_matching_basis_correlation': avg_matching_correlation,
    'qber_estimate': qber_estimate,
    'qber_from_extinction_ratio': qber_from_extinction,
    'qber_from_dark_counts': qber_from_dark_counts,
    'avg_mismatched_basis_ratio': avg_mismatched_ratio,
    'basis_match_probability': basis_match_probability,
    
    # System performance
    'total_transmission_efficiency': float(total_efficiency),
    'channel_transmission': float(channel_transmission),
    'detection_probability': detection_probability,
    'sifted_key_rate': sifted_key_rate,
    
    # Component verification
    'alice_fiber_efficiency': alice_fiber_efficiency,
    'bob_fiber_efficiency': bob_fiber_efficiency,
    'detector_efficiency': detector_efficiency,
    'extinction_ratio': float(extinction_ratio),
    'extinction_ratio_cross_talk': cross_talk,
    'dark_count_rate_hz': float(dark_count_rate),
    'dark_count_prob_per_gate': float(dark_count_prob),
    'measurement_window_ns': float(measurement_window * 1e9),
    
    # Example measurement results (H state, rectilinear basis)
    'H_rectilinear_det0_prob': results_matrix['H_rectilinear']['det0_prob'],
    'H_rectilinear_det1_prob': results_matrix['H_rectilinear']['det1_prob'],
    
    # Example mismatched basis (H state, diagonal basis - should be ~50/50)
    'H_diagonal_det0_prob': results_matrix['H_diagonal']['det0_prob'],
    'H_diagonal_det1_prob': results_matrix['H_diagonal']['det1_prob'],
    
    # Verify correlation examples with imperfections
    'D_diagonal_det0_prob': results_matrix['D_diagonal']['det0_prob'],
    'A_diagonal_det1_prob': results_matrix['A_diagonal']['det1_prob'],
    
    # Physics validation
    'correlation_std_dev': std_matching_correlation,
    'num_matching_cases': len(matching_basis_correlations),
    'num_mismatched_cases': len(mismatched_basis_results),
    
    # Design notes
    'note_attenuator': 'optical_depth=10 specified but not used - code models ideal single-photon Fock states',
    'note_timing': 'timing_resolution=50ps specified - used 1ns gate window for dark count calculation'
}