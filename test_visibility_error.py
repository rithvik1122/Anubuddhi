#!/usr/bin/env python3
"""
Demonstrate why single-phase visibility calculation is WRONG
"""

print("="*70)
print("VISIBILITY CALCULATION: CORRECT vs WRONG")
print("="*70)

# Simulated Mach-Zehnder outputs at different phases
import numpy as np

# At phase φ = 0 (constructive interference at output A)
I_A_at_0 = 4.0  # All light goes to detector A
I_B_at_0 = 0.0

# At phase φ = π/2 (intermediate)
I_A_at_pi2 = 2.0  # Equal splitting
I_B_at_pi2 = 2.0

# At phase φ = π (destructive interference at output A)
I_A_at_pi = 0.0  # All light goes to detector B
I_B_at_pi = 4.0

print("\nMeasured intensities:")
print(f"  φ = 0:   I_A = {I_A_at_0:.1f}, I_B = {I_B_at_0:.1f}")
print(f"  φ = π/2: I_A = {I_A_at_pi2:.1f}, I_B = {I_B_at_pi2:.1f}")
print(f"  φ = π:   I_A = {I_A_at_pi:.1f}, I_B = {I_B_at_pi:.1f}")

print("\n" + "="*70)
print("❌ WRONG METHOD (what the LLM did):")
print("="*70)
print("Calculate at single phase φ = π/2:")
V_wrong = abs(I_A_at_pi2 - I_B_at_pi2) / (I_A_at_pi2 + I_B_at_pi2)
print(f"  V = |I_A - I_B| / (I_A + I_B)")
print(f"  V = |{I_A_at_pi2:.1f} - {I_B_at_pi2:.1f}| / ({I_A_at_pi2:.1f} + {I_B_at_pi2:.1f})")
print(f"  V = {V_wrong:.3f}")
print(f"\n❌ This gives V = 0.0 even though there IS perfect interference!")

print("\n" + "="*70)
print("✅ CORRECT METHOD:")
print("="*70)
print("Compare maximum and minimum across phases:")
I_max = max(I_A_at_0, I_A_at_pi2, I_A_at_pi)
I_min = min(I_A_at_0, I_A_at_pi2, I_A_at_pi)
V_correct = (I_max - I_min) / (I_max + I_min)
print(f"  I_max = {I_max:.1f} (at φ = 0)")
print(f"  I_min = {I_min:.1f} (at φ = π)")
print(f"  V = (I_max - I_min) / (I_max + I_min)")
print(f"  V = ({I_max:.1f} - {I_min:.1f}) / ({I_max:.1f} + {I_min:.1f})")
print(f"  V = {V_correct:.3f}")
print(f"\n✅ This correctly shows V = 1.0 for perfect interference!")

print("\n" + "="*70)
print("LESSON:")
print("="*70)
print("Visibility measures the DEPTH of interference fringes.")
print("You MUST scan phase and compare max vs min intensities.")
print("A single-phase measurement tells you nothing about visibility!")
print("="*70)
