#!/usr/bin/env python3
"""
Test that the improved prompt prevents common Mach-Zehnder simulation errors
"""

import qutip as qt
import numpy as np

print("="*70)
print("TESTING CORRECT MACH-ZEHNDER IMPLEMENTATION")
print("="*70)

# ========== SINGLE PHOTON MACH-ZEHNDER ==========
print("\n1. Single Photon Mach-Zehnder (Should show perfect interference)")
print("-"*70)

cutoff = 3
# Initial: single photon in mode 0, vacuum in mode 1
psi = qt.tensor(qt.fock(cutoff, 1), qt.fock(cutoff, 0))
psi = psi.unit()
print(f"✓ Initial state: |1,0⟩ (one photon in first mode)")
print(f"  Photon number: {qt.expect(qt.tensor(qt.num(cutoff), qt.qeye(cutoff)), psi):.6f}")

# First 50:50 beam splitter
theta_bs = np.pi/4  # Correct angle for 50:50
a = qt.tensor(qt.destroy(cutoff), qt.qeye(cutoff))
b = qt.tensor(qt.qeye(cutoff), qt.destroy(cutoff))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
psi = U_bs1 * psi
psi = psi.unit()
print(f"\n✓ After first BS:")
n_a = qt.tensor(qt.num(cutoff), qt.qeye(cutoff))
n_b = qt.tensor(qt.qeye(cutoff), qt.num(cutoff))
print(f"  Mode A photons: {qt.expect(n_a, psi):.6f}")
print(f"  Mode B photons: {qt.expect(n_b, psi):.6f}")
print(f"  Total photons: {qt.expect(n_a + n_b, psi):.6f} (should be 1.0)")

# Test at two phases: 0 and π
results = {}
for label, phi in [("constructive (φ=0)", 0), ("destructive (φ=π)", np.pi)]:
    # Apply phase to mode A
    phase_op = qt.tensor((1j * phi * qt.num(cutoff)).expm(), qt.qeye(cutoff))
    psi_phase = phase_op * psi
    psi_phase = psi_phase.unit()
    
    # Second 50:50 BS
    U_bs2 = (-1j * H_bs).expm()
    psi_final = U_bs2 * psi_phase
    psi_final = psi_final.unit()
    
    # Measure outputs
    out_a = float(qt.expect(n_a, psi_final).real)
    out_b = float(qt.expect(n_b, psi_final).real)
    total = out_a + out_b
    
    print(f"\n✓ {label}:")
    print(f"  Output A: {out_a:.6f} photons")
    print(f"  Output B: {out_b:.6f} photons")
    print(f"  Total: {total:.6f} (energy conserved: {abs(total-1.0) < 0.01})")
    
    results[label] = {'out_a': out_a, 'out_b': out_b, 'total': total}

# Calculate visibility
I_max = max(results['constructive (φ=0)']['out_a'], results['destructive (φ=π)']['out_a'])
I_min = min(results['constructive (φ=0)']['out_a'], results['destructive (φ=π)']['out_a'])
visibility = (I_max - I_min) / (I_max + I_min + 1e-12)

print(f"\n{'='*70}")
print(f"VISIBILITY: {visibility:.3f}")
if visibility > 0.95:
    print(f"✅ EXCELLENT! Near-perfect interference visibility")
else:
    print(f"❌ PROBLEM! Visibility should be ~1.0 for single photon")
print(f"{'='*70}")

# ========== COHERENT STATE MACH-ZEHNDER ==========
print("\n\n2. Coherent State Mach-Zehnder (Classical-like)")
print("-"*70)

cutoff = 10
alpha = 2.0  # Coherent state amplitude
# Initial: coherent state in mode 0, vacuum in mode 1
psi_coh = qt.tensor(qt.coherent(cutoff, alpha), qt.coherent(cutoff, 0))
psi_coh = psi_coh.unit()
print(f"✓ Initial state: |α,0⟩ with α={alpha}")
print(f"  Photon number: {qt.expect(qt.tensor(qt.num(cutoff), qt.qeye(cutoff)), psi_coh):.6f}")

# First BS
theta_bs = np.pi/4
a = qt.tensor(qt.destroy(cutoff), qt.qeye(cutoff))
b = qt.tensor(qt.qeye(cutoff), qt.destroy(cutoff))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
psi_coh = U_bs1 * psi_coh
psi_coh = psi_coh.unit()

n_a = qt.tensor(qt.num(cutoff), qt.qeye(cutoff))
n_b = qt.tensor(qt.qeye(cutoff), qt.num(cutoff))
print(f"\n✓ After first BS:")
print(f"  Mode A photons: {qt.expect(n_a, psi_coh):.6f}")
print(f"  Mode B photons: {qt.expect(n_b, psi_coh):.6f}")
print(f"  Total: {qt.expect(n_a + n_b, psi_coh):.6f}")

# Test visibility with phase scan
phase_values = np.linspace(0, 2*np.pi, 20)
intensities_a = []
intensities_b = []

for phi in phase_values:
    phase_op = qt.tensor((1j * phi * qt.num(cutoff)).expm(), qt.qeye(cutoff))
    psi_p = phase_op * psi_coh
    psi_p = psi_p.unit()
    
    U_bs2 = (-1j * H_bs).expm()
    psi_f = U_bs2 * psi_p
    psi_f = psi_f.unit()
    
    intensities_a.append(float(qt.expect(n_a, psi_f).real))
    intensities_b.append(float(qt.expect(n_b, psi_f).real))

I_max_coh = max(intensities_a)
I_min_coh = min(intensities_a)
visibility_coh = (I_max_coh - I_min_coh) / (I_max_coh + I_min_coh + 1e-12)

print(f"\n✓ Phase scan results:")
print(f"  Max intensity: {I_max_coh:.6f}")
print(f"  Min intensity: {I_min_coh:.6f}")
print(f"  Visibility: {visibility_coh:.3f}")

# Check energy conservation across all phases
energy_conserved = True
for i, phi in enumerate(phase_values):
    total_out = intensities_a[i] + intensities_b[i]
    if abs(total_out - alpha**2) > 0.1:  # Allow small numerical error
        energy_conserved = False
        print(f"⚠️  Energy not conserved at φ={phi:.2f}: {total_out:.3f} vs {alpha**2:.3f}")

if energy_conserved:
    print(f"✅ Energy conserved across all phases!")

print(f"\n{'='*70}")
print(f"SUMMARY:")
print(f"  Single photon visibility: {visibility:.3f} (should be ~1.0)")
print(f"  Coherent state visibility: {visibility_coh:.3f} (should be 0.5-1.0)")
if visibility > 0.95 and visibility_coh > 0.4 and energy_conserved:
    print(f"✅ ALL TESTS PASSED - Physics is correct!")
else:
    print(f"❌ SOME TESTS FAILED - Check implementation")
print(f"{'='*70}")
