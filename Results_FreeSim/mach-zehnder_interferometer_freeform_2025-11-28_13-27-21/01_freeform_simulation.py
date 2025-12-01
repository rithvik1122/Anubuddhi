import numpy as np
import matplotlib.pyplot as plt

# Extract physical parameters from experiment design
wavelength = 632.8e-9  # m (He-Ne laser)
power = 5e-3  # W (5 mW)
linewidth = 1  # kHz (coherent laser)

# Beam splitter parameters
bs1_transmittance = 0.5
bs1_reflectance = 0.5
bs2_transmittance = 0.5
bs2_reflectance = 0.5

# Mirror reflectivities
mirror_upper_reflectivity = 0.99
mirror_lower_reflectivity = 0.99

# Detector efficiencies
detector1_efficiency = 0.85
detector2_efficiency = 0.85

# Physical constants
h = 6.62607015e-34  # J·s
c = 299792458  # m/s

# Calculate photon energy and photon flux
photon_energy = h * c / wavelength  # J
photon_flux = power / photon_energy  # photons/s

print("=" * 60)
print("MACH-ZEHNDER INTERFEROMETER SIMULATION")
print("=" * 60)
print(f"\nInput Parameters:")
print(f"  Wavelength: {wavelength*1e9:.1f} nm")
print(f"  Laser power: {power*1e3:.1f} mW")
print(f"  Photon flux: {photon_flux:.2e} photons/s")
print(f"  Photon energy: {photon_energy:.2e} J")

# Quantum state representation using complex amplitudes
# After BS1, the beam is split into two paths (upper and lower)
# Initial state: |ψ_in⟩ = |1⟩ (single mode input)
# After BS1: |ψ⟩ = (1/√2)(|upper⟩ + i|lower⟩)
# Note: 50/50 beam splitter introduces π/2 phase shift on reflection

# Beam splitter transformation matrix (50/50 BS)
# Using standard convention: transmitted gets no phase, reflected gets i
BS_matrix = (1/np.sqrt(2)) * np.array([[1, 1j], 
                                        [1j, 1]])

# Initial state (all intensity in input mode)
initial_amplitude = np.sqrt(photon_flux)
state_in = np.array([initial_amplitude, 0], dtype=complex)

# After BS1
state_after_bs1 = BS_matrix @ state_in
upper_arm_amplitude = state_after_bs1[0]
lower_arm_amplitude = state_after_bs1[1]

print(f"\nAfter BS1:")
print(f"  Upper arm amplitude: {np.abs(upper_arm_amplitude):.2e}")
print(f"  Lower arm amplitude: {np.abs(lower_arm_amplitude):.2e}")
print(f"  Upper arm phase: {np.angle(upper_arm_amplitude):.3f} rad")
print(f"  Lower arm phase: {np.angle(lower_arm_amplitude):.3f} rad")

# Apply mirror reflections with losses
upper_arm_amplitude *= np.sqrt(mirror_upper_reflectivity)
lower_arm_amplitude *= np.sqrt(mirror_lower_reflectivity)

# Scan phase shifter from 0 to 2π
phase_values = np.linspace(0, 2*np.pi, 100)
detector1_intensities = []
detector2_intensities = []

for phi in phase_values:
    # Apply phase shift to upper arm
    upper_with_phase = upper_arm_amplitude * np.exp(1j * phi)
    lower_no_phase = lower_arm_amplitude
    
    # State before BS2
    state_before_bs2 = np.array([upper_with_phase, lower_no_phase])
    
    # After BS2 (recombination)
    state_after_bs2 = BS_matrix @ state_before_bs2
    
    # Output modes
    detector1_amplitude = state_after_bs2[0]  # Transmission port
    detector2_amplitude = state_after_bs2[1]  # Reflection port
    
    # Calculate intensities (photon rates)
    intensity1 = np.abs(detector1_amplitude)**2 * detector1_efficiency
    intensity2 = np.abs(detector2_amplitude)**2 * detector2_efficiency
    
    detector1_intensities.append(intensity1)
    detector2_intensities.append(intensity2)

detector1_intensities = np.array(detector1_intensities)
detector2_intensities = np.array(detector2_intensities)

# Calculate visibility for both detectors
I1_max = np.max(detector1_intensities)
I1_min = np.min(detector1_intensities)
visibility1 = (I1_max - I1_min) / (I1_max + I1_min)

I2_max = np.max(detector2_intensities)
I2_min = np.min(detector2_intensities)
visibility2 = (I2_max - I2_min) / (I2_max + I2_min)

