import numpy as np
import matplotlib.pyplot as plt

# Physical parameters from experiment design
wavelength = 632.8e-9  # meters (He-Ne laser)
power = 5e-3  # 5 mW
linewidth = 1  # kHz (very coherent)

# Optical component parameters
bs1_transmittance = 0.5
bs2_transmittance = 0.5
mirror_reflectivity = 0.99
detector_efficiency = 0.95

# Beam splitter phase convention for 50:50 splitter
# Transmitted: amplitude * 1/sqrt(2)
# Reflected: amplitude * i/sqrt(2) (90 degree phase shift)

def beam_splitter_transform(input_amplitude_transmitted, input_amplitude_reflected):
    """
    50:50 beam splitter transformation
    Returns (output_transmitted, output_reflected)
    """
    t = np.sqrt(0.5)  # transmission amplitude
    r = 1j * np.sqrt(0.5)  # reflection amplitude (with i phase)
    
    output_transmitted = t * input_amplitude_transmitted + r * input_amplitude_reflected
    output_reflected = r * input_amplitude_transmitted + t * input_amplitude_reflected
    
    return output_transmitted, output_reflected

def mirror_reflect(amplitude, reflectivity=0.99):
    """Mirror reflection with loss"""
    return np.sqrt(reflectivity) * amplitude

def apply_phase_shift(amplitude, phase):
    """Apply phase shift to amplitude"""
    return amplitude * np.exp(1j * phase)

# Simulate Mach-Zehnder interferometer
def simulate_mz_interferometer(phase_shift):
    """
    Simulate MZ interferometer for a given phase shift
    Returns intensities at both detectors
    """
    # Initial coherent field amplitude (normalized to 1 for simplicity)
    initial_amplitude = 1.0 + 0j
    
    # First beam splitter (BS1)
    # Input from laser goes to transmitted port
    # No input on reflected port
    upper_arm, lower_arm = beam_splitter_transform(initial_amplitude, 0)
    
    # Upper arm path
    # Mirror at (3.0, 5.0) - reflects upward beam
    upper_arm = mirror_reflect(upper_arm, mirror_reflectivity)
    
    # Phase shifter at (5.5, 5.0)
    upper_arm = apply_phase_shift(upper_arm, phase_shift)
    
    # Mirror at (8.0, 5.0) - upper corner
    upper_arm = mirror_reflect(upper_arm, mirror_reflectivity)
    
    # Lower arm path
    # Mirror at (3.0, 1.0) - reflects downward beam
    lower_arm = mirror_reflect(lower_arm, mirror_reflectivity)
    
    # Mirror at (8.0, 1.0) - lower corner
    lower_arm = mirror_reflect(lower_arm, mirror_reflectivity)
    
    # Second beam splitter (BS2) at (8.0, 3.0)
    # Upper arm comes from above (reflected port of BS2)
    # Lower arm comes from left (transmitted port of BS2)
    detector1_amplitude, detector2_amplitude = beam_splitter_transform(lower_arm, upper_arm)
    
    # Calculate intensities
    intensity1 = np.abs(detector1_amplitude)**2
    intensity2 = np.abs(detector2_amplitude)**2
    
    # Apply detector efficiency
    intensity1 *= detector_efficiency
    intensity2 *= detector_efficiency
    
    return intensity1, intensity2

# Scan phase from 0 to 2π
num_points = 200
phase_array = np.linspace(0, 2*np.pi, num_points)
intensity1_array = np.zeros(num_points)
intensity2_array = np.zeros(num_points)

for i, phase in enumerate(phase_array):
    intensity1_array[i], intensity2_array[i] = simulate_mz_interferometer(phase)

# Calculate visibility for both detectors
I1_max = np.max(intensity1_array)
I1_min = np.min(intensity1_array)
visibility1 = (I1_max - I1_min) / (I1_max + I1_min)

I2_max = np.max(intensity2_array)
I2_min = np.min(intensity2_array)
visibility2 = (I2_max - I2_min) / (I2_max + I2_min)

# Verify energy conservation
total_intensity = intensity1_array + intensity2_array

# Theoretical predictions accounting for mirror losses
# Each path has 2 mirrors, so loss factor is (0.99)^2 per arm
# Both arms have same loss, so total transmission through interferometer
mirror_loss_factor = mirror_reflectivity**4  # 4 mirrors total (2 per arm)
expected_total = detector_efficiency * mirror_loss_factor

