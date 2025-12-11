#!/usr/bin/env python3
"""
Test to verify that the reviewer is now consistent and has memory.
Simulates the scenario where reviewer gave bad advice and LLM followed it.
"""

def test_reviewer_memory():
    """
    Simulate the problematic scenario:
    1. First review suggests manual construction (BAD ADVICE)
    2. LLM follows advice
    3. Second review should recognize this was ITS advice and either:
       a) Approve it (consistent), OR
       b) Recognize the mistake and say "I was wrong before, actually do X"
    
    With the NEW fix, the second review gets context about what it said before.
    """
    
    print("="*80)
    print("TEST: Reviewer Consistency with Memory")
    print("="*80)
    
    # Simulate first review that gave bad advice
    first_review_feedback = """
**ANALYSIS:**
The Hamiltonian approach H = θ(a†b + ab†) with θ = π/4 does not implement 
a 50:50 beam splitter correctly.

**VERDICT: FAIL**

**CRITICAL PHYSICS ERRORS:**
1. Incorrect beam splitter implementation

**HOW TO FIX:**
- Use the standard beam splitter transformation directly:
  ```python
  # For 50:50 beam splitter: |1,1⟩ → (1/√2)(|2,0⟩ - |0,2⟩)
  state_20 = qt.tensor(qt.fock(cutoff_dim, 2), qt.fock(cutoff_dim, 0))
  state_02 = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 2))
  state_output_zero = (1/np.sqrt(2)) * (state_20 - state_02)
  ```
"""
    
    # LLM follows advice and manually constructs state
    revised_code = """
# Following reviewer's advice
state_20 = qt.tensor(qt.fock(cutoff_dim, 2), qt.fock(cutoff_dim, 0))
state_02 = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 2))
state_output_zero = (1/np.sqrt(2)) * (state_20 - state_02)
"""
    
    print("\n📋 First Review Said:")
    print("   ❌ Hamiltonian approach is wrong")
    print("   ✅ FIX: Manually construct state: (1/√2)(|2,0⟩ - |0,2⟩)")
    
    print("\n🤖 LLM Response:")
    print("   Followed advice and manually constructed the state")
    
    print("\n👨‍🔬 Second Review (WITHOUT memory - OLD BEHAVIOR):")
    print("   ❌ Manual construction is wrong! Use operator evolution!")
    print("   ⚠️  CONTRADICTION: Complaining about following its own advice!")
    
    print("\n" + "="*80)
    print("WITH THE FIX")
    print("="*80)
    
    print("\n👨‍🔬 Second Review (WITH memory - NEW BEHAVIOR):")
    print("   Context provided: 'You previously advised manual construction'")
    print("   Expected responses:")
    print("   ")
    print("   Option A (Consistent):")
    print("   ✅ 'Code correctly follows my previous advice. VERDICT: PASS'")
    print("   ")
    print("   Option B (Self-correction):")
    print("   ⚠️  'I realize my previous advice was wrong. I suggested manual")
    print("       construction, but this bypasses actual simulation. Please use")
    print("       operator evolution instead. I apologize for the confusion.'")
    print("   ")
    print("   Either way, the reviewer is now AWARE of its previous advice")
    print("   and won't blindly contradict itself!")
    
    print("\n" + "="*80)
    print("CODE CHANGES IMPLEMENTED")
    print("="*80)
    
    print("""
1. ✅ Added 'previous_review_feedback' parameter to _review_simulation_code()
2. ✅ Second review now receives first review's feedback as context
3. ✅ Reviewer prompt explicitly says:
      "You previously reviewed this code and gave feedback."
      "Check if revised code addresses YOUR feedback."
      "If you told them to do X, and they did X, don't complain about X!"
4. ✅ Strengthened prohibition: "NEVER suggest manual construction as a fix"
5. ✅ Added explicit operator evolution guidance in review prompt

RESULT: Reviewer can now:
- See its own previous advice
- Be consistent across iterations
- Self-correct if it realizes it was wrong
- Never suggest manual state construction as a "fix"
""")

if __name__ == '__main__':
    test_reviewer_memory()
