# REASONING: Fixed Franson interferometer to include BS1 input beam splitters and correct operator sequence.
# The original code manually constructed the time-bin entangled state, skipping BS1 entirely.
# Corrected approach: Start with photons at interferometer inputs → Apply BS1 → Apply phase shifts → Apply BS2 → Detect
# Using 6 modes: signal_in, signal_short, signal_long, idler_in, idler_short, idler_long

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = 2  # Single photon per mode is sufficient
wavelength_pump = 405  # nm
wavelength_signal = 810  # nm
wavelength_idler = 810  # nm

# Step 1: Initialize state with photons at interferometer input ports
# 6 modes: [signal_in, signal_short, signal_long, idler_in, idler_short, idler_long]
# Initial state from SPDC: |1_signal_in, 0, 0, 1_idler_in, 0, 0⟩
vac = qt.fock(cutoff_dim, 0)
one = qt.fock(cutoff_dim, 1)

psi_initial = qt.tensor(one, vac, vac, one, vac, vac)

# Step 2: Construct BS1 operators (input beam splitters)
# BS1 Signal: couples signal_in (mode 0) to signal_short (mode 1) and signal_long (mode 2)
# BS1 Idler: couples idler_in (mode 3) to idler_short (mode 4) and idler_long (mode 5)

theta_bs = np.pi/4  # 50:50 beam splitter

# For BS1 Signal: need to split input into short and long arms
# Use simplified model: input port → short arm coupling
a_sig_in = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), 
                     qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_sig_short = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim),
                        qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_sig_long = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.destroy(cutoff_dim),
                       qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))

# BS1 Signal Hamiltonian: creates superposition of short and long paths
H_bs1_signal = theta_bs * (a_sig_short.dag() * a_sig_in + a_sig_short * a_sig_in.dag() +
                           a_sig_long.dag() * a_sig_in + a_sig_long * a_sig_in.dag())
U_bs1_signal = (-1j * H_bs1_signal).expm()

# For BS1 Idler
a_idl_in = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                     qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a_idl_short = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                        qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
a_idl_long = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                       qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

H_bs1_idler = theta_bs * (a_idl_short.dag() * a_idl_in + a_idl_short * a_idl_in.dag() +
                          a_idl_long.dag() * a_idl_in + a_idl_long * a_idl_in.dag())
U_bs1_idler = (-1j * H_bs1_idler).expm()

# Apply BS1 to create path superpositions
psi_after_bs1 = U_bs1_idler * U_bs1_signal * psi_initial
psi_after_bs1 = psi_after_bs1.unit()

# Step 3: Construct BS2 operators (output beam splitters)
# BS2 Signal: interferes signal_short (mode 1) and signal_long (mode 2)
# BS2 Idler: interferes idler_short (mode 4) and idler_long (mode 5)

H_bs2_signal = theta_bs * (a_sig_short.dag() * a_sig_long + a_sig_short * a_sig_long.dag())
U_bs2_signal = (-1j * H_bs2_signal).expm()

H_bs2_idler = theta_bs * (a_idl_short.dag() * a_idl_long + a_idl_short * a_idl_long.dag())
U_bs2_idler = (-1j * H_bs2_idler).expm()

# Step 4: Scan phase differences and measure coincidences
phi_signal_values = np.linspace(0, 2*np.pi, 20)
phi_idler = 0  # Fix idler phase

coincidence_counts = []

for phi_signal in phi_signal_values:
    # Apply phase shifts to long arms (modes 2 and 5)
    phase_signal = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                            (1j * phi_signal * qt.num(cutoff_dim)).expm(),
                            qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
    
    phase_idler = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                           qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                           (1j * phi_idler * qt.num(cutoff_dim)).expm())
    
    # Correct sequence: BS1 → phase shifts → BS2
    psi = phase_idler * phase_signal * psi_after_bs1
    psi = psi.unit()
    
    psi = U_bs2_idler * U_bs2_signal * psi
    psi = psi.unit()
    
    # Measure coincidences at output ports (short arms: modes 1 and 4)
    n_sig_short = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim), qt.qeye(cutoff_dim),
                            qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
    n_idl_short = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                            qt.qeye(cutoff_dim), qt.num(cutoff_dim), qt.qeye(cutoff_dim))
    
    coincidence_op = n_sig_short * n_idl_short
    coincidence = float(abs(qt.expect(coincidence_op, psi)))
    coincidence_counts.append(coincidence)

coincidence_counts = np.array(coincidence_counts)

# Step 5: Calculate Franson interference visibility
I_max = float(np.max(coincidence_counts))
I_min = float(np.min(coincidence_counts))
visibility_franson = float((I_max - I_min) / (I_max + I_min + 1e-12))

# Step 6: Verify entanglement of state after BS1
rho_full = psi_after_bs1 * psi_after_bs1.dag()
dims = [[cutoff_dim]*6, [cutoff_dim]*6]
rho_full.dims = dims

# Trace out idler modes (3,4,5) to get signal reduced state (modes 0,1,2)
rho_signal = rho_full.ptrace([0, 1, 2])
purity_signal = float(abs((rho_signal * rho_signal).tr()))

# Von Neumann entropy
entropy_signal = float(abs(qt.entropy_vn(rho_signal, base=2)))

# Step 7: Check photon number conservation
n_total = sum([qt.tensor(*[qt.num(cutoff_dim) if i == j else qt.qeye(cutoff_dim) 
                           for j in range(6)]) for i in range(6)])
total_photons = float(abs(qt.expect(n_total, psi_after_bs1)))

# Step 8: Calculate fidelity to maximally entangled state
# After BS1, expect superposition of (both short) and (both long)
ideal_state = (qt.tensor(vac, one, vac, vac, one, vac) + 
               qt.tensor(vac, vac, one, vac, vac, one)).unit()
fidelity_to_ideal = float(abs(qt.fidelity(psi_after_bs1, ideal_state)))

# Step 9: Optimal phase correlation
phi_optimal = np.pi/2
phase_signal_opt = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                            (1j * phi_optimal * qt.num(cutoff_dim)).expm(),
                            qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
phase_idler_opt = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                           qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                           (1j * phi_optimal * qt.num(cutoff_dim)).expm())

psi_opt = phase_idler_opt * phase_signal_opt * psi_after_bs1
psi_opt = U_bs2_idler * U_bs2_signal * psi_opt
psi_opt = psi_opt.unit()

n_sig_short = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim), qt.qeye(cutoff_dim),
                        qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
n_idl_short = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim),
                        qt.qeye(cutoff_dim), qt.num(cutoff_dim), qt.qeye(cutoff_dim))
coincidence_op = n_sig_short * n_idl_short
coincidence_optimal = float(abs(qt.expect(coincidence_op, psi_opt)))

results = {
    'visibility_franson': visibility_franson,
    'coincidence_max': I_max,
    'coincidence_min': I_min,
    'purity_reduced_state': purity_signal,
    'entanglement_entropy': entropy_signal,
    'total_photon_number': total_photons,
    'fidelity_to_ideal_timebin': fidelity_to_ideal,
    'coincidence_at_optimal_phase': coincidence_optimal,
    'mean_coincidence_rate': float(np.mean(coincidence_counts)),
    'std_coincidence_rate': float(np.std(coincidence_counts))
}