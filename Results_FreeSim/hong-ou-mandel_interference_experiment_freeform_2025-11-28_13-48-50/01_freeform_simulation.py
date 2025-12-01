import numpy as np
from scipy.integrate import simps
from scipy.special import hermite
import matplotlib.pyplot as plt

# Physical constants
c = 3e8  # m/s
hbar = 1.054571817e-34  # J*s

# Extract parameters from experiment
pump_wavelength = 405e-9  # m
pump_power = 100e-3  # W
signal_wavelength = 810e-9  # m
idler_wavelength = 810e-9  # m

# BBO crystal parameters
crystal_length = 2e-3  # m
spdc_efficiency = 1e-12  # Realistic SPDC pair generation efficiency

# Detector parameters
detector_efficiency = 0.65
dark_count_rate = 25  # Hz
timing_resolution = 50e-12  # s
coincidence_window = 1e-9  # s

# Beam splitter parameters
bs_reflectivity = 0.5
bs_transmissivity = 0.5

# Delay stage scan parameters
delay_range = 100e-6  # m (100 microns)
delay_steps = 201
delay_positions = np.linspace(-delay_range/2, delay_range/2, delay_steps)

# Calculate temporal delays from path length differences
time_delays = 2 * delay_positions / c  # Factor of 2 for round trip

# Photon temporal wavepacket parameters
# Coherence time determined by spectral bandwidth
spectral_bandwidth = 3e-9  # m (3 nm interference filter)
coherence_time = signal_wavelength**2 / (c * spectral_bandwidth)
coherence_length = c * coherence_time

print("=" * 60)
print("Hong-Ou-Mandel Interference Simulation")
print("=" * 60)
print(f"Signal/Idler wavelength: {signal_wavelength*1e9:.1f} nm")
print(f"Coherence time: {coherence_time*1e15:.2f} fs")
print(f"Coherence length: {coherence_length*1e6:.2f} μm")
print(f"Detector efficiency: {detector_efficiency*100:.1f}%")
print(f"Coincidence window: {coincidence_window*1e9:.2f} ns")
print()

# Define photon wavepacket in time domain (Gaussian)
def photon_wavepacket(t, t0=0, sigma=None):
    """Gaussian temporal wavepacket for a photon"""
    if sigma is None:
        sigma = coherence_time / (2 * np.sqrt(2 * np.log(2)))  # FWHM relation
    return (1 / (np.pi * sigma**2)**0.25) * np.exp(-((t - t0)**2) / (2 * sigma**2))

# Time grid for wavepacket overlap calculation
t_max = 5 * coherence_time
dt = coherence_time / 100
time_grid = np.arange(-t_max, t_max, dt)

# Calculate pair generation rate
pump_photon_rate = pump_power / (hbar * 2 * np.pi * c / pump_wavelength)
pair_generation_rate = spdc_efficiency * pump_photon_rate

# Validation
if pair_generation_rate > 1e7:
    print("WARNING: Unrealistic pair rate")
    pair_generation_rate = 1e5

integration_time = 1.0  # seconds
total_pairs = pair_generation_rate * integration_time

print(f"Pair generation rate: {pair_generation_rate:.2e} pairs/s")
print(f"Integration time: {integration_time:.1f} s")
print(f"Total pairs generated: {total_pairs:.2e}")
print()

# Hong-Ou-Mandel quantum interference calculation
# Two indistinguishable photons at a 50:50 beam splitter
# Quantum state: |1,1⟩ → (|2,0⟩ + |0,2⟩)/√2 (bunching)

def hom_interference(tau, visibility=1.0):
    """
    Calculate HOM interference pattern
    
    tau: time delay between photons
    visibility: interference visibility (0 to 1)
    
    Returns coincidence probability
    """
    # Wavepacket overlap integral
    psi_a = photon_wavepacket(time_grid, t0=0)
    psi_b = photon_wavepacket(time_grid, t0=tau)
    
    # Overlap integral
    overlap = simps(np.conj(psi_a) * psi_b, time_grid)
    overlap_squared = np.abs(overlap)**2
    
    # HOM interference formula
    # P_coincidence = 0.5 * (1 - V * |overlap|^2)
    # At zero delay with perfect visibility: P = 0 (complete destructive interference)
    # At large delay: P = 0.5 (no interference, classical bunching at BS)
    
    P_coincidence = 0.5 * (1 - visibility * overlap_squared)
    
    return P_coincidence

# Experimental imperfections
mode_matching_visibility = 0.95  # Imperfect mode matching
distinguishability = 0.02  # Small residual distinguishability
overall_visibility = mode_matching_visibility * (1 - distinguishability)

print(f"Expected visibility: {overall_visibility:.3f}")
print()

# Calculate HOM dip
coincidence_probabilities = np.array([hom_interference(tau, overall_visibility) 
                                      for tau in time_delays])

# Apply detection efficiencies and realistic count rates
# Singles rates at each detector
singles_rate_per_detector = pair_generation_rate * detector_efficiency