# Calculate contrast at specific phase points
phase_0 = 0.0
phase_pi = np.pi
I1_0, I2_0 = simulate_mz_interferometer(phase_0)
I1_pi, I2_pi = simulate_mz_interferometer(phase_pi)

# Print results
print("=" * 60)
print("MACH-ZEHNDER INTERFEROMETER SIMULATION")
print("=" * 60)
print(f"\nExperimental Parameters:")
print(f"  Wavelength: {wavelength*1e9:.1f} nm")
print(f"  Laser Power: {power*1e3:.1f} mW")
print(f"  Linewidth: {linewidth} kHz")
print(f"  Mirror Reflectivity: {mirror_reflectivity*100:.1f}%")
print(f"  Detector Efficiency: {detector_efficiency*100:.1f}%")

print(f"\n" + "=" * 60)
print("INTERFERENCE PATTERN ANALYSIS")
print("=" * 60)

print(f"\nDetector 1 (Transmitted Port):")
print(f"  Maximum Intensity: {I1_max:.6f}")
print(f"  Minimum Intensity: {I1_min:.6f}")
print(f"  Visibility: {visibility1:.4f} ({visibility1*100:.2f}%)")
print(f"  Intensity at φ=0: {I1_0:.6f}")
print(f"  Intensity at φ=π: {I1_pi:.6f}")

print(f"\nDetector 2 (Reflected Port):")
print(f"  Maximum Intensity: {I2_max:.6f}")
print(f"  Minimum Intensity: {I2_min:.6f}")
print(f"  Visibility: {visibility2:.4f} ({visibility2*100:.2f}%)")
print(f"  Intensity at φ=0: {I2_0:.6f}")
print(f"  Intensity at φ=π: {I2_pi:.6f}")

print(f"\n" + "=" * 60)
print("COMPLEMENTARITY CHECK")
print("=" * 60)
print(f"\nTotal intensity (averaged): {np.mean(total_intensity):.6f}")
print(f"Expected total (with losses): {expected_total:.6f}")
print(f"Energy conservation error: {np.std(total_intensity)/np.mean(total_intensity)*100:.3f}%")

# Verify theoretical prediction: I1 ∝ cos²(φ/2), I2 ∝ sin²(φ/2)
print(f"\n" + "=" * 60)
print("THEORETICAL COMPARISON")
print("=" * 60)

# Account for all losses
normalization = mirror_loss_factor * detector_efficiency

# Theoretical intensities
I1_theory = normalization * np.cos(phase_array/2)**2
I2_theory = normalization * np.sin(phase_array/2)**2

# Calculate RMS error
rms_error_1 = np.sqrt(np.mean((intensity1_array - I1_theory)**2))
rms_error_2 = np.sqrt(np.mean((intensity2_array - I2_theory)**2))

print(f"\nDetector 1 vs cos²(φ/2) prediction:")
print(f"  RMS Error: {rms_error_1:.8f}")
print(f"  Relative Error: {rms_error_1/np.mean(intensity1_array)*100:.4f}%")

print(f"\nDetector 2 vs sin²(φ/2) prediction:")
print(f"  RMS Error: {rms_error_2:.8f}")
print(f"  Relative Error: {rms_error_2/np.mean(intensity2_array)*100:.4f}%")

print(f"\n" + "=" * 60)
print("WAVE-PARTICLE DUALITY DEMONSTRATION")
print("=" * 60)
print(f"\nHigh visibility ({visibility1*100:.1f}%) confirms wave nature:")
print(f"  - Coherent superposition of paths")
print(f"  - Phase-dependent interference")
print(f"  - Complementary output ports")
print(f"\nPerfect anti-correlation between detectors:")
print(f"  - When D1 is bright, D2 is dark (and vice versa)")
print(f"  - Demonstrates which-path information erasure")

# Check phase relationship
phase_d1_max = phase_array[np.argmax(intensity1_array)]
phase_d2_max = phase_array[np.argmax(intensity2_array)]
print(f"\nPhase at D1 maximum: {phase_d1_max:.4f} rad ({phase_d1_max*180/np.pi:.1f}°)")
print(f"Phase at D2 maximum: {phase_d2_max:.4f} rad ({phase_d2_max*180/np.pi:.1f}°)")
print(f"Phase difference: {abs(phase_d2_max - phase_d1_max):.4f} rad ({abs(phase_d2_max - phase_d1_max)*180/np.pi:.1f}°)")

print(f"\n" + "=" * 60)
print("SIMULATION COMPLETE")
print("=" * 60)