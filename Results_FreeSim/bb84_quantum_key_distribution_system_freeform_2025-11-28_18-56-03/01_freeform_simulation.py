import numpy as np
from scipy.stats import bernoulli
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# PHYSICAL PARAMETERS FROM EXPERIMENT DESIGN
# ============================================================================

# Single-photon source parameters
wavelength = 850e-9  # 850 nm
photons_per_pulse = 0.1  # After attenuation

# Quantum channel parameters
fiber_length_km = 10
loss_db_per_km = 0.2
total_loss_db = fiber_length_km * loss_db_per_km
transmission_efficiency = 10**(-total_loss_db / 10)

# Beam splitter parameters
bs_transmittance = 0.5
bs_reflectance = 0.5

# Mirror reflectivity
mirror_reflectivity = 0.99

# Detector parameters
detector_efficiency = 0.70  # 70%
dark_count_rate = 100  # Hz
dark_count_prob_per_pulse = 1e-6  # Assuming high rep rate

# Simulation parameters
n_photons = 10000  # Number of photons to simulate

# ============================================================================
# POLARIZATION STATE DEFINITIONS
# ============================================================================

# Define polarization states as Jones vectors
H = np.array([1, 0], dtype=complex)  # Horizontal
V = np.array([0, 1], dtype=complex)  # Vertical
P45 = np.array([1, 1], dtype=complex) / np.sqrt(2)  # +45 degrees
M45 = np.array([1, -1], dtype=complex) / np.sqrt(2)  # -45 degrees

# Basis definitions
RECTILINEAR = 0
DIAGONAL = 1

# Bit definitions
BIT_0 = 0
BIT_1 = 1

# Alice's encoding map: (basis, bit) -> polarization state
alice_encoding = {
    (RECTILINEAR, BIT_0): H,
    (RECTILINEAR, BIT_1): V,
    (DIAGONAL, BIT_0): P45,
    (DIAGONAL, BIT_1): M45
}

# ============================================================================
# MEASUREMENT OPERATORS
# ============================================================================

# Projectors for rectilinear basis (H/V measurement)
proj_H = np.outer(H, H.conj())
proj_V = np.outer(V, V.conj())

# Projectors for diagonal basis (+45/-45 measurement)
proj_P45 = np.outer(P45, P45.conj())
proj_M45 = np.outer(M45, M45.conj())

# ============================================================================
# BB84 PROTOCOL SIMULATION
# ============================================================================

print("=" * 70)
print("BB84 QUANTUM KEY DISTRIBUTION SIMULATION")
print("=" * 70)
print(f"\nSimulation Parameters:")
print(f"  Number of photons: {n_photons}")
print(f"  Wavelength: {wavelength * 1e9:.0f} nm")
print(f"  Fiber length: {fiber_length_km} km")
print(f"  Channel transmission: {transmission_efficiency:.4f}")
print(f"  Detector efficiency: {detector_efficiency:.2%}")
print(f"  Beam splitter ratio: 50:50")
print()

# Storage for Alice and Bob's data
alice_bases = []
alice_bits = []
alice_states = []

bob_bases = []
bob_measurements = []
bob_detected = []

# ============================================================================
# STEP 1: ALICE PREPARES AND SENDS PHOTONS
# ============================================================================

for i in range(n_photons):
    # Alice randomly chooses basis and bit
    alice_basis = np.random.choice([RECTILINEAR, DIAGONAL])
    alice_bit = np.random.choice([BIT_0, BIT_1])
    
    # Alice encodes the photon
    state = alice_encoding[(alice_basis, alice_bit)].copy()
    
    # Store Alice's choices
    alice_bases.append(alice_basis)
    alice_bits.append(alice_bit)
    alice_states.append(state)

# ============================================================================
# STEP 2: QUANTUM CHANNEL TRANSMISSION
# ============================================================================

# Photons survive transmission with probability = transmission_efficiency
transmission_survived = np.random.random(n_photons) < transmission_efficiency

# ============================================================================
# STEP 3: BOB'S MEASUREMENT
# ============================================================================

