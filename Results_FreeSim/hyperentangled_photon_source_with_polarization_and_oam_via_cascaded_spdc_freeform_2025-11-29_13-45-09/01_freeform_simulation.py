import numpy as np
import qutip as qt
from scipy.linalg import sqrtm
from itertools import product

# Physical parameters from experiment
wavelength_pump = 405e-9  # m
wavelength_down = 810e-9  # m
pump_power = 300e-3  # W
crystal_length = 2e-3  # m
detector_efficiency = 0.70
oam_sorter_efficiency = 0.85
coincidence_window = 500e-12  # s
dark_count_rate = 100  # Hz

# SPDC parameters
# Conversion efficiency for Type-I BBO (typical ~10^-6 to 10^-8 per mW pump power per crystal length)
# Using realistic value for 300mW pump, 2mm crystal
conversion_efficiency = 1e-7  # pairs per pump photon
pump_photon_rate = pump_power / (6.626e-34 * 3e8 / wavelength_pump)
pair_generation_rate = pump_photon_rate * conversion_efficiency

# After PBS split, each path gets 50% of pump power (HWP at 45deg creates diagonal polarization)
pair_rate_per_crystal = pair_generation_rate / 2

# Simulation time and number of trials
measurement_time = 1.0  # seconds
num_pairs = int(pair_rate_per_crystal * measurement_time)
print(f"Simulating {num_pairs} photon pairs per crystal arm over {measurement_time}s")
print(f"Total pair generation rate: {pair_generation_rate:.2e} pairs/s")
print()

# OAM quantum number (using ell=1 as typical value)
ell = 1

# Define polarization basis states
# Computational basis: |H⟩, |V⟩
H = 0
V = 1

# OAM basis states
# |+ell⟩, |-ell⟩
plus_ell = 0
minus_ell = 1

# Create hyperentangled state
# Polarization: (|HH⟩ + |VV⟩)/√2
# OAM: (|+ell,+ell⟩ + |-ell,-ell⟩)/√2
# Full state: tensor product of both

# Using 4-dimensional Hilbert space for two qubits
# Basis ordering: |HH⟩, |HV⟩, |VH⟩, |VV⟩
pol_bell_state = (qt.tensor(qt.basis(2, 0), qt.basis(2, 0)) + 
                  qt.tensor(qt.basis(2, 1), qt.basis(2, 1))).unit()

# OAM entangled state in same form
# Basis ordering: |+ell,+ell⟩, |+ell,-ell⟩, |-ell,+ell⟩, |-ell,-ell⟩
oam_bell_state = (qt.tensor(qt.basis(2, 0), qt.basis(2, 0)) + 
                  qt.tensor(qt.basis(2, 1), qt.basis(2, 1))).unit()

# Hyperentangled state is tensor product
# 16-dimensional Hilbert space (4 pol × 4 OAM)
hyperentangled_state = qt.tensor(pol_bell_state, oam_bell_state)

print("Hyperentangled state created:")
print(f"Polarization Bell state fidelity with |Φ+⟩: {qt.fidelity(pol_bell_state, pol_bell_state):.4f}")
print(f"OAM Bell state fidelity: {qt.fidelity(oam_bell_state, oam_bell_state):.4f}")
print()

# Define measurement operators for polarization analysis
# PBS separates H and V polarization
def pol_projector(pol1, pol2):
    """Create projector for polarization measurement on both photons"""
    return qt.tensor(qt.basis(2, pol1) * qt.basis(2, pol1).dag(),
                     qt.basis(2, pol2) * qt.basis(2, pol2).dag())

# Define measurement operators for OAM analysis
def oam_projector(oam1, oam2):
    """Create projector for OAM measurement on both photons"""
    return qt.tensor(qt.basis(2, oam1) * qt.basis(2, oam1).dag(),
                     qt.basis(2, oam2) * qt.basis(2, oam2).dag())

# Full measurement projector (pol ⊗ oam)
def full_projector(pol1, pol2, oam1, oam2):
    """Create projector for simultaneous polarization and OAM measurement"""
    pol_proj = pol_projector(pol1, pol2)
    oam_proj = oam_projector(oam1, oam2)
    return qt.tensor(pol_proj, oam_proj)

# Calculate ideal probabilities for hyperentangled state
print("=== IDEAL PROBABILITIES (NO LOSSES) ===")
print()

# All possible measurement outcomes
pol_outcomes = [(H, H), (H, V), (V, H), (V, V)]
oam_outcomes = [(plus_ell, plus_ell), (plus_ell, minus_ell), 
                (minus_ell, plus_ell), (minus_ell, minus_ell)]

pol_labels = {(H, H): "HH", (H, V): "HV", (V, H): "VH", (V, V): "VV"}
oam_labels = {(plus_ell, plus_ell): "+ℓ+ℓ", (plus_ell, minus_ell): "+ℓ-ℓ",
              (minus_ell, plus_ell): "-ℓ+ℓ", (minus_ell, minus_ell): "-ℓ-ℓ"}

