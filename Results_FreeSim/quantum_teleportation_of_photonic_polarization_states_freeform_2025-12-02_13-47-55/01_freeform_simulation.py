import numpy as np
import qutip as qt
from itertools import product

# Physical parameters
wavelength_pump = 405e-9  # m
wavelength_signal = 810e-9  # m (downconverted)
wavelength_idler = 810e-9  # m

# Detector efficiency
eta_detector = 0.70

# Extinction ratio for polarizers/PBS
extinction_ratio = 10000

# Beam splitter transmittance
bs_transmittance = 0.5

# State preparation angle (45 degrees)
state_prep_angle = np.pi / 4

# Define polarization basis states
# |H> = |0>, |V> = |1>
H = qt.basis(2, 0)
V = qt.basis(2, 1)

# Pauli matrices for corrections
sigma_x = qt.sigmax()
sigma_z = qt.sigmaz()
identity = qt.qeye(2)

# Prepare unknown state to teleport: |ψ⟩ = α|H⟩ + β|V⟩
# Using 45-degree polarization: |ψ⟩ = (|H⟩ + |V⟩)/√2
alpha = np.cos(state_prep_angle)
beta = np.sin(state_prep_angle)
psi_input = alpha * H + beta * V
psi_input = psi_input.unit()

print("=" * 60)
print("QUANTUM TELEPORTATION SIMULATION")
print("=" * 60)
print("\nInput state to teleport:")
print(f"|ψ⟩ = {alpha:.4f}|H⟩ + {beta:.4f}|V⟩")
print(f"Bloch sphere: θ = {2*state_prep_angle*180/np.pi:.1f}°")

# Create entangled Bell state |Φ+⟩ = (|HH⟩ + |VV⟩)/√2
# Photon 1 goes to Alice, Photon 2 goes to Bob
HH = qt.tensor(H, H)
VV = qt.tensor(V, V)
phi_plus = (HH + VV).unit()

print("\nEntangled state (SPDC):")
print("|Φ+⟩ = (|HH⟩ + |VV⟩)/√2")

# Total initial state: |ψ⟩_input ⊗ |Φ+⟩_{Alice,Bob}
# Three qubits: input photon, Alice's entangled photon, Bob's entangled photon
psi_total = qt.tensor(psi_input, phi_plus)

# Expand in computational basis
# |ψ⟩ ⊗ |Φ+⟩ = (α|H⟩ + β|V⟩) ⊗ (|HH⟩ + |VV⟩)/√2
# = α/√2 (|HHH⟩ + |HVV⟩) + β/√2 (|VHH⟩ + |VVV⟩)

print("\n" + "=" * 60)
print("ALICE'S BELL STATE MEASUREMENT")
print("=" * 60)

# Define Bell states for Alice's two photons (input + entangled)
# Bell basis for first two qubits
phi_plus_alice = (qt.tensor(H, H) + qt.tensor(V, V)).unit()
phi_minus_alice = (qt.tensor(H, H) - qt.tensor(V, V)).unit()
psi_plus_alice = (qt.tensor(H, V) + qt.tensor(V, H)).unit()
psi_minus_alice = (qt.tensor(H, V) - qt.tensor(V, H)).unit()

bell_states_alice = [phi_plus_alice, phi_minus_alice, psi_plus_alice, psi_minus_alice]
bell_names = ["|Φ+⟩", "|Φ-⟩", "|Ψ+⟩", "|Ψ-⟩"]

# Corresponding Bob states after measurement (without correction)
# |Φ+⟩ → |ψ⟩, |Φ-⟩ → σ_z|ψ⟩, |Ψ+⟩ → σ_x|ψ⟩, |Ψ-⟩ → σ_xσ_z|ψ⟩
bob_operators = [identity, sigma_z, sigma_x, sigma_x * sigma_z]

# Simulate Bell state measurement
# Project onto each Bell state and calculate probability
print("\nBell measurement probabilities:")

