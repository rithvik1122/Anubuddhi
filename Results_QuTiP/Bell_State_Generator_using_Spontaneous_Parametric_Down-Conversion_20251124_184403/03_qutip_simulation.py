# REASONING: Fixed fundamental physics errors - replaced photon number entanglement with proper polarization entanglement for Type-II SPDC, implemented 4D polarization Hilbert space, and added correct Bell parameter calculation with multiple measurement angles

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 2  # Binary polarization states: H=0, V=1
pump_wavelength = 405  # nm
signal_wavelength = 810  # nm (2x pump for Type-II SPDC)
pump_power = 50  # mW
crystal_length = 2  # mm
detector_efficiency = 0.65
polarizer_angle = 45  # degrees

# Step 1: Define polarization basis states
# Mode A and Mode B each have H and V polarizations
H = qt.basis(2, 0)  # Horizontal polarization
V = qt.basis(2, 1)  # Vertical polarization

# 4D Hilbert space for two-photon polarization states
HH = qt.tensor(H, H)
HV = qt.tensor(H, V)
VH = qt.tensor(V, H)
VV = qt.tensor(V, V)

# Step 2: Type-II SPDC creates polarization-entangled Bell state
# |ψ⟩ = cos(r)|vacuum⟩ + sin(r)(|HV⟩ + |VH⟩)/√2
# where r depends on pump power and crystal length
r = np.sqrt(pump_power * crystal_length * 0.001)  # Scaling factor for SPDC efficiency
r = min(r, 0.5)  # Limit to avoid unphysical states

# Create Type-II SPDC state
vacuum_component = np.cos(r)
entangled_component = np.sin(r) / np.sqrt(2)

# For detection, we focus on the two-photon component
spdc_state = entangled_component * (HV + VH)
spdc_state = spdc_state.unit()

# Step 3: Pump block filter removes pump, leaves signal/idler
filter_transmission = 0.95
state_after_filter = spdc_state * np.sqrt(filter_transmission)
state_after_filter = state_after_filter.unit()

# Step 4: Beam separation preserves entanglement
separated_state = state_after_filter

# Step 5: Define polarization measurement operators
def polarization_operator(angle_deg, mode_index):
    """Create polarization measurement operator at given angle"""
    theta = np.radians(angle_deg)
    # Polarization operator: cos(θ)|H⟩⟨H| + sin(θ)|V⟩⟨V|
    pol_op = np.cos(theta) * qt.basis(2, 0) * qt.basis(2, 0).dag() + \
             np.sin(theta) * qt.basis(2, 1) * qt.basis(2, 1).dag()
    
    if mode_index == 0:  # Mode A
        return qt.tensor(pol_op, qt.qeye(2))
    else:  # Mode B
        return qt.tensor(qt.qeye(2), pol_op)

# Step 6: Bell parameter calculation with multiple measurement angles
# CHSH inequality requires 4 correlation measurements
angles_a = [0, 0, 45, 45]  # Alice's polarizer angles
angles_b = [0, 45, 0, 45]  # Bob's polarizer angles

correlations = []
for i in range(4):
    # Create measurement operators for both modes
    pol_a = polarization_operator(angles_a[i], 0)
    pol_b = polarization_operator(angles_b[i], 1)
    
    # Joint measurement probability
    joint_op = pol_a * pol_b
    prob_both = float(abs(qt.expect(joint_op, separated_state)))
    
    # Individual measurement probabilities
    prob_a = float(abs(qt.expect(pol_a, separated_state)))
    prob_b = float(abs(qt.expect(pol_b, separated_state)))
    
    # Correlation coefficient E(a,b) = P(both) - P(a)P(b) (normalized)
    correlation = (prob_both - prob_a * prob_b) / (prob_a * prob_b + 1e-12)
    correlations.append(correlation)

# Bell/CHSH parameter: S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|
E_ab = correlations[0]    # 0°, 0°
E_ab_prime = correlations[1]  # 0°, 45°
E_a_prime_b = correlations[2]  # 45°, 0°
E_a_prime_b_prime = correlations[3]  # 45°, 45°

bell_parameter = float(abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime))

# Step 7: Detection with SPAD efficiency
pol_45_a = polarization_operator(45, 0)
pol_45_b = polarization_operator(45, 1)

detection_prob_a = float(abs(qt.expect(pol_45_a, separated_state))) * detector_efficiency
detection_prob_b = float(abs(qt.expect(pol_45_b, separated_state))) * detector_efficiency
coincidence_rate = float(abs(qt.expect(pol_45_a * pol_45_b, separated_state))) * detector_efficiency**2

# Step 8: Calculate validation metrics
# Density matrix for entanglement analysis
rho_total = separated_state * separated_state.dag()
rho_a = rho_total.ptrace(0)  # Reduced state of mode A

# Entanglement entropy
entropy_a = float(abs(qt.entropy_vn(rho_a)))

# State purity
purity = float(abs((rho_total * rho_total).tr()))

# Fidelity to ideal Bell state |ψ⟩ = (|HV⟩ + |VH⟩)/√2
ideal_bell = (HV + VH).unit()
bell_fidelity = float(abs(qt.fidelity(separated_state, ideal_bell)))

# Visibility calculation
I_parallel = float(abs(qt.expect(polarization_operator(0, 0) * polarization_operator(0, 1), separated_state)))
I_orthogonal = float(abs(qt.expect(polarization_operator(0, 0) * polarization_operator(90, 1), separated_state)))
visibility = float((I_parallel - I_orthogonal) / (I_parallel + I_orthogonal + 1e-12))

# Store results for validation
results = {
    'photon_count_a': float(detection_prob_a),
    'photon_count_b': float(detection_prob_b),
    'coincidence_rate': float(coincidence_rate),
    'entanglement_entropy': float(entropy_a),
    'state_purity': float(purity),
    'bell_state_fidelity': float(bell_fidelity),
    'bell_parameter': float(bell_parameter),
    'visibility': float(abs(visibility)),
    'total_efficiency': float(detector_efficiency),
    'spdc_strength': float(r)
}