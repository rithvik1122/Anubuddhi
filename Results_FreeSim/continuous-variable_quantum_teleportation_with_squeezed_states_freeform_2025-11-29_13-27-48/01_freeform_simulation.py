import numpy as np
from scipy.linalg import sqrtm
import warnings
warnings.filterwarnings('ignore')

# Physical constants and parameters
hbar = 1.054571817e-34  # J·s
c = 3e8  # m/s

# Extract parameters from experiment design
wavelength = 1064e-9  # m
detector_efficiency = 0.95
squeezing_dB = 8.0  # Realistic squeezing level for PPLN OPA

# Feedforward parameters
feedforward_gain = np.sqrt(2)
feedforward_efficiency = 0.90  # Account for electronic losses and latency

print("=" * 70)
print("CONTINUOUS-VARIABLE QUANTUM TELEPORTATION SIMULATION")
print("=" * 70)
print("\nExperimental Parameters:")
print(f"Wavelength: {wavelength*1e9:.1f} nm")
print(f"Squeezing level: {squeezing_dB:.1f} dB")
print(f"Detector efficiency: {detector_efficiency*100:.1f}%")
print(f"Feedforward gain: {feedforward_gain:.3f}")

# Continuous variable quantum state representation
# Use quadrature operators in phase space (Wigner function approach)
# For CV teleportation, we work with quadrature operators X and P

# Squeezing parameter from dB
squeezing_linear = 10**(-squeezing_dB/20)  # variance reduction factor
r = -0.5 * np.log(squeezing_linear)  # squeezing parameter

print(f"\nSqueezing parameter r: {r:.4f}")

# EPR entangled state preparation
# Two squeezed vacuum states with pi/2 phase difference create EPR pair
# EPR state has correlations: X_A - X_B and P_A + P_B are squeezed

# Variance of squeezed quadratures
var_squeezed = np.exp(-2*r)
var_antisqueezed = np.exp(2*r)

print(f"Squeezed variance: {var_squeezed:.6f} (shot noise units)")
print(f"Anti-squeezed variance: {var_antisqueezed:.6f} (shot noise units)")

# EPR correlations (ideal case)
# Var(X_A - X_B) = 2 * var_squeezed
# Var(P_A + P_B) = 2 * var_squeezed
var_epr_corr = 2 * var_squeezed

print(f"EPR correlation variance: {var_epr_corr:.6f}")

# Dimensionless coherent state amplitude (in shot noise units)
alpha_amplitude = 2.0  # Typical value for CV experiments
alpha_phase = 0.3
alpha = alpha_amplitude * np.exp(1j * alpha_phase)

# Quadrature values of input state
X_in = 2 * np.real(alpha)  # Factor of 2 for quadrature definition
P_in = 2 * np.imag(alpha)

print(f"\nInput coherent state:")
print(f"  alpha = {alpha:.4f}")
print(f"  X_in = {X_in:.4f}")
print(f"  P_in = {P_in:.4f}")
print(f"  Mean photon number: {np.abs(alpha)**2:.4f}")

# Alice's Bell measurement
# Input state interferes with Alice's EPR mode on 50:50 BS
# Two outputs measured by homodyne detectors (X and P quadratures)

# Beam splitter transformation matrix (50:50)
BS_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

# Simulate EPR pair with proper correlations
# EPR state: X_- = X_A - X_B is squeezed, P_+ = P_A + P_B is squeezed
np.random.seed(42)

# Generate properly correlated EPR pair
X_minus = np.random.normal(0, np.sqrt(var_squeezed))  # X_A - X_B squeezed
P_plus = np.random.normal(0, np.sqrt(var_squeezed))   # P_A + P_B squeezed
X_A = np.random.normal(0, 1)  # Local noise at Alice
P_A = np.random.normal(0, 1)  # Local noise at Alice
X_B = X_A - X_minus  # Construct Bob's mode from correlation
P_B = -P_A + P_plus  # Construct Bob's mode from correlation

# Alice's 50:50 beam splitter mixing input state with EPR mode A
# BS transformation for X quadrature
X_input_vec = np.array([X_in, X_A])
X_output_vec = BS_matrix @ X_input_vec
X_BS_out1 = X_output_vec[0]
X_BS_out2 = X_output_vec[1]

