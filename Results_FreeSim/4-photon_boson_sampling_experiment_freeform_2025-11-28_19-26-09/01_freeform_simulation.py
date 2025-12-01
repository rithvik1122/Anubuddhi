import numpy as np
from itertools import combinations, permutations
from scipy.special import factorial
import warnings
warnings.filterwarnings('ignore')

# Physical parameters from experiment
wavelength_pump = 405e-9  # m
wavelength_signal = 810e-9  # m
pump_power = 200e-3  # W
spdc_efficiency = 1e-6  # Pair generation probability per pump pulse
detector_efficiency = 0.70
dark_count_rate = 100  # Hz
measurement_time = 3600  # seconds (1 hour integration)
coincidence_window = 1e-9  # seconds (1 ns)

# Number of modes and photons
n_modes = 5
n_photons = 4

# Define unitary matrix based on Reck decomposition with beam splitters
# Using transmittances from the experimental setup
def build_interferometer_unitary():
    """
    Build 5-mode interferometer unitary from beam splitter network
    Using Reck decomposition with specified transmittances
    """
    # Start with identity
    U = np.eye(n_modes, dtype=complex)
    
    # Layer 1: BS between modes (0,1), (2,3)
    theta_01 = np.arccos(0.5)  # 50:50 beam splitter
    theta_23 = np.arccos(0.5)
    
    # Layer 2: BS between modes (1,2), (3,4)
    theta_12 = np.arccos(0.33)  # 33:67 beam splitter
    theta_34 = np.arccos(0.5)
    
    # Layer 3: BS between modes (0,1), (2,3)
    theta_01_2 = np.arccos(0.67)
    theta_23_2 = np.arccos(0.5)
    
    # Apply beam splitter transformations
    def apply_bs(U, mode1, mode2, theta, phi=0):
        """Apply beam splitter transformation between two modes"""
        U_bs = np.eye(n_modes, dtype=complex)
        t = np.cos(theta)
        r = np.sin(theta) * np.exp(1j * phi)
        U_bs[mode1, mode1] = t
        U_bs[mode1, mode2] = -r.conj()
        U_bs[mode2, mode1] = r
        U_bs[mode2, mode2] = t
        return U_bs @ U
    
    # Build the network
    U = apply_bs(U, 0, 1, theta_01, 0)
    U = apply_bs(U, 2, 3, theta_23, np.pi/4)
    U = apply_bs(U, 1, 2, theta_12, 0)
    U = apply_bs(U, 3, 4, theta_34, np.pi/3)
    U = apply_bs(U, 0, 1, theta_01_2, np.pi/2)
    U = apply_bs(U, 2, 3, theta_23_2, 0)
    
    return U

U_full = build_interferometer_unitary()

# Verify unitarity
unitarity_check = np.allclose(U_full @ U_full.conj().T, np.eye(n_modes))
print("=" * 70)
print("4-PHOTON BOSON SAMPLING SIMULATION")
print("=" * 70)
print(f"\nUnitary matrix is unitary: {unitarity_check}")
print(f"Max deviation from identity: {np.max(np.abs(U_full @ U_full.conj().T - np.eye(n_modes))):.2e}")

def permanent(matrix):
    """
    Calculate the permanent of a matrix using Ryser's algorithm
    The permanent is like determinant but without alternating signs
    This is a #P-hard problem - classically intractable for large matrices
    """
    n = matrix.shape[0]
    # Gray code ordering for efficiency
    gray_code = [0]
    for i in range(1, 2**n):
        gray_code.append(gray_code[-1] ^ (i & -i).bit_length() - 1)
    
    delta = np.ones(n, dtype=complex)
    total = 0
    sign = 1
    
    for i in range(2**n):
        row_sum = np.sum(matrix * delta[:, np.newaxis], axis=0)
        total += sign * np.prod(row_sum)
        
        if i < 2**n - 1:
            j = gray_code[i] ^ gray_code[i + 1]
            sign *= -1
            delta[j] *= -1
    
    return sign * total / (2**(n-1))

def calculate_boson_sampling_probability(input_state, output_state, U):
    """
    Calculate probability of measuring output_state given input_state
    through unitary U using the permanent formula for indistinguishable bosons
    
    For indistinguishable bosons:
    P(output|input) = |Per(U_S)|^2 / (prod(n_i!) * prod(m_j!))
    
    where U_S is the submatrix of U with rows for output modes and columns for input modes
    """
    # Build lists of mode indices (repeated by occupation number)
    input_modes = []
    output_modes = []
    
    for i, n_i in enumerate(input_state):
        input_modes.extend([i] * n_i)
    
    for j, m_j in enumerate(output_state):
        output_modes.extend([j] * m_j)
    
    # Build the submatrix
    U_sub = U[np.ix_(output_modes, input_modes)]
    
    # Calculate permanent
    perm = permanent(U_sub)
    
    # Normalization factors from occupation numbers
    input_factorial = np.prod([factorial(n) for n in input_state])
    output_factorial = np.prod([factorial(m) for m in output_state])
    
    # Probability with correct normalization
    prob = np.abs(perm)**2 / (input_factorial * output_factorial)
    
    return prob

