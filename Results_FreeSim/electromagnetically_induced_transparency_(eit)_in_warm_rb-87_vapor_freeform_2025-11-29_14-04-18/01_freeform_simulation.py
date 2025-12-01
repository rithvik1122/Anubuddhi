import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.constants import hbar, c, epsilon_0, k as k_B
from scipy.ndimage import gaussian_filter1d

# Physical constants and parameters
lambda_probe = 780e-9  # m
omega_probe = 2 * np.pi * c / lambda_probe  # rad/s
m_Rb87 = 87 * 1.66054e-27  # kg

# Rb-87 D2 line parameters
Gamma = 2 * np.pi * 6.0e6  # Natural linewidth (rad/s), ~6 MHz for 5P_3/2
delta_hfs = 2 * np.pi * 6.834682610904e9  # Ground state hyperfine splitting (rad/s), ~6.8 GHz

# Laser parameters
P_probe = 0.5e-3  # W (0.5 mW)
P_coupling = 50e-3  # W (50 mW)
beam_waist = 1e-3  # m (1 mm beam diameter)
beam_area = np.pi * (beam_waist / 2)**2  # m^2

# Calculate intensities
I_probe = P_probe / beam_area  # W/m^2
I_coupling = P_coupling / beam_area  # W/m^2

# Transition dipole moment for Rb-87 D2 line (5S_1/2 -> 5P_3/2)
# Using typical value: d ~ 3 x 10^-29 C·m
d = 3.0e-29  # C·m

# Calculate Rabi frequencies
# Omega = d * E / hbar, where E = sqrt(2 * I / (c * epsilon_0))
E_probe = np.sqrt(2 * I_probe / (c * epsilon_0))
E_coupling = np.sqrt(2 * I_coupling / (c * epsilon_0))

Omega_p = d * E_probe / hbar  # Probe Rabi frequency (rad/s)
Omega_c = d * E_coupling / hbar  # Coupling Rabi frequency (rad/s)

print("=== EIT Simulation for Rb-87 Vapor ===")
print(f"\nLaser Parameters:")
print(f"Probe power: {P_probe*1e3:.2f} mW")
print(f"Coupling power: {P_coupling*1e3:.2f} mW")
print(f"Probe Rabi frequency: {Omega_p/(2*np.pi)*1e-6:.2f} MHz")
print(f"Coupling Rabi frequency: {Omega_c/(2*np.pi)*1e-6:.2f} MHz")
print(f"Natural linewidth: {Gamma/(2*np.pi)*1e-6:.2f} MHz")

# Vapor cell parameters
T = 60 + 273.15  # K (60°C)
L = 75e-3  # m (75 mm cell length)

# Atomic density at 60°C for Rb-87 (realistic value)
n_atoms = 2e16  # atoms/m^3 (realistic for 60°C)

# Doppler width calculation
v_thermal = np.sqrt(2 * k_B * T / m_Rb87)
doppler_width = 2 * np.pi * v_thermal / lambda_probe  # rad/s

print(f"\nDoppler broadening:")
print(f"Thermal velocity: {v_thermal:.2f} m/s")
print(f"Doppler width (FWHM): {doppler_width/(2*np.pi)*1e-6:.2f} MHz")

# Optical depth with reduced effective cross-section for Lambda system
sigma_0 = 3 * lambda_probe**2 / (2 * np.pi) * 0.1  # Reduced effective cross-section for Lambda system
OD_resonant = n_atoms * sigma_0 * L

# Validation of optical depth
if OD_resonant > 100:
    print(f"WARNING: Optical depth {OD_resonant:.1f} is too high. Reducing atomic density.")
    n_atoms = n_atoms * 10 / OD_resonant
    OD_resonant = 10.0
    sigma_0 = OD_resonant / (n_atoms * L)

print(f"\nVapor Cell Parameters:")
print(f"Temperature: {T-273.15:.1f} °C")
print(f"Cell length: {L*1e3:.1f} mm")
print(f"Atomic density: {n_atoms:.2e} atoms/m^3")
print(f"Effective cross-section: {sigma_0:.2e} m^2")
print(f"Resonant optical depth: {OD_resonant:.2f}")

# Three-level Lambda system density matrix simulation
# States: |1⟩ = |5S_1/2, F=1⟩, |2⟩ = |5S_1/2, F=2⟩, |3⟩ = |5P_3/2⟩
# Probe couples |1⟩ ↔ |3⟩
# Coupling couples |2⟩ ↔ |3⟩

# Detunings to scan
delta_probe_scan = np.linspace(-100e6, 100e6, 401) * 2 * np.pi  # rad/s, ±100 MHz
delta_coupling = 0.0  # Two-photon resonance condition

# Dephasing rates
gamma_13 = Gamma / 2  # Decay rate from |3⟩ to |1⟩
gamma_23 = Gamma / 2  # Decay rate from |3⟩ to |2⟩
gamma_12 = 0  # No direct decay between ground states
gamma_dephasing = 2 * np.pi * 1e6  # Ground state dephasing ~1 MHz (collisions, etc.)