ideal_probs = {}
for pol_out in pol_outcomes:
    for oam_out in oam_outcomes:
        proj = full_projector(pol_out[0], pol_out[1], oam_out[0], oam_out[1])
        prob = qt.expect(proj, hyperentangled_state)
        ideal_probs[(pol_out, oam_out)] = prob
        if prob > 1e-6:  # Only print non-zero probabilities
            print(f"P({pol_labels[pol_out]}, {oam_labels[oam_out]}) = {prob:.4f}")

print()

# Verify probabilities sum to 1
total_prob = sum(ideal_probs.values())
print(f"Total probability (should be 1.0): {total_prob:.6f}")
print()

# Calculate polarization entanglement measures
# Trace out OAM degrees of freedom to get reduced polarization state
# The hyperentangled state has structure: sum_i c_i |pol_i⟩|oam_i⟩
# We need to trace over OAM indices

# Convert to density matrix
rho_full = hyperentangled_state * hyperentangled_state.dag()

# Partial trace over OAM (indices 2,3 in tensor product pol1⊗pol2⊗oam1⊗oam2)
# QuTiP ptrace keeps specified subsystems
rho_pol = rho_full.ptrace([0, 1])  # Keep polarization subsystems

print("=== POLARIZATION ENTANGLEMENT ===")
print()

# Calculate concurrence for polarization
def concurrence(rho):
    """Calculate concurrence for 2-qubit density matrix"""
    # Pauli Y matrix
    sigma_y = qt.sigmay()
    # Spin-flipped density matrix
    rho_tilde = qt.tensor(sigma_y, sigma_y) * rho.conj() * qt.tensor(sigma_y, sigma_y)
    # Product matrix
    R = rho * rho_tilde
    # Eigenvalues in decreasing order
    eigenvals = np.sort(np.real(R.eigenenergies()))[::-1]
    sqrt_eigenvals = np.sqrt(np.maximum(eigenvals, 0))
    C = max(0, sqrt_eigenvals[0] - sqrt_eigenvals[1] - sqrt_eigenvals[2] - sqrt_eigenvals[3])
    return C

C_pol = concurrence(rho_pol)
print(f"Polarization concurrence: {C_pol:.4f}")

# Calculate fidelity with maximally entangled state
pol_bell_dm = pol_bell_state * pol_bell_state.dag()
F_pol = qt.fidelity(rho_pol, pol_bell_dm)
print(f"Polarization fidelity with |Φ+⟩: {F_pol:.4f}")
print()

# Calculate OAM entanglement measures
rho_oam = rho_full.ptrace([2, 3])  # Keep OAM subsystems

print("=== OAM ENTANGLEMENT ===")
print()

C_oam = concurrence(rho_oam)
print(f"OAM concurrence: {C_oam:.4f}")

oam_bell_dm = oam_bell_state * oam_bell_state.dag()
F_oam = qt.fidelity(rho_oam, oam_bell_dm)
print(f"OAM fidelity with Bell state: {F_oam:.4f}")
print()

# Simulate realistic detection with losses
print("=== REALISTIC DETECTION WITH LOSSES ===")
print()

# Account for:
# 1. OAM sorter efficiency
# 2. Detector efficiency
# 3. Dark counts

total_detection_efficiency = detector_efficiency * oam_sorter_efficiency
print(f"Total detection efficiency per channel: {total_detection_efficiency:.2%}")
print()

# Simulate coincidence measurements
np.random.seed(42)

# For each measurement combination, simulate detections
detected_counts = {}
for pol_out in pol_outcomes:
    for oam_out in oam_outcomes:
        ideal_prob = ideal_probs[(pol_out, oam_out)]
        # Number of pairs in this state
        expected_pairs = num_pairs * ideal_prob
        # Detection probability for both photons
        detection_prob = total_detection_efficiency**2
        # Expected detected coincidences
        expected_detections = expected_pairs * detection_prob
        # Add Poisson noise
        actual_detections = np.random.poisson(expected_detections)
        # Add dark count coincidences (accidental)
        dark_coincidences = np.random.poisson(dark_count_rate * coincidence_window * measurement_time)
        total_counts = actual_detections + dark_coincidences
        detected_counts[(pol_out, oam_out)] = total_counts

# Print detected coincidences
print("Detected coincidence counts:")
for pol_out in pol_outcomes:
    for oam_out in oam_outcomes:
        counts = detected_counts[(pol_out, oam_out)]
        if counts > 0:
            print(f"{pol_labels[pol_out]}, {oam_labels[oam_out]}: {counts} counts")

print()

# Calculate correlation visibility for polarization
# Compare HH+VV (correlated) vs HV+VH (anti-correlated)
correlated_pol = detected_counts[((H, H), (plus_ell, plus_ell))] + detected_counts[((H, H), (minus_ell, minus_ell))] + \
                 detected_counts[((V, V), (plus_ell, plus_ell))] + detected_counts[((V, V), (minus_ell, minus_ell))]