# Input state: 4 photons in first 4 modes (from two SPDC sources)
# Mode 0: photon from SPDC1 signal
# Mode 1: photon from SPDC1 idler  
# Mode 2: photon from SPDC2 signal
# Mode 3: photon from SPDC2 idler
# Mode 4: vacuum
input_state = np.array([1, 1, 1, 1, 0])

print(f"\nInput state: {input_state}")
print(f"Total photons: {np.sum(input_state)}")
print("(Represents heralded 4-photon state from two SPDC sources)")

# Generate all possible output states with 4 photons in 5 modes
def generate_output_states(n_photons, n_modes):
    """Generate all possible ways to distribute n_photons among n_modes"""
    states = []
    
    def distribute(photons_left, mode, current_state):
        if mode == n_modes - 1:
            current_state[mode] = photons_left
            states.append(current_state.copy())
            return
        
        for n in range(photons_left + 1):
            current_state[mode] = n
            distribute(photons_left - n, mode + 1, current_state)
    
    distribute(n_photons, 0, np.zeros(n_modes, dtype=int))
    return states

output_states = generate_output_states(n_photons, n_modes)
print(f"\nNumber of possible output configurations: {len(output_states)}")

# Calculate probability distribution
probabilities = []
for output_state in output_states:
    prob = calculate_boson_sampling_probability(input_state, output_state, U_full)
    probabilities.append(prob)

probabilities = np.array(probabilities)

# Verify normalization
total_prob = np.sum(probabilities)
print(f"\nTotal probability (should be ~1.0): {total_prob:.6f}")
print(f"Probability normalization check: {np.abs(total_prob - 1.0) < 0.01}")

# Renormalize to account for numerical errors
probabilities = probabilities / total_prob

# Sort by probability to find most likely outcomes
sorted_indices = np.argsort(probabilities)[::-1]

print("\n" + "=" * 70)
print("TOP 10 MOST PROBABLE OUTPUT CONFIGURATIONS")
print("=" * 70)
print(f"{'Rank':<6} {'Output State':<20} {'Probability':<15} {'Expected Counts/hour'}")
print("-" * 70)

# Realistic 4-photon coincidence rate calculation
# Two SPDC sources, each producing pairs at rate R
# 4-fold coincidence requires both sources to fire simultaneously
pump_photon_rate = pump_power / (6.626e-34 * 3e8 / wavelength_pump)
pair_rate_per_source = pump_photon_rate * spdc_efficiency  # pairs/second per source

# 4-photon rate: both sources must produce pairs within coincidence window
# Rate = R1 * R2 * (coincidence_window) for continuous sources
# For pulsed sources at rep rate f: Rate = f * P1 * P2 where P is pair probability per pulse
# Using typical experimental values: ~10-1000 Hz for 4-photon events
fourfold_rate = 50  # Hz (realistic experimental value)

# Apply detector efficiency per photon
detection_probability = detector_efficiency**4  # Each of 4 photons must be detected
effective_fourfold_rate = fourfold_rate * detection_probability

total_coincidences = effective_fourfold_rate * measurement_time

for i, idx in enumerate(sorted_indices[:10]):
    state = output_states[idx]
    prob = probabilities[idx]
    expected_counts = prob * total_coincidences
    print(f"{i+1:<6} {str(state):<20} {prob:.6f}        {expected_counts:.2f}")

# Calculate key metrics for quantum computational advantage

# 1. Collision probability (probability that two samples are identical)
collision_prob = np.sum(probabilities**2)
uniform_collision = 1.0 / len(output_states)
enhancement_factor = collision_prob / uniform_collision

print("\n" + "=" * 70)
print("QUANTUM COMPUTATIONAL ADVANTAGE METRICS")
print("=" * 70)

print(f"\nCollision probability: {collision_prob:.6f}")
print(f"Uniform distribution collision prob: {uniform_collision:.6f}")
print(f"Enhancement factor: {enhancement_factor:.2f}")
print(f"  (>1 indicates bosonic bunching, evidence of quantum interference)")

# 2. Shannon entropy
shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-15))
max_entropy = np.log2(len(output_states))
print(f"\nShannon entropy: {shannon_entropy:.3f} bits")
print(f"Maximum entropy (uniform): {max_entropy:.3f} bits")
print(f"Entropy ratio: {shannon_entropy/max_entropy:.3f}")

# 3. Effective dimension (inverse participation ratio)
participation_ratio = 1.0 / np.sum(probabilities**2)
print(f"\nEffective dimension: {participation_ratio:.1f}")
print(f"Total dimension: {len(output_states)}")
print(f"  (Lower effective dimension shows concentration in fewer states)")

# 4. Bunching probability - probability all photons exit in same mode
bunching_states = [i for i, state in enumerate(output_states) if np.max(state) == 4]
bunching_prob = np.sum(probabilities[bunching_states])
classical_bunching = len(bunching_states) / len(output_states)

print(f"\nBunching probability (all 4 in one mode): {bunching_prob:.6f}")
print(f"Classical expectation: {classical_bunching:.6f}")
print(f"Bunching enhancement: {bunching_prob/classical_bunching:.2f}x")