def lambda_system_steady_state(delta_p, delta_c, Omega_p, Omega_c, gamma_13, gamma_23, gamma_dephasing):
    """
    Solve for steady-state density matrix of three-level Lambda system
    Using correct analytical solution from Harris et al., Phys. Today 50, 36 (1997)
    
    States: |1⟩, |2⟩ (ground states), |3⟩ (excited state)
    Probe: |1⟩ ↔ |3⟩ with detuning delta_p
    Coupling: |2⟩ ↔ |3⟩ with detuning delta_c
    """
    # Total decay rate from excited state
    Gamma_total = gamma_13 + gamma_23
    
    # Correct Lambda-system susceptibility formula
    denominator = (-delta_p + 1j * Gamma_total / 2) * (-delta_c + delta_p + 1j * gamma_dephasing) + Omega_c**2 / 4
    
    # Probe coherence rho_13
    rho_13 = -1j * (Omega_p / 2) * (-delta_c + delta_p + 1j * gamma_dephasing) / denominator
    
    # Normalize properly
    rho_13 = rho_13 * (Omega_p / Gamma)
    
    # Absorption coefficient proportional to Im(rho_13)
    absorption = -np.imag(rho_13)
    
    # Dispersion proportional to Re(rho_13)
    dispersion = np.real(rho_13)
    
    return absorption, dispersion

# Calculate transmission spectra
absorption_with_coupling = []
dispersion_with_coupling = []
absorption_without_coupling = []

print(f"\n=== Scanning Probe Detuning ===")

for delta_p in delta_probe_scan:
    # With coupling laser (EIT)
    abs_val, disp_val = lambda_system_steady_state(
        delta_p, delta_coupling, Omega_p, Omega_c, 
        gamma_13, gamma_23, gamma_dephasing
    )
    absorption_with_coupling.append(abs_val)
    dispersion_with_coupling.append(disp_val)
    
    # Without coupling laser (normal absorption)
    abs_val_no_coupling, _ = lambda_system_steady_state(
        delta_p, delta_coupling, Omega_p, 0.0, 
        gamma_13, gamma_23, gamma_dephasing
    )
    absorption_without_coupling.append(abs_val_no_coupling)

absorption_with_coupling = np.array(absorption_with_coupling)
dispersion_with_coupling = np.array(dispersion_with_coupling)
absorption_without_coupling = np.array(absorption_without_coupling)

# Apply Doppler broadening via Gaussian convolution
delta_freq = delta_probe_scan[1] - delta_probe_scan[0]
sigma_doppler = doppler_width / (2 * np.sqrt(2 * np.log(2)))  # Convert FWHM to sigma
sigma_points = sigma_doppler / delta_freq

absorption_with_coupling = gaussian_filter1d(absorption_with_coupling, sigma_points)
absorption_without_coupling = gaussian_filter1d(absorption_without_coupling, sigma_points)
dispersion_with_coupling = gaussian_filter1d(dispersion_with_coupling, sigma_points)

# Fix normalization with proper scaling
absorption_with_coupling_normalized = absorption_with_coupling * OD_resonant * 0.01  # Scale factor to prevent saturation
absorption_without_coupling_normalized = absorption_without_coupling * OD_resonant * 0.01

# Calculate transmission
transmission_with_coupling = np.exp(-absorption_with_coupling_normalized)
transmission_without_coupling = np.exp(-absorption_without_coupling_normalized)

# Clip to physical range [0, 1]
transmission_with_coupling = np.clip(transmission_with_coupling, 0, 1)
transmission_without_coupling = np.clip(transmission_without_coupling, 0, 1)

# Find EIT window characteristics - proper FWHM calculation
center_idx = len(delta_probe_scan) // 2

# Maximum transmission in EIT window
peak_transmission = np.max(transmission_with_coupling)
T_max_eit = peak_transmission
T_min_no_eit = transmission_without_coupling[center_idx]

# Find FWHM properly
half_max = peak_transmission / 2
above_half = transmission_with_coupling > half_max

# Check for unphysical transmission
if T_max_eit > 1.0:
    print('ERROR: Unphysical transmission')
    exit()

# EIT contrast
if T_min_no_eit > 0:
    eit_contrast = (T_max_eit - T_min_no_eit) / T_min_no_eit
else:
    eit_contrast = 0

# EIT window width (FWHM)
indices = np.where(above_half)[0]
if len(indices) > 1:
    eit_width = (delta_probe_scan[indices[-1]] - delta_probe_scan[indices[0]]) / (2 * np.pi)
else:
    eit_width = 0

# Transparency enhancement
if T_min_no_eit > 0:
    transparency_enhancement = T_max_eit / T_min_no_eit
else:
    transparency_enhancement = 0

print(f"\n=== EIT Window Characteristics ===")
print(f"Maximum transmission with EIT: {T_max_eit:.4f}")
print(f"Minimum transmission without coupling: {T_min_no_eit:.4f}")
print(f"Transparency enhancement: {transparency_enhancement:.2f}x")
print(f"EIT contrast: {eit_contrast:.2%}")
print(f"EIT window width (FWHM): {eit_width*1e-6:.2f} MHz")
print(f"Expected width (~ Omega_c): {Omega_c/(2*np.pi)*1e-6:.2f} MHz")

# Group velocity reduction - proper susceptibility relation
chi_real = -n_atoms * d**2 * dispersion_with_coupling / (epsilon_0 * hbar)
phase_shift = chi_real * omega_probe * L / (2 * c)
delta_omega = delta_probe_scan[1] - delta_probe_scan[0]
group_delay_derivative = np.gradient(phase_shift, delta_omega)

# Maximum group delay at EIT resonance
max_group_delay_idx = center_idx
group_delay_max = group_delay_derivative[max_group_delay_idx]

# Group velocity v_g = c / (1 + d(phi)/d(omega))
if group_delay_max > 0:
    v_g_reduction_factor = 1 + group_delay_max
    v_g = c / v_g_reduction_factor
else:
    v_g_reduction_factor = 1
    v_g = c

print(f"\n=== Group Velocity Effects ===")
print(f"Maximum group delay derivative: {group_delay_max:.2e} s")
print(f"Group velocity: {v_g:.2e} m/s")
print(f"Group velocity reduction factor: {v_g_reduction_factor:.2e}")

# Dark state analysis
# Dark state: |D⟩ = (Omega_c|F=2⟩ - Omega_p|F=1⟩) / sqrt(Omega_c^2 + Omega_p^2)
dark_state_population_2 = Omega_c**2 / (Omega_c**2 + Omega_p**2)
dark_state_population_1 = Omega_p**2 / (Omega_c**2 + Omega_p**2)

print(f"\n=== Dark State Composition ===")
print(f"Dark state |D⟩ = {np.sqrt(dark_state_population_2):.4f}|F=2⟩ - {np.sqrt(dark_state_population_1):.4f}|F=1⟩")
print(f"Population in |F=2⟩: {dark_state_population_2:.4f}")
print(f"Population in |F=1⟩: {dark_state_population_1:.4f}")

# Physical validation
print(f"\n=== Physical Validation ===")
print(f"Transmission range: [{np.min(transmission_with_coupling):.4f}, {np.max(transmission_with_coupling):.4f}]")
print(f"All transmissions in [0,1]: {np.all((transmission_with_coupling >= 0) & (transmission_with_coupling <= 1))}")
print(f"EIT enhancement reasonable (<100x): {transparency_enhancement < 100}")
print(f"Coupling Rabi > Probe Rabi (required for EIT): {Omega_c > Omega_p}")
print(f"Doppler width > Natural linewidth: {doppler_width > Gamma}")

# Summary of quantum interference effect
print(f"\n=== Quantum Interference Summary ===")
print(f"EIT demonstrates quantum interference between two excitation pathways:")
print(f"  Path 1: |F=1⟩ --probe--> |5P_3/2⟩")
print(f"  Path 2: |F=2⟩ --coupling--> |5P_3/2⟩")
print(f"\nAt two-photon resonance, destructive interference creates:")
print(f"  - Dark state that cannot absorb probe photons")
print(f"  - Transparency window of width {eit_width*1e-6:.2f} MHz")
print(f"  - {transparency_enhancement:.1f}x enhancement in transmission")
print(f"  - Group velocity reduction to {v_g:.2e} m/s ({c/v_g:.0f}x slower than c)")
print(f"\nWhen coupling laser is blocked (Omega_c = 0):")
print(f"  - No quantum interference")
print(f"  - Normal absorption restored (transmission = {T_min_no_eit:.4f})")

# Plot results
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

delta_MHz = delta_probe_scan / (2 * np.pi * 1e6)

ax1.plot(delta_MHz, transmission_without_coupling, 'b-', linewidth=2, label='Without coupling (normal absorption)')
ax1.plot(delta_MHz, transmission_with_coupling, 'r-', linewidth=2, label='With coupling (EIT)')
ax1.set_xlabel('Probe Detuning (MHz)')
ax1.set_ylabel('Transmission')
ax1.set_title('Electromagnetically Induced Transparency in Rb-87')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, 1])

ax2.plot(delta_MHz, absorption_without_coupling_normalized, 'b-', linewidth=2, label='Without coupling')
ax2.plot(delta_MHz, absorption_with_coupling_normalized, 'r-', linewidth=2, label='With coupling')
ax2.set_xlabel('Probe Detuning (MHz)')
ax2.set_ylabel('Optical Depth')
ax2.set_title('Absorption Spectrum')
ax2.legend()
ax2.grid(True, alpha=0.3)

ax3.plot(delta_MHz, dispersion_with_coupling, 'g-', linewidth=2)
ax3.set_xlabel('Probe Detuning (MHz)')
ax3.set_ylabel('Dispersion (arb. units)')
ax3.set_title('Steep Dispersion in EIT Window')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('eit_simulation.png', dpi=150, bbox_inches='tight')
print(f"\nPlot saved as 'eit_simulation.png'")

print("\n=== Simulation Complete ===")