anticorrelated_pol = detected_counts[((H, V), (plus_ell, plus_ell))] + detected_counts[((H, V), (minus_ell, minus_ell))] + \
                     detected_counts[((V, H), (plus_ell, plus_ell))] + detected_counts[((V, H), (minus_ell, minus_ell))]

if (correlated_pol + anticorrelated_pol) > 0:
    visibility_pol = (correlated_pol - anticorrelated_pol) / (correlated_pol + anticorrelated_pol)
else:
    visibility_pol = 0

print(f"Polarization correlation visibility: {visibility_pol:.4f}")

# Calculate correlation visibility for OAM
correlated_oam = detected_counts[((H, H), (plus_ell, plus_ell))] + detected_counts[((H, H), (minus_ell, minus_ell))] + \
                 detected_counts[((V, V), (plus_ell, plus_ell))] + detected_counts[((V, V), (minus_ell, minus_ell))]

anticorrelated_oam = detected_counts[((H, H), (plus_ell, minus_ell))] + detected_counts[((H, H), (minus_ell, plus_ell))] + \
                     detected_counts[((V, V), (plus_ell, minus_ell))] + detected_counts[((V, V), (minus_ell, plus_ell))]

if (correlated_oam + anticorrelated_oam) > 0:
    visibility_oam = (correlated_oam - anticorrelated_oam) / (correlated_oam + anticorrelated_oam)
else:
    visibility_oam = 0

print(f"OAM correlation visibility: {visibility_oam:.4f}")
print()

# Bell inequality test for hyperentanglement
# CHSH inequality: |S| ≤ 2 for classical, can reach 2√2 ≈ 2.828 for quantum
print("=== BELL INEQUALITY TEST ===")
print()

# For hyperentangled state, we can test CHSH on each degree of freedom
# CHSH parameter S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
# where E(a,b) is correlation function for measurement settings a,b

# For polarization in HV basis and diagonal basis
# Measurement angles: 0°, 45°, 22.5°, 67.5°
# This would require additional HWPs in the setup, but we can calculate expected values

# Using the ideal state, calculate CHSH for polarization
# Settings: a=H/V, a'=D/A (diagonal/antidiagonal), b=H/V, b'=D/A

# Define diagonal basis states
D_state = (qt.basis(2, 0) + qt.basis(2, 1)).unit()  # (|H⟩ + |V⟩)/√2
A_state = (qt.basis(2, 0) - qt.basis(2, 1)).unit()  # (|H⟩ - |V⟩)/√2

# For Bell state |Φ+⟩ = (|HH⟩ + |VV⟩)/√2
# E(HV, HV) = ⟨ZZ⟩ = 1
# E(HV, DA) = ⟨ZX⟩ = 0
# E(DA, HV) = ⟨XZ⟩ = 0  
# E(DA, DA) = ⟨XX⟩ = 1

# For ideal |Φ+⟩ state, maximal CHSH violation gives S = 2√2

# Simplified calculation: for |Φ+⟩ with optimal angles
S_max_theoretical = 2 * np.sqrt(2)
print(f"Maximum CHSH parameter (theoretical): {S_max_theoretical:.4f}")

# With realistic detection efficiency and dark counts, violation is reduced
# Estimate based on visibility
S_estimated = visibility_pol * S_max_theoretical
print(f"Estimated CHSH parameter (with losses): {S_estimated:.4f}")
print(f"Classical bound: 2.000")
print(f"Quantum violation: {S_estimated > 2.0}")
print()

# Summary
print("=== SUMMARY ===")
print()
print(f"Hyperentangled photon source characteristics:")
print(f"  Pump wavelength: {wavelength_pump*1e9:.0f} nm")
print(f"  Down-converted wavelength: {wavelength_down*1e9:.0f} nm")
print(f"  Pair generation rate: {pair_generation_rate:.2e} pairs/s")
print(f"  OAM charge: ±{ell}")
print()
print(f"Polarization entanglement:")
print(f"  Concurrence: {C_pol:.4f}")
print(f"  Fidelity with |Φ+⟩: {F_pol:.4f}")
print(f"  Visibility: {visibility_pol:.4f}")
print()
print(f"OAM entanglement:")
print(f"  Concurrence: {C_oam:.4f}")
print(f"  Fidelity with Bell state: {F_oam:.4f}")
print(f"  Visibility: {visibility_oam:.4f}")
print()
print(f"Detection parameters:")
print(f"  Detector efficiency: {detector_efficiency:.0%}")
print(f"  OAM sorter efficiency: {oam_sorter_efficiency:.0%}")
print(f"  Total efficiency: {total_detection_efficiency:.1%}")
print(f"  Coincidence window: {coincidence_window*1e12:.0f} ps")
print()
print(f"Bell inequality:")
print(f"  Estimated CHSH: {S_estimated:.4f}")
print(f"  Violation: {'YES' if S_estimated > 2.0 else 'NO'}")
print()
print("Note: This simulation models the quantum state generation and measurement")
print("of hyperentangled photon pairs in polarization and OAM degrees of freedom.")
print("The cascaded SPDC configuration with path indistinguishability creates")
print("polarization entanglement, while SLM encoding creates OAM entanglement.")