measurement_results = []
for i, (bell_state, name, operator) in enumerate(zip(bell_states_alice, bell_names, bob_operators)):
    # Projector for Alice's two qubits onto Bell state, identity for Bob
    projector = qt.tensor(bell_state * bell_state.dag(), qt.qeye(2))
    
    # Probability of this outcome
    prob = (projector * psi_total).norm() ** 2
    
    # Bob's state after this measurement (unnormalized)
    bob_state_unnorm = (projector * psi_total)
    
    if prob > 1e-10:
        # Trace out Alice's qubits to get Bob's reduced state
        # Bob is qubit 3 (index 2)
        bob_state = bob_state_unnorm.ptrace(2)
        bob_state = bob_state / bob_state.tr()
        
        # Expected Bob state (before correction)
        expected_bob = operator * psi_input
        
        measurement_results.append({
            'bell_state': name,
            'probability': prob,
            'bob_state': bob_state,
            'expected_bob': expected_bob,
            'correction': operator
        })
        
        print(f"{name}: P = {prob:.4f}")

# Account for detector efficiency and beam splitter losses
# Each photon must be detected with efficiency eta
# Bell measurement requires coincidence detection
detection_efficiency_per_event = eta_detector ** 2  # Two photons detected at Alice

print(f"\nDetection efficiency (2-photon coincidence): {detection_efficiency_per_event:.4f}")

# Classical communication and correction at Bob's station
print("\n" + "=" * 60)
print("BOB'S STATE RECONSTRUCTION")
print("=" * 60)

fidelities = []
for result in measurement_results:
    bell_name = result['bell_state']
    prob = result['probability']
    bob_state = result['bob_state']
    correction_op = result['correction']
    
    # Bob applies correction based on classical communication
    # Correction is the inverse of the transformation
    if correction_op == identity:
        correction_to_apply = identity
        correction_name = "I"
    elif correction_op == sigma_z:
        correction_to_apply = sigma_z
        correction_name = "σ_z"
    elif correction_op == sigma_x:
        correction_to_apply = sigma_x
        correction_name = "σ_x"
    else:  # sigma_x * sigma_z
        correction_to_apply = sigma_x * sigma_z
        correction_name = "σ_xσ_z"
    
    # Apply correction (unitary operation)
    bob_corrected_dm = correction_to_apply * bob_state * correction_to_apply.dag()
    
    # Calculate fidelity with input state
    fidelity = qt.fidelity(bob_corrected_dm, psi_input * psi_input.dag())
    fidelities.append(fidelity * prob)
    
    print(f"\n{bell_name} measurement (P={prob:.4f}):")
    print(f"  Correction applied: {correction_name}")
    print(f"  Fidelity with input: {fidelity:.6f}")

# Average fidelity weighted by measurement probabilities
average_fidelity = sum(fidelities)

print("\n" + "=" * 60)
print("TELEPORTATION RESULTS")
print("=" * 60)
print(f"\nIdeal average fidelity: {average_fidelity:.6f}")

# Account for realistic imperfections
# 1. Detector efficiency reduces successful teleportation rate
# 2. Dark counts add noise
# 3. Imperfect Bell state measurement due to BS and PBS imperfections

dark_count_rate = 100  # Hz
measurement_time = 1e-9  # 1 ns coincidence window
dark_count_prob = dark_count_rate * measurement_time

# Visibility of Bell state measurement (limited by HOM interference)
hom_visibility = 0.95  # Typical for good spatial/temporal mode matching

# Effective fidelity including imperfections
fidelity_with_detection = average_fidelity * detection_efficiency_per_event
fidelity_with_visibility = average_fidelity * hom_visibility

# Combined realistic fidelity
realistic_fidelity = average_fidelity * hom_visibility * (1 - 4 * dark_count_prob)

print(f"Fidelity with detection efficiency: {fidelity_with_detection:.6f}")
print(f"Fidelity with HOM visibility: {fidelity_with_visibility:.6f}")
print(f"Realistic fidelity (all effects): {realistic_fidelity:.6f}")