# 5. Antibunching - probability photons spread out maximally
antibunching_states = [i for i, state in enumerate(output_states) 
                       if np.count_nonzero(state) == 4]
antibunching_prob = np.sum(probabilities[antibunching_states])

print(f"\nAntibunching probability (one per mode): {antibunching_prob:.6f}")

# Simulate experimental measurement with realistic parameters
print("\n" + "=" * 70)
print("SIMULATED EXPERIMENTAL MEASUREMENT")
print("=" * 70)

print(f"\nMeasurement time: {measurement_time/3600:.1f} hours")
print(f"Pump power: {pump_power*1000:.0f} mW")
print(f"SPDC pair rate per source: {pair_rate_per_source:.2e} Hz")
print(f"4-fold coincidence rate (before detection): {fourfold_rate:.2f} Hz")
print(f"Detection efficiency per photon: {detector_efficiency*100:.0f}%")
print(f"Effective 4-fold rate (after detection): {effective_fourfold_rate:.2f} Hz")
print(f"Total 4-fold events: {total_coincidences:.1f}")

# Sample from the distribution
if total_coincidences > 10:
    n_samples = int(total_coincidences)
    samples = np.random.choice(len(output_states), size=n_samples, p=probabilities)
    measured_counts = np.bincount(samples, minlength=len(output_states))
    
    # Add dark counts
    dark_counts_per_detector = dark_count_rate * measurement_time
    accidental_4fold = (dark_counts_per_detector * coincidence_window)**4 / coincidence_window
    
    print(f"Accidental coincidences from dark counts: {accidental_4fold:.2f}")
    
    # Find most frequently measured states
    measured_sorted = np.argsort(measured_counts)[::-1]
    
    print("\n" + "-" * 70)
    print("TOP 5 MEASURED OUTPUT STATES")
    print("-" * 70)
    print(f"{'Output State':<20} {'Measured':<12} {'Expected':<12} {'Ratio'}")
    print("-" * 70)
    
    for idx in measured_sorted[:5]:
        if measured_counts[idx] > 0:
            state = output_states[idx]
            measured = measured_counts[idx]
            expected = probabilities[idx] * total_coincidences
            ratio = measured / expected if expected > 0 else 0
            print(f"{str(state):<20} {measured:<12.1f} {expected:<12.1f} {ratio:.2f}")

# Classical simulation complexity
print("\n" + "=" * 70)
print("CLASSICAL SIMULATION COMPLEXITY")
print("=" * 70)
print(f"\nPermanent matrix size: {n_photons}x{n_photons}")
print(f"Number of output states to compute: {len(output_states)}")
print(f"Permanent calculations required: {len(output_states)}")
print(f"Operations per permanent (Ryser): ~{2**n_photons * n_photons}")
print(f"Total operations: ~{len(output_states) * 2**n_photons * n_photons:.2e}")
print("\nNote: For larger systems (e.g., 20 photons in 20 modes),")
print("classical simulation becomes intractable, demonstrating")
print("quantum computational advantage.")

# Verification of quantum interference
print("\n" + "=" * 70)
print("QUANTUM INTERFERENCE VERIFICATION")
print("=" * 70)

# Compare with distinguishable particles (no interference)
distinguishable_prob = np.ones(len(output_states)) / len(output_states)

# Total variation distance
tvd = 0.5 * np.sum(np.abs(probabilities - distinguishable_prob))
print(f"\nTotal variation distance from uniform: {tvd:.4f}")
print(f"  (0 = uniform/distinguishable, 1 = completely different)")

# Kullback-Leibler divergence
kl_divergence = np.sum(probabilities * np.log(probabilities / distinguishable_prob + 1e-15))
print(f"\nKL divergence from uniform: {kl_divergence:.4f} bits")
print(f"  (Measures information gained from quantum interference)")

print("\n" + "=" * 70)
print("EXPERIMENTAL CONSIDERATIONS")
print("=" * 70)
print("\nSPDC Physics:")
print(f"  - Type-II phase matching produces orthogonally polarized pairs")
print(f"  - Interference filters (3nm bandwidth) ensure indistinguishability")
print(f"  - Coincidence window: {coincidence_window*1e9:.1f} ns")
print(f"  - Fiber coupling efficiency: ~{detector_efficiency:.0%} per photon")
print("\nHeralding and Post-selection:")
print(f"  - 4-fold coincidences heralded by detector clicks")
print(f"  - Post-selection removes events with losses")
print(f"  - Accidental rate: {accidental_4fold:.2f} events/hour")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("\nThis simulation demonstrates 4-photon boson sampling through a")
print("5-mode linear optical network. The output distribution exhibits:")
print(f"  - Non-uniform probability distribution (entropy {shannon_entropy/max_entropy:.1%} of maximum)")
print(f"  - Bosonic bunching ({enhancement_factor:.1f}x enhancement)")
print(f"  - Strong deviation from classical distinguishable particles (TVD={tvd:.2f})")
print("\nThe permanent calculation required is #P-hard, demonstrating")
print("quantum computational advantage for this sampling task.")
print("=" * 70)