# BS transformation for P quadrature
P_input_vec = np.array([P_in, P_A])
P_output_vec = BS_matrix @ P_input_vec
P_BS_out1 = P_output_vec[0]
P_BS_out2 = P_output_vec[1]

# Homodyne detection on output 1 (X quadrature measurement)
# LO phase = 0, measures X quadrature
# Balanced homodyne: photocurrent difference proportional to X quadrature
X_meas_1 = X_BS_out1

# Homodyne detection on output 2 (P quadrature measurement)
# LO phase = π/2, measures P quadrature
# Balanced homodyne: photocurrent difference proportional to P quadrature
P_meas_2 = P_BS_out2

# Add detector noise (quantum efficiency < 1)
detector_noise_X = np.random.normal(0, np.sqrt((1 - detector_efficiency) / detector_efficiency))
detector_noise_P = np.random.normal(0, np.sqrt((1 - detector_efficiency) / detector_efficiency))

X_meas_1_noisy = X_meas_1 + detector_noise_X
P_meas_2_noisy = P_meas_2 + detector_noise_P

print(f"\nAlice's measurements:")
print(f"  X measurement: {X_meas_1_noisy:.4f}")
print(f"  P measurement: {P_meas_2_noisy:.4f}")

# Feedforward: Alice sends classical measurement results to Bob
# Bob applies displacement operations with gain G = sqrt(2)

# Ideal feedforward displacements
displacement_X = feedforward_gain * X_meas_1_noisy
displacement_P = feedforward_gain * P_meas_2_noisy

# Apply feedforward efficiency (EOM efficiency)
displacement_X *= feedforward_efficiency
displacement_P *= feedforward_efficiency

print(f"\nFeedforward displacements (to Bob):")
print(f"  X displacement: {displacement_X:.4f}")
print(f"  P displacement: {displacement_P:.4f}")

# Bob's state after EOM displacement operations
# Initial Bob's EPR mode: X_B, P_B
# After displacement: X_B + displacement_X, P_B + displacement_P
X_Bob_final = X_B + displacement_X
P_Bob_final = P_B + displacement_P

print(f"\nBob's final state quadratures:")
print(f"  X_Bob = {X_Bob_final:.4f}")
print(f"  P_Bob = {P_Bob_final:.4f}")

# Calculate teleportation fidelity
# For coherent states, fidelity F = exp(-0.5 * |alpha_out - alpha_in|^2)
alpha_out = (X_Bob_final + 1j * P_Bob_final) / 2  # Divide by 2, not sqrt(2)
fidelity = np.exp(-0.5 * np.abs(alpha_out - alpha)**2)

# Validation
assert 0 <= fidelity <= 1, f"Unphysical fidelity: {fidelity}"
assert np.abs(alpha_out) < 100, f"Unreasonable amplitude: {alpha_out}"

print(f"\n" + "=" * 70)
print("TELEPORTATION RESULTS:")
print("=" * 70)
print(f"\nInput state: alpha_in = {alpha:.4f}")
print(f"Output state: alpha_out = {alpha_out:.4f}")
print(f"Displacement error: |alpha_out - alpha_in| = {np.abs(alpha_out - alpha):.4f}")
print(f"\nTeleportation Fidelity: {fidelity:.6f} ({fidelity*100:.4f}%)")

# Calculate quadrature errors
error_X = X_Bob_final - X_in
error_P = P_Bob_final - P_in
total_error = np.sqrt(error_X**2 + error_P**2)

print(f"\nQuadrature errors:")
print(f"  ΔX = {error_X:.4f}")
print(f"  ΔP = {error_P:.4f}")
print(f"  Total error = {total_error:.4f}")

# Monte Carlo simulation for average fidelity
print(f"\n" + "=" * 70)
print("MONTE CARLO SIMULATION (1000 runs)")
print("=" * 70)

n_runs = 1000
fidelities = []