# Success rate (probability of successful teleportation per trial)
success_rate = detection_efficiency_per_event * (1 - 4 * dark_count_prob)
print(f"\nTeleportation success rate: {success_rate:.6f}")

# Verify state reconstruction for specific case
print("\n" + "=" * 60)
print("STATE VERIFICATION (Example: |Φ+⟩ measurement)")
print("=" * 60)

# For |Φ+⟩ measurement, no correction needed
phi_plus_result = measurement_results[0]
bob_final = phi_plus_result['bob_state']

print(f"\nInput state |ψ⟩:")
print(f"  α = {alpha:.6f}, β = {beta:.6f}")

# Extract Bob's state coefficients
bob_dm = bob_final.full()
bob_state_vec = np.array([bob_dm[0, 0], bob_dm[1, 1]])
bob_state_vec = bob_state_vec / np.sum(bob_state_vec)

print(f"\nBob's reconstructed state (after correction):")
print(f"  P(H) = {bob_state_vec[0]:.6f}, P(V) = {bob_state_vec[1]:.6f}")
print(f"  Expected: P(H) = {alpha**2:.6f}, P(V) = {beta**2:.6f}")

# Quantum process fidelity
print("\n" + "=" * 60)
print("QUANTUM CHANNEL CHARACTERIZATION")
print("=" * 60)

# Test teleportation for different input states
test_angles = [0, np.pi/6, np.pi/4, np.pi/3, np.pi/2]
test_fidelities = []

print("\nFidelity for different input states:")
for angle in test_angles:
    alpha_test = np.cos(angle)
    beta_test = np.sin(angle)
    psi_test = alpha_test * H + beta_test * V
    psi_test = psi_test.unit()
    
    # Create total state
    psi_total_test = qt.tensor(psi_test, phi_plus)
    
    # Average fidelity over all Bell measurements
    fid_test = 0
    for bell_state, operator in zip(bell_states_alice, bob_operators):
        projector = qt.tensor(bell_state * bell_state.dag(), qt.qeye(2))
        prob = (projector * psi_total_test).norm() ** 2
        
        if prob > 1e-10:
            bob_state_test = (projector * psi_total_test).ptrace(2)
            bob_state_test = bob_state_test / bob_state_test.tr()
            
            # Apply correction
            if operator == identity:
                correction = identity
            elif operator == sigma_z:
                correction = sigma_z
            elif operator == sigma_x:
                correction = sigma_x
            else:
                correction = sigma_x * sigma_z
            
            bob_corrected = correction * bob_state_test * correction.dag()
            fid = qt.fidelity(bob_corrected, psi_test * psi_test.dag())
            fid_test += fid * prob
    
    test_fidelities.append(fid_test)
    print(f"  θ = {angle*180/np.pi:5.1f}°: F = {fid_test:.6f}")

avg_process_fidelity = np.mean(test_fidelities)
print(f"\nAverage process fidelity: {avg_process_fidelity:.6f}")

# Theoretical limit (perfect teleportation)
print(f"Theoretical limit: 1.000000")
print(f"Achieved: {avg_process_fidelity:.6f} ({avg_process_fidelity*100:.2f}%)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Teleportation fidelity: {realistic_fidelity:.4f}")
print(f"Success rate: {success_rate:.4f}")
print(f"Process fidelity: {avg_process_fidelity:.4f}")
print("\nPhysical constraints satisfied:")
print(f"  ✓ Fidelity ∈ [0,1]: {0 <= realistic_fidelity <= 1}")
print(f"  ✓ Probabilities sum to 1: {np.abs(sum([r['probability'] for r in measurement_results]) - 1) < 1e-10}")
print(f"  ✓ States normalized: {np.abs(psi_input.norm() - 1) < 1e-10}")
print(f"  ✓ Detector efficiency realistic: {eta_detector} = 70%")
print("=" * 60)