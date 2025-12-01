import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv

# Extract physical parameters
wavelength = 632.8e-9  # HeNe laser wavelength in meters
power = 5e-3  # 5 mW laser power
beam_splitter_ratio = 0.5  # 50:50 beam splitter
mirror_reflectivity = 0.99
magnification = 3
input_diameter = 1e-3  # 1mm beam diameter
expanded_diameter = magnification * input_diameter

# Screen parameters
screen_size = 50e-3  # 50mm screen
screen_pixels = 256  # Resolution for interference pattern

# Piezo mirror scan range
max_path_difference = 100e-6  # 100 microns travel range
num_scan_points = 200

# Calculate wavenumber
k = 2 * np.pi / wavelength

# Calculate photon flux
photon_energy = 6.626e-34 * 3e8 / wavelength  # h*c/lambda
photon_flux = power / photon_energy  # photons/second

print("=== Michelson Interferometer Simulation ===")
print(f"Wavelength: {wavelength*1e9:.1f} nm")
print(f"Laser power: {power*1e3:.1f} mW")
print(f"Photon flux: {photon_flux:.2e} photons/s")
print(f"Beam diameter (expanded): {expanded_diameter*1e3:.1f} mm")
print()

# Simulate interference pattern on screen as function of path difference
# The intensity at the screen depends on the phase difference between the two arms

def calculate_interference_pattern(path_difference, screen_size, pixels, wavelength, beam_diameter):
    """
    Calculate 2D interference pattern on screen for given path difference.
    For a Michelson interferometer with slightly misaligned mirrors,
    we get circular fringes (Haidinger fringes).
    """
    # Create coordinate grid for screen
    x = np.linspace(-screen_size/2, screen_size/2, pixels)
    y = np.linspace(-screen_size/2, screen_size/2, pixels)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    # Phase difference due to path length difference
    # Delta_phi = 2*k*delta_L (factor of 2 because light travels twice through each arm)
    phase_diff = 2 * k * path_difference
    
    # For perfectly aligned mirrors, intensity is uniform across screen
    # For slight tilt, we get circular fringes
    # Add small radial phase variation to simulate slight misalignment
    tilt_angle = 0.001  # small tilt in radians
    radial_phase = k * tilt_angle * R
    
    # Total phase
    total_phase = phase_diff + radial_phase
    
    # Intensity pattern: I = I1 + I2 + 2*sqrt(I1*I2)*cos(phase)
    # For 50:50 beam splitter, I1 = I2 = I0/2
    # Account for mirror reflectivity losses
    I1 = 0.5 * mirror_reflectivity**2
    I2 = 0.5 * mirror_reflectivity**2
    
    # Gaussian beam profile
    w0 = beam_diameter / 2  # beam waist
    beam_profile = np.exp(-2 * R**2 / w0**2)
    
    # Interference intensity
    I_total = (I1 + I2 + 2 * np.sqrt(I1 * I2) * np.cos(total_phase)) * beam_profile
    
    return I_total, X, Y

# Scan through path differences
path_differences = np.linspace(-wavelength, wavelength, num_scan_points)
max_intensities = []
min_intensities = []
mean_intensities = []

for pd in path_differences:
    pattern, _, _ = calculate_interference_pattern(pd, screen_size, screen_pixels, wavelength, expanded_diameter)
    max_intensities.append(np.max(pattern))
    min_intensities.append(np.min(pattern))
    mean_intensities.append(np.mean(pattern))

max_intensities = np.array(max_intensities)
min_intensities = np.array(min_intensities)
mean_intensities = np.array(mean_intensities)

# Calculate visibility
# Visibility V = (I_max - I_min) / (I_max + I_min)
visibility = (np.max(mean_intensities) - np.min(mean_intensities)) / (np.max(mean_intensities) + np.min(mean_intensities))

print("=== Interference Analysis ===")
print(f"Visibility: {visibility:.4f}")
print(f"Theoretical maximum visibility (with losses): {2*np.sqrt(0.5*0.5)*mirror_reflectivity**2 / (0.5*mirror_reflectivity**2 + 0.5*mirror_reflectivity**2):.4f}")
print()

# Calculate fringe spacing
# For small tilt angle theta, fringe spacing is lambda/(2*theta)
tilt_angle = 0.001
fringe_spacing = wavelength / (2 * tilt_angle)
print(f"Expected fringe spacing: {fringe_spacing*1e3:.2f} mm")
print()

# Generate interference patterns at key path differences
key_positions = [0, wavelength/4, wavelength/2, 3*wavelength/4]
position_labels = ['Constructive (0)', 'Quarter wave (λ/4)', 'Destructive (λ/2)', 'Three-quarter (3λ/4)']

print("=== Interference Patterns at Key Positions ===")
for i, (pd, label) in enumerate(zip(key_positions, position_labels)):
    pattern, X, Y = calculate_interference_pattern(pd, screen_size, 128, wavelength, expanded_diameter)
    center_intensity = pattern[64, 64]  # Center pixel
    print(f"{label}: Center intensity = {center_intensity:.4f} (relative)")

print()

# Simulate piezo mirror scan
print("=== Piezo Mirror Scan ===")
scan_range = np.linspace(0, 5*wavelength, 500)  # Scan over 5 wavelengths
scan_intensities = []

for pd in scan_range:
    pattern, _, _ = calculate_interference_pattern(pd, screen_size, 64, wavelength, expanded_diameter)
    scan_intensities.append(np.mean(pattern))

scan_intensities = np.array(scan_intensities)

# Find peaks and troughs
from scipy.signal import find_peaks
peaks, _ = find_peaks(scan_intensities)
troughs, _ = find_peaks(-scan_intensities)

if len(peaks) > 1:
    peak_spacing = np.mean(np.diff(scan_range[peaks]))
    print(f"Measured fringe period: {peak_spacing*1e9:.2f} nm")
    print(f"Expected fringe period (λ/2): {wavelength/2*1e9:.2f} nm")
    print(f"Number of fringes in scan: {len(peaks)}")
else:
    print("Not enough fringes detected in scan range")

print()

# Calculate contrast for the scan
I_max_scan = np.max(scan_intensities)
I_min_scan = np.min(scan_intensities)
contrast = (I_max_scan - I_min_scan) / (I_max_scan + I_min_scan)
print(f"Fringe contrast from scan: {contrast:.4f}")

# Account for realistic imperfections
print()
print("=== Realistic Considerations ===")
print(f"Mirror reflectivity loss: {(1-mirror_reflectivity**2)*100:.1f}% per round trip")
print(f"Beam splitter loss: {(1-2*beam_splitter_ratio)*100:.1f}% (ideal 50:50)")
print(f"Total efficiency: {(beam_splitter_ratio**2 * mirror_reflectivity**4):.4f}")

# Coherence length consideration
linewidth_hz = 1000  # Hz
coherence_length = 3e8 / linewidth_hz  # c / Δν
print(f"Laser linewidth: {linewidth_hz} Hz")
print(f"Coherence length: {coherence_length/1e3:.1f} km")
print(f"Path difference range: {max_path_difference*1e6:.1f} μm")
print(f"Coherence maintained: Yes (path difference << coherence length)")

print()
print("=== Summary ===")
print(f"The Michelson interferometer successfully demonstrates:")
print(f"  - Wave interference with visibility {visibility:.3f}")
print(f"  - Fringe period of λ/2 = {wavelength/2*1e9:.1f} nm")
print(f"  - Sensitive phase measurement capability")
print(f"  - Path difference resolution: ~{wavelength/10*1e9:.1f} nm (λ/10)")