print(f"\n" + "=" * 60)
print("INTERFERENCE RESULTS")
print("=" * 60)

print(f"\nDetector 1 (Transmission Port):")
print(f"  Maximum intensity: {I1_max:.2e} photons/s")
print(f"  Minimum intensity: {I1_min:.2e} photons/s")
print(f"  Visibility: {visibility1:.4f}")

print(f"\nDetector 2 (Reflection Port):")
print(f"  Maximum intensity: {I2_max:.2e} photons/s")
print(f"  Minimum intensity: {I2_min:.2e} photons/s")
print(f"  Visibility: {visibility2:.4f}")

# Verify complementary behavior
total_intensity = detector1_intensities + detector2_intensities
total_variation = np.std(total_intensity) / np.mean(total_intensity)
print(f"\nComplementarity Check:")
print(f"  Total intensity variation: {total_variation:.2e}")
print(f"  (Should be ~0 for ideal complementary outputs)")

# Verify theoretical predictions
# For ideal MZI: I1 ∝ (1 + cos φ), I2 ∝ (1 - cos φ)
# Account for losses
expected_max = photon_flux * 0.5 * mirror_upper_reflectivity * 0.85
expected_min_approx = photon_flux * 0.5 * mirror_lower_reflectivity * 0.85 * 0.01

print(f"\nTheoretical vs Simulated (Detector 1):")
print(f"  Expected max (approx): {expected_max:.2e} photons/s")
print(f"  Simulated max: {I1_max:.2e} photons/s")

# Calculate fringe contrast at specific phase values
phi_0 = 0
phi_pi = np.pi
idx_0 = np.argmin(np.abs(phase_values - phi_0))
idx_pi = np.argmin(np.abs(phase_values - phi_pi))

print(f"\nInterference Pattern Analysis:")
print(f"  At φ=0: D1={detector1_intensities[idx_0]:.2e}, D2={detector2_intensities[idx_0]:.2e}")
print(f"  At φ=π: D1={detector1_intensities[idx_pi]:.2e}, D2={detector2_intensities[idx_pi]:.2e}")
print(f"  Ratio D1(0)/D1(π): {detector1_intensities[idx_0]/detector1_intensities[idx_pi]:.2f}")

# Energy conservation check
input_photon_rate = photon_flux
output_photon_rate_avg = np.mean(detector1_intensities + detector2_intensities)
loss_factor = mirror_upper_reflectivity * mirror_lower_reflectivity * 0.5
expected_output = input_photon_rate * loss_factor * detector1_efficiency

print(f"\nEnergy Conservation:")
print(f"  Input photon rate: {input_photon_rate:.2e} photons/s")
print(f"  Average output rate: {output_photon_rate_avg:.2e} photons/s")
print(f"  Expected (with losses): {expected_output:.2e} photons/s")
print(f"  Conservation ratio: {output_photon_rate_avg/input_photon_rate:.4f}")

print(f"\n" + "=" * 60)
print("PHYSICAL VALIDITY CHECKS")
print("=" * 60)
print(f"  Visibility in valid range [0,1]: {0 <= visibility1 <= 1 and 0 <= visibility2 <= 1}")
print(f"  Intensities non-negative: {np.all(detector1_intensities >= 0) and np.all(detector2_intensities >= 0)}")
print(f"  Complementary behavior: {total_variation < 0.01}")
print(f"  Energy conserved (within losses): {0.3 < output_photon_rate_avg/input_photon_rate < 0.6}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(phase_values/np.pi, detector1_intensities, 'b-', linewidth=2, label='Detector 1')
ax1.plot(phase_values/np.pi, detector2_intensities, 'r-', linewidth=2, label='Detector 2')
ax1.set_xlabel('Phase Shift (units of π)', fontsize=12)
ax1.set_ylabel('Intensity (photons/s)', fontsize=12)
ax1.set_title('Mach-Zehnder Interferometer: Detector Outputs', fontsize=14)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

ax2.plot(phase_values/np.pi, detector1_intensities + detector2_intensities, 'g-', linewidth=2)
ax2.set_xlabel('Phase Shift (units of π)', fontsize=12)
ax2.set_ylabel('Total Intensity (photons/s)', fontsize=12)
ax2.set_title('Total Output (Energy Conservation Check)', fontsize=14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mach_zehnder_interference.png', dpi=150, bbox_inches='tight')
print(f"\nPlot saved as 'mach_zehnder_interference.png'")

print("\n" + "=" * 60)
print("SIMULATION COMPLETE")
print("=" * 60)