#!/usr/bin/env python3
"""
Demonstrate the code review system catching common mistakes
"""

# Example of WRONG code (what the LLM generated before)
wrong_code = """
# WRONG: Single-phase visibility calculation
import qutip as qt
import numpy as np

cutoff = 8
alpha = 2.0

# Initial state
psi = qt.tensor(qt.coherent(cutoff, alpha), qt.fock(cutoff, 0))
psi = psi.unit()

# Beam splitter
theta_bs = np.pi/4
a = qt.tensor(qt.destroy(cutoff), qt.qeye(cutoff))
b = qt.tensor(qt.qeye(cutoff), qt.destroy(cutoff))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()
psi = U_bs * psi

# Phase shift
phase = np.pi/2
phase_op = qt.tensor((1j * phase * qt.num(cutoff)).expm(), qt.qeye(cutoff))
psi = phase_op * psi

# Second BS
psi = U_bs * psi

# WRONG: Visibility at single phase!
n_a = qt.tensor(qt.num(cutoff), qt.qeye(cutoff))
n_b = qt.tensor(qt.qeye(cutoff), qt.num(cutoff))
I_a = qt.expect(n_a, psi)
I_b = qt.expect(n_b, psi)
visibility = abs(I_a - I_b) / (I_a + I_b)  # MEANINGLESS!

results = {'visibility': visibility}
"""

# Example of CORRECT code
correct_code = """
# CORRECT: Multi-phase visibility calculation
import qutip as qt
import numpy as np

cutoff = 8
alpha = 2.0

# Initial state
psi = qt.tensor(qt.coherent(cutoff, alpha), qt.fock(cutoff, 0))
psi = psi.unit()

# Beam splitter
theta_bs = np.pi/4
a = qt.tensor(qt.destroy(cutoff), qt.qeye(cutoff))
b = qt.tensor(qt.qeye(cutoff), qt.destroy(cutoff))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
psi_after_bs1 = U_bs1 * psi
psi_after_bs1 = psi_after_bs1.unit()

# Measurement operators
n_a = qt.tensor(qt.num(cutoff), qt.qeye(cutoff))
n_b = qt.tensor(qt.qeye(cutoff), qt.num(cutoff))

# Measure at phase = 0
phase_0 = qt.tensor(qt.qeye(cutoff), qt.qeye(cutoff))
psi_0 = phase_0 * psi_after_bs1
U_bs2 = (-1j * H_bs).expm()
psi_final_0 = U_bs2 * psi_0
psi_final_0 = psi_final_0.unit()
I_a_0 = float(abs(qt.expect(n_a, psi_final_0)))

# Measure at phase = π
phase_pi = qt.tensor((1j * np.pi * qt.num(cutoff)).expm(), qt.qeye(cutoff))
psi_pi = phase_pi * psi_after_bs1
psi_final_pi = U_bs2 * psi_pi
psi_final_pi = psi_final_pi.unit()
I_a_pi = float(abs(qt.expect(n_a, psi_final_pi)))

# CORRECT: Compare max and min
visibility = (max(I_a_0, I_a_pi) - min(I_a_0, I_a_pi)) / (max(I_a_0, I_a_pi) + min(I_a_0, I_a_pi))

results = {'visibility': float(visibility)}
"""

print("="*70)
print("CODE REVIEW SYSTEM: What It Should Catch")
print("="*70)

print("\n" + "="*70)
print("EXAMPLE 1: WRONG CODE (single-phase visibility)")
print("="*70)
print(wrong_code)
print("\n❌ REVIEW SHOULD CATCH:")
print("   - Visibility calculated at single phase (φ = π/2)")
print("   - No phase scan or comparison")
print("   - Result will be meaningless (~0 at symmetric phases)")

print("\n" + "="*70)
print("EXAMPLE 2: CORRECT CODE (multi-phase visibility)")
print("="*70)
print(correct_code)
print("\n✅ REVIEW SHOULD APPROVE:")
print("   - Measures at two phases (φ = 0 and φ = π)")
print("   - Compares max and min intensities")
print("   - Properly calculates V = (I_max - I_min)/(I_max + I_min)")

print("\n" + "="*70)
print("REVIEW SYSTEM WORKFLOW")
print("="*70)
print("""
1. 🤖 LLM generates simulation code
   ↓
2. 👨‍🔬 Reviewer LLM checks for physics errors:
   - Beam splitter implementation
   - Visibility calculation method  
   - Energy conservation logic
   - State normalization
   - Component sequence matches design
   ↓
3a. ✅ PASS → Execute code
3b. ❌ FAIL → Regenerate with review feedback → Review again
   ↓
4. ⚙️ Execute and validate physics constraints
   ↓
5. 📊 Return results
""")

print("="*70)
print("KEY BENEFITS")
print("="*70)
print("""
✓ Catches physics errors BEFORE execution
✓ Reduces wasted retries on fundamentally wrong approaches
✓ Provides specific feedback for regeneration
✓ Acts as expert peer reviewer
✓ Ensures simulation faithfully represents designer's setup
""")

print("="*70)