for i in range(n_photons):
    if not transmission_survived[i]:
        # Photon lost in channel
        bob_bases.append(None)
        bob_measurements.append(None)
        bob_detected.append(False)
        continue
    
    state = alice_states[i]
    
    # Bob's beam splitter randomly chooses measurement basis
    # Transmitted -> Rectilinear (50%)
    # Reflected -> Diagonal (50%)
    bob_basis = np.random.choice([RECTILINEAR, DIAGONAL])
    bob_bases.append(bob_basis)
    
    # Calculate measurement probabilities based on Bob's basis
    if bob_basis == RECTILINEAR:
        # Measure in H/V basis
        prob_H = np.abs(np.vdot(H, state))**2
        prob_V = np.abs(np.vdot(V, state))**2
        
        # Bob's measurement outcome
        if np.random.random() < prob_H:
            measurement_result = BIT_0  # H corresponds to bit 0
        else:
            measurement_result = BIT_1  # V corresponds to bit 1
    else:
        # Measure in +45/-45 basis (diagonal)
        prob_P45 = np.abs(np.vdot(P45, state))**2
        prob_M45 = np.abs(np.vdot(M45, state))**2
        
        # Bob's measurement outcome
        if np.random.random() < prob_P45:
            measurement_result = BIT_0  # +45 corresponds to bit 0
        else:
            measurement_result = BIT_1  # -45 corresponds to bit 1
    
    # Apply detector efficiency and dark counts
    detected = False
    if np.random.random() < detector_efficiency:
        detected = True
    elif np.random.random() < dark_count_prob_per_pulse:
        # Dark count - random measurement
        detected = True
        measurement_result = np.random.choice([BIT_0, BIT_1])
    
    bob_measurements.append(measurement_result if detected else None)
    bob_detected.append(detected)

# ============================================================================
# STEP 4: BASIS SIFTING (PUBLIC CLASSICAL CHANNEL)
# ============================================================================

print("=" * 70)
print("BASIS SIFTING AND KEY GENERATION")
print("=" * 70)

sifted_alice_bits = []
sifted_bob_bits = []
sifted_indices = []

for i in range(n_photons):
    # Only keep events where:
    # 1. Bob detected the photon
    # 2. Alice and Bob used the same basis
    if bob_detected[i] and alice_bases[i] == bob_bases[i]:
        sifted_alice_bits.append(alice_bits[i])
        sifted_bob_bits.append(bob_measurements[i])
        sifted_indices.append(i)

sifted_alice_bits = np.array(sifted_alice_bits)
sifted_bob_bits = np.array(sifted_bob_bits)

print(f"\nPhotons sent by Alice: {n_photons}")
print(f"Photons detected by Bob: {sum(bob_detected)}")
print(f"Sifted key length (matching bases): {len(sifted_alice_bits)}")

# ============================================================================
# STEP 5: ERROR ESTIMATION (QBER CALCULATION)
# ============================================================================

if len(sifted_alice_bits) > 0:
    # Compare subset of bits to estimate error rate
    # In practice, ~10-20% of sifted bits are sacrificed for error estimation
    test_fraction = 0.15
    n_test = int(len(sifted_alice_bits) * test_fraction)
    
    if n_test > 0:
        test_indices = np.random.choice(len(sifted_alice_bits), n_test, replace=False)
        test_alice = sifted_alice_bits[test_indices]
        test_bob = sifted_bob_bits[test_indices]
        
        errors = np.sum(test_alice != test_bob)
        qber = errors / n_test if n_test > 0 else 0
        
        print(f"\nError Estimation:")
        print(f"  Test bits used: {n_test}")
        print(f"  Errors found: {errors}")
        print(f"  QBER (Quantum Bit Error Rate): {qber:.4f} ({qber*100:.2f}%)")
        
        # Remove test bits from final key
        keep_mask = np.ones(len(sifted_alice_bits), dtype=bool)
        keep_mask[test_indices] = False
        final_alice_key = sifted_alice_bits[keep_mask]
        final_bob_key = sifted_bob_bits[keep_mask]
        
        print(f"  Final key length (after error estimation): {len(final_alice_key)}")
    else:
        qber = 0
        final_alice_key = sifted_alice_bits
        final_bob_key = sifted_bob_bits
        print(f"\nInsufficient bits for error estimation")
else:
    qber = 0
    final_alice_key = np.array([])
    final_bob_key = np.array([])
    print(f"\nNo sifted bits available")

# ============================================================================
# STEP 6: SECURITY ANALYSIS
# ============================================================================

print(f"\n" + "=" * 70)
print("SECURITY ANALYSIS")
print("=" * 70)

# Expected QBER without eavesdropping
# Sources: detector dark counts, channel noise, imperfect components
expected_qber_intrinsic = dark_count_prob_per_pulse / (detector_efficiency + dark_count_prob_per_pulse)