# Diagnostic output
true_coincidence_base_rate = pair_generation_rate * detector_efficiency**2
print(f"True coincidence rate: {true_coincidence_base_rate:.2e} Hz")

# Coincidence counts including accidental coincidences
accidental_rate = singles_rate_per_detector**2 * coincidence_window
print(f"Accidental rate: {accidental_rate:.2e} Hz")
print(f"Ratio (true/accidental): {(true_coincidence_base_rate / accidental_rate):.2e}")
print()

true_coincidence_rate = pair_generation_rate * detector_efficiency**2 * coincidence_probabilities

total_coincidence_rate = true_coincidence_rate + accidental_rate

# Add dark counts
dark_coincidence_rate = 2 * dark_count_rate * singles_rate_per_detector * coincidence_window + dark_count_rate**2 * coincidence_window

total_rate_with_dark = total_coincidence_rate + dark_coincidence_rate

# Convert to counts
coincidence_counts = total_rate_with_dark * integration_time

# Add Poisson noise
coincidence_counts_noisy = np.random.poisson(coincidence_counts)

# Calculate experimental visibility
count_max = np.max(coincidence_counts_noisy)
count_min = np.min(coincidence_counts_noisy)
measured_visibility = (count_max - count_min) / (count_max + count_min)

if measured_visibility < 0.1:
    print("ERROR: Visibility near zero - check accidental coincidences dominating")

# Find FWHM of the dip
half_max = (count_max + count_min) / 2
below_half = coincidence_counts_noisy < half_max
if np.any(below_half):
    indices = np.where(below_half)[0]
    if len(indices) > 1:
        fwhm_indices = [indices[0], indices[-1]]
        fwhm_delays = time_delays[fwhm_indices]
        fwhm_time = np.abs(fwhm_delays[1] - fwhm_delays[0])
        fwhm_length = fwhm_time * c / 2
    else:
        fwhm_time = 0
        fwhm_length = 0
else:
    fwhm_time = 0
    fwhm_length = 0

print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Maximum coincidence counts: {count_max:.1f}")
print(f"Minimum coincidence counts: {count_min:.1f}")
print(f"Measured visibility: {measured_visibility:.3f}")
print(f"Expected visibility: {overall_visibility:.3f}")
print(f"HOM dip FWHM: {fwhm_time*1e15:.2f} fs ({fwhm_length*1e6:.2f} μm)")
print(f"Theoretical coherence time: {coherence_time*1e15:.2f} fs")
print()

# Signal-to-noise analysis
signal_dip = count_max - count_min
noise = np.sqrt(count_max)  # Poisson noise
snr = signal_dip / noise
print(f"Signal-to-noise ratio: {snr:.2f}")
print()

# Verify quantum nature
classical_visibility_limit = 0.5  # Classical limit for distinguishable particles
if measured_visibility > classical_visibility_limit:
    print("✓ Visibility exceeds classical limit (0.5)")
    print("  → Demonstrates quantum interference of indistinguishable photons")
else:
    print("⚠ Visibility below quantum threshold")
    print("  → May indicate distinguishability or poor mode matching")
print()

# Two-photon bunching verification
bunching_factor = count_min / (0.5 * count_max)
print(f"Bunching factor at zero delay: {bunching_factor:.3f}")
print(f"  (Perfect bunching = 0, Classical = 1)")
print()

print("=" * 60)
print("PHYSICAL INTERPRETATION")
print("=" * 60)
print("The HOM dip demonstrates:")
print("1. Quantum interference between two-photon probability amplitudes")
print("2. Bosonic bunching: both photons exit same output port")
print("3. Indistinguishability: photons must have same polarization,")
print("   frequency, spatial mode, and timing")
print("4. The dip width corresponds to photon coherence time")
print()

# Plot results
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(delay_positions*1e6, coincidence_counts, 'b-', linewidth=2, label='Theory')
plt.plot(delay_positions*1e6, coincidence_counts_noisy, 'r.', markersize=4, alpha=0.6, label='With noise')
plt.axhline(y=count_max, color='g', linestyle='--', alpha=0.5, label='Max')
plt.axhline(y=count_min, color='orange', linestyle='--', alpha=0.5, label='Min')
plt.xlabel('Delay Position (μm)', fontsize=12)
plt.ylabel('Coincidence Counts', fontsize=12)
plt.title('Hong-Ou-Mandel Interference Dip', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(time_delays*1e15, coincidence_probabilities, 'b-', linewidth=2)
plt.xlabel('Time Delay (fs)', fontsize=12)
plt.ylabel('Coincidence Probability', fontsize=12)
plt.title('Two-Photon Interference Pattern', fontsize=14, fontweight='bold')
plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='Classical limit')
plt.axhline(y=0, color='g', linestyle='--', alpha=0.5, label='Perfect interference')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('hom_interference.png', dpi=150, bbox_inches='tight')
print("Plot saved as 'hom_interference.png'")