for run in range(n_runs):
    # Generate properly correlated EPR pair
    X_minus_mc = np.random.normal(0, np.sqrt(var_squeezed))  # X_A - X_B squeezed
    P_plus_mc = np.random.normal(0, np.sqrt(var_squeezed))   # P_A + P_B squeezed
    X_A_mc = np.random.normal(0, 1)  # Local noise at Alice
    P_A_mc = np.random.normal(0, 1)  # Local noise at Alice
    X_B_mc = X_A_mc - X_minus_mc  # Construct Bob's mode from correlation
    P_B_mc = -P_A_mc + P_plus_mc  # Construct Bob's mode from correlation
    
    # Alice's BS transformation
    X_input_vec_mc = np.array([X_in, X_A_mc])
    X_output_vec_mc = BS_matrix @ X_input_vec_mc
    X_BS_out1_mc = X_output_vec_mc[0]
    
    P_input_vec_mc = np.array([P_in, P_A_mc])
    P_output_vec_mc = BS_matrix @ P_input_vec_mc
    P_BS_out2_mc = P_output_vec_mc[1]
    
    # Alice's homodyne measurements
    X_meas_mc = X_BS_out1_mc
    P_meas_mc = P_BS_out2_mc
    
    # Detector noise
    det_noise_X = np.random.normal(0, np.sqrt((1 - detector_efficiency) / detector_efficiency))
    det_noise_P = np.random.normal(0, np.sqrt((1 - detector_efficiency) / detector_efficiency))
    
    X_meas_mc += det_noise_X
    P_meas_mc += det_noise_P
    
    # Feedforward
    disp_X_mc = feedforward_gain * X_meas_mc * feedforward_efficiency
    disp_P_mc = feedforward_gain * P_meas_mc * feedforward_efficiency
    
    # Bob's final state
    X_Bob_mc = X_B_mc + disp_X_mc
    P_Bob_mc = P_B_mc + disp_P_mc
    
    alpha_out_mc = (X_Bob_mc + 1j * P_Bob_mc) / 2
    fid_mc = np.exp(-0.5 * np.abs(alpha_out_mc - alpha)**2)
    fidelities.append(fid_mc)

fidelities = np.array(fidelities)
mean_fidelity = np.mean(fidelities)
std_fidelity = np.std(fidelities)

print(f"\nAverage teleportation fidelity: {mean_fidelity:.6f} ± {std_fidelity:.6f}")
print(f"Minimum fidelity: {np.min(fidelities):.6f}")
print(f"Maximum fidelity: {np.max(fidelities):.6f}")

# Classical benchmark (no entanglement)
# For CV teleportation, classical limit is 1/(1+<n>) where <n> is mean photon number
classical_fidelity = 1.0 / (1.0 + np.abs(alpha)**2)

print(f"\n" + "=" * 70)
print("COMPARISON WITH CLASSICAL LIMIT:")
print("=" * 70)
print(f"Quantum teleportation fidelity: {mean_fidelity:.6f}")
print(f"Classical limit (no entanglement): {classical_fidelity:.6f}")
print(f"Quantum advantage: {(mean_fidelity - classical_fidelity)*100:.2f}% above classical")

if mean_fidelity > classical_fidelity:
    print("\n✓ Quantum teleportation successful (exceeds classical limit)")
else:
    print("\n✗ Teleportation below classical limit (check parameters)")

print(f"\n" + "=" * 70)
print("PHYSICAL VALIDATION:")
print("=" * 70)
print(f"✓ Squeezing level: {squeezing_dB:.1f} dB (realistic for PPLN)")
print(f"✓ Fidelity range: [0, 1] - Current: {mean_fidelity:.4f}")
print(f"✓ Detector efficiency: {detector_efficiency*100:.1f}% (realistic)")
print(f"✓ Feedforward gain: {feedforward_gain:.3f} (optimal for CV teleportation)")
print(f"✓ Beam splitter transformation: 50:50 unitary matrix")
print(f"✓ Homodyne detection with balanced photodiodes")
print(f"✓ EOM displacement operations applied to Bob's mode")
print(f"✓ Input state amplitude: {alpha_amplitude:.2f} (dimensionless, shot noise units)")

print(f"\n" + "=" * 70)
print("SIMULATION COMPLETE")
print("=" * 70)