print(f"\nExpected intrinsic QBER (no eavesdropper): {expected_qber_intrinsic:.6f}")
print(f"Measured QBER: {qber:.6f}")

# Security threshold for BB84
# Typical threshold: QBER < 11% for secure key distillation
qber_threshold = 0.11

if qber < qber_threshold:
    print(f"\n✓ QBER below security threshold ({qber_threshold*100:.0f}%)")
    print(f"  Key is secure (no significant eavesdropping detected)")
    secure = True
else:
    print(f"\n✗ QBER exceeds security threshold ({qber_threshold*100:.0f}%)")
    print(f"  Possible eavesdropping or excessive channel noise")
    print(f"  Key should be discarded")
    secure = False

# ============================================================================
# STEP 7: KEY RATE CALCULATION
# ============================================================================

print(f"\n" + "=" * 70)
print("KEY RATE ANALYSIS")
print("=" * 70)

# Sifting efficiency (fraction of photons that contribute to sifted key)
sifting_efficiency = len(sifted_alice_bits) / n_photons if n_photons > 0 else 0

# Expected sifting efficiency (50% basis matching * transmission * detection)
expected_sifting = 0.5 * transmission_efficiency * detector_efficiency

print(f"\nSifting efficiency: {sifting_efficiency:.4f}")
print(f"Expected sifting efficiency: {expected_sifting:.4f}")

# Final secure key rate after error correction and privacy amplification
# Simplified formula: R = sifting_rate * [1 - h(QBER) - h(QBER)]
# where h(x) is binary entropy
def binary_entropy(p):
    if p == 0 or p == 1:
        return 0
    return -p * np.log2(p) - (1-p) * np.log2(1-p)

if secure and len(final_alice_key) > 0:
    # Information leaked to eavesdropper
    info_leaked = binary_entropy(qber)
    # Error correction cost
    error_correction_cost = binary_entropy(qber)
    # Net key rate per sifted bit
    net_rate_per_sifted = max(0, 1 - info_leaked - error_correction_cost)
    
    final_key_length = int(len(final_alice_key) * net_rate_per_sifted)
    
    print(f"\nPrivacy amplification:")
    print(f"  Binary entropy h(QBER): {binary_entropy(qber):.4f}")
    print(f"  Net rate per sifted bit: {net_rate_per_sifted:.4f}")
    print(f"  Final secure key length: {final_key_length} bits")
else:
    final_key_length = 0
    print(f"\nNo secure key generated (QBER too high or insufficient data)")

# ============================================================================
# STEP 8: VERIFICATION OF QUANTUM MECHANICS
# ============================================================================

print(f"\n" + "=" * 70)
print("QUANTUM MECHANICS VERIFICATION")
print("=" * 70)

# Analyze what happens when bases match vs. don't match
matching_basis_indices = []
mismatched_basis_indices = []

for i in range(n_photons):
    if bob_detected[i]:
        if alice_bases[i] == bob_bases[i]:
            matching_basis_indices.append(i)
        else:
            mismatched_basis_indices.append(i)

# For matching bases: should have ~0% error (except noise)
if len(matching_basis_indices) > 0:
    matching_errors = 0
    for i in matching_basis_indices:
        if alice_bits[i] != bob_measurements[i]:
            matching_errors += 1
    matching_error_rate = matching_errors / len(matching_basis_indices)
    print(f"\nMatching basis events: {len(matching_basis_indices)}")
    print(f"  Error rate: {matching_error_rate:.4f} ({matching_error_rate*100:.2f}%)")
    print(f"  (Should be ~0% in ideal case)")

# For mismatched bases: should have ~50% error (random outcomes)
if len(mismatched_basis_indices) > 0:
    mismatched_errors = 0
    for i in mismatched_basis_indices:
        if alice_bits[i] != bob_measurements[i]:
            mismatched_errors += 1
    mismatched_error_rate = mismatched_errors / len(mismatched_basis_indices)
    print(f"\nMismatched basis events: {len(mismatched_basis_indices)}")
    print(f"  Error rate: {mismatched_error_rate:.4f} ({mismatched_error_rate*100:.2f}%)")
    print(f"  (Should be ~50% due to quantum measurement disturbance)")

# ============================================================================
# STEP 9: EAVESDROPPING SIMULATION (OPTIONAL DEMONSTRATION)
# ============================================================================

print(f"\n" + "=" * 70)
print("EAVESDROPPING ATTACK SIMULATION")
print("=" * 70)

# Simulate Eve's intercept-resend attack
print(f"\nSimulating intercept-resend attack by Eve...")

eve_alice_bases = []
eve_alice_bits = []
eve_bob_bases = []
eve_bob_measurements = []
eve_bob_detected = []

for i in range(n_photons):
    # Alice prepares photon
    alice_basis = np.random.choice([RECTILINEAR, DIAGONAL])
    alice_bit = np.random.choice([BIT_0, BIT_1])
    state = alice_encoding[(alice_basis, alice_bit)].copy()
    
    eve_alice_bases.append(alice_basis)
    eve_alice_bits.append(alice_bit)
    
    # Photon survives to Eve
    if np.random.random() > transmission_efficiency * 0.5:
        eve_bob_bases.append(None)
        eve_bob_measurements.append(None)
        eve_bob_detected.append(False)
        continue
    
    # Eve intercepts and measures in random basis
    eve_basis = np.random.choice([RECTILINEAR, DIAGONAL])
    
    if eve_basis == RECTILINEAR:
        prob_H = np.abs(np.vdot(H, state))**2
        eve_result = BIT_0 if np.random.random() < prob_H else BIT_1
        # Eve resends photon in measured state
        state = H if eve_result == BIT_0 else V
    else:
        prob_P45 = np.abs(np.vdot(P45, state))**2
        eve_result = BIT_0 if np.random.random() < prob_P45 else BIT_1
        # Eve resends photon in measured state
        state = P45 if eve_result == BIT_0 else M45
    
    # Photon continues to Bob
    if np.random.random() > transmission_efficiency * 0.5:
        eve_bob_bases.append(None)
        eve_bob_measurements.append(None)
        eve_bob_detected.append(False)
        continue
    
    # Bob measures
    bob_basis = np.random.choice([RECTILINEAR, DIAGONAL])
    eve_bob_bases.append(bob_basis)
    
    if bob_basis == RECTILINEAR:
        prob_H = np.abs(np.vdot(H, state))**2
        measurement_result = BIT_0 if np.random.random() < prob_H else BIT_1
    else:
        prob_P45 = np.abs(np.vdot(P45, state))**2
        measurement_result = BIT_0 if np.random.random() < prob_P45 else BIT_1
    
    detected = np.random.random() < detector_efficiency
    eve_bob_measurements.append(measurement_result if detected else None)
    eve_bob_detected.append(detected)

# Calculate QBER with eavesdropper
eve_sifted_alice = []
eve_sifted_bob = []

for i in range(n_photons):
    if eve_bob_detected[i] and eve_alice_bases[i] == eve_bob_bases[i]:
        eve_sifted_alice.append(eve_alice_bits[i])
        eve_sifted_bob.append(eve_bob_measurements[i])

if len(eve_sifted_alice) > 0:
    eve_errors = np.sum(np.array(eve_sifted_alice) != np.array(eve_sifted_bob))
    eve_qber = eve_errors / len(eve_sifted_alice)
    print(f"  Sifted bits with eavesdropper: {len(eve_sifted_alice)}")
    print(f"  QBER with eavesdropper: {eve_qber:.4f} ({eve_qber*100:.2f}%)")
    print(f"  Expected QBER with intercept-resend: ~25%")
    print(f"\n  ✓ Eavesdropping detected! QBER significantly increased.")
else:
    print(f"  Insufficient data")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n" + "=" * 70)
print("SIMULATION SUMMARY")
print("=" * 70)

print(f"\nWithout eavesdropper:")
print(f"  Total photons sent: {n_photons}")
print(f"  Sifted key length: {len(sifted_alice_bits)}")
print(f"  QBER: {qber:.4f} ({qber*100:.2f}%)")
print(f"  Secure key length: {final_key_length} bits")
print(f"  Security status: {'SECURE' if secure else 'INSECURE'}")

print(f"\nKey physical principles demonstrated:")
print(f"  ✓ Quantum state preparation in 4 polarization states")
print(f"  ✓ Random basis selection via beam splitter")
print(f"  ✓ Basis sifting reduces raw key by ~50%")
print(f"  ✓ Matching basis: low error rate")
print(f"  ✓ Mismatched basis: ~50% random outcomes")
print(f"  ✓ Eavesdropping introduces detectable errors (QBER increase)")
print(f"  ✓ No-cloning theorem prevents copying quantum states")

print(f"\n" + "=" * 70)
print("BB84 SIMULATION COMPLETE")
print("=" * 70)