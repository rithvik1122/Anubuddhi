# Feedback Loop Analysis and Fixes

## Executive Summary

**Investigation Date:** November 19, 2025  
**Issue:** User suspected feedback loops weren't incorporating refinement feedback  
**Finding:** ✅ **Feedback loops ARE mechanically working**, but **feedback quality was poor**  

## Critical Discovery 🔥

**The simulation code reviewer was contradicting itself:**

1. **First Review:** "Don't use Hamiltonian H=θ(a†b+ab†), instead manually construct: `state = (1/√2)(|2,0⟩ - |0,2⟩)`"
2. **LLM follows advice** → implements manual state construction
3. **Second Review:** "Manual state construction is wrong! Must use operator evolution!"

**Root Cause:** Reviewer had no memory of its previous advice, leading to contradictory feedback that made the code worse, not better.

---

## Detailed Analysis

### Designer Refinement Loop

**Status:** ✅ **Mechanically Working**

**Evidence from logs:**
```
🔄 Refinement Cycle 3/3
🔧 Refining design based on feedback...
⚠️  Validation issues found:
    • Beam Path Logic Error: photons reaching same narrowband filters at [6.5, 3.0]
    • Spatial Layout Problems: Filter A and B at identical coordinates
    • Missing Path Length Matching
```

**Code Flow:**
1. `llm_designer.py:336` - Calls `_build_refinement_prompt(query, response, validation_feedback)`
2. `llm_designer.py:894` - Constructs prompt with:
   - Original request
   - Previous design
   - **Reviewer feedback** ← THIS IS INCLUDED
3. Prompt sent to LLM for refinement

**Conclusion:** Feedback IS reaching the refinement prompt. If the designer isn't fixing issues, it's because:
- LLM doesn't understand the spatial constraints
- Validation feedback needs to be more specific/prescriptive
- LLM capability limitations

**Recommendation:** Make validation feedback more concrete with examples (e.g., "Move Filter A to [6.0, 2.5], Filter B to [6.0, 3.5]")

---

### Simulation Code Review Loop

**Status:** ⚠️ **Mechanically Working, Quality FAILED**

**The Contradiction (from actual logs):**

**First Review:**
```
**HOW TO FIX:**
- Replace beam splitter implementation: Use the standard beam splitter 
  transformation directly:
  
  state_20 = qt.tensor(qt.fock(cutoff_dim, 2), qt.fock(cutoff_dim, 0))
  state_02 = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 2))
  state_output_zero = (1/np.sqrt(2)) * (state_20 - state_02)
```

**Second Review (after LLM followed advice):**
```
**CRITICAL PHYSICS ERRORS:**
2. **Beam Splitter Transformation**: This is the most critical error. 
   The code manually constructs output states instead of applying the 
   proper beam splitter operator.
   
**HOW TO FIX:**
- Replace the manual state construction with proper beam splitter operator
```

**Analysis:**
- First review **suggested manual construction as the fix**
- LLM **correctly followed the advice**
- Second review **complained about manual construction**
- Result: LLM confused, code oscillates between approaches

**Root Cause:**
1. Reviewer has no memory of previous advice
2. Reviewer prompt doesn't explicitly forbid suggesting manual construction
3. No consistency check between review iterations

---

## Fixes Implemented

### Fix 1: Reviewer Memory

**File:** `simulation_agent.py:170-180`

**Before:**
```python
review_passed_2, review_feedback_2 = self._review_simulation_code(design, sim_code)
```

**After:**
```python
review_passed_2, review_feedback_2 = self._review_simulation_code(
    design, sim_code, previous_review_feedback=review_feedback
)
```

**Effect:** Second review now sees first review's feedback and can check for consistency.

---

### Fix 2: Context Section in Reviewer Prompt

**File:** `simulation_agent.py:580-595`

**Added:**
```python
if previous_review_feedback:
    context_section = """
⚠️ IMPORTANT CONTEXT - This is a SECOND review:
You previously reviewed this experiment's code and provided feedback.
The researcher has now revised the code based on your advice.

**YOUR PREVIOUS FEEDBACK:**
{previous_review_feedback}

**CRITICAL**: Check if the revised code correctly addresses your feedback.
- Did they fix what you asked them to fix?
- Did they introduce new errors while fixing the old ones?
- Are you being consistent with your previous advice?
- If you told them to do X, and they did X, don't now complain about X!
```

**Effect:** Reviewer explicitly reminded to be consistent with previous advice.

---

### Fix 3: Strengthen Anti-Manual-Construction Guidance

**File:** `simulation_agent.py:640-650`

**Enhanced:**
```python
**CRITICAL: Manually constructing "expected" output states instead of evolving**
  * If you see states like `(1/√2)(|2,0⟩ - |0,2⟩)` written directly
  * This is NOT simulation - it's just encoding the textbook answer!
  * Must use actual beam splitter Hamiltonian: `H = θ(a†b + ab†)` 
    then `U = (-1j*H).expm()`
  * Then evolve: `state_out = U * state_in * U.dag()` (for density matrices)
  * Or: `state_out = U * state_in` (for kets)
  * ⚠️ **NEVER suggest manual construction as a "fix" - always require 
       operator evolution!**
```

**Effect:** Explicit prohibition prevents reviewer from suggesting manual construction.

---

### Fix 4: Updated FAIL Response Format

**File:** `simulation_agent.py:720-730`

**Added:**
```python
⚠️ **IMPORTANT**: When suggesting fixes:
- ALWAYS require operator-based evolution (Hamiltonians, unitaries)
- NEVER suggest manually writing output states like `(|2,0⟩ ± |0,2⟩)/√2`
- If code uses wrong operator, say "use correct operator" not "write state directly"
```

**Effect:** Reviewer constrained to only suggest physics-correct fixes.

---

## Testing

**Test File:** `test_reviewer_consistency.py`

Demonstrates the scenario:
1. First review gives bad advice (manual construction)
2. LLM follows advice
3. OLD: Second review contradicts itself
4. NEW: Second review sees previous advice and is consistent

---

## Expected Behavior After Fix

### Scenario 1: Consistent Reviewer
```
First Review: "Use operator evolution with Hamiltonian H = θ(a†b + ab†)"
LLM: Implements operator evolution
Second Review: "✅ Code correctly implements operator evolution. PASS"
```

### Scenario 2: Self-Correcting Reviewer (if realizes mistake)
```
First Review: "The Hamiltonian angle is wrong, try θ = π/3"
LLM: Uses θ = π/3
Second Review: "I see you used θ = π/3 as I suggested. However, I realize
                my previous advice was incorrect. For a 50:50 beam splitter,
                θ should be π/4. I apologize for the confusion."
```

### Scenario 3: Catching Real Errors
```
First Review: "Use proper beam splitter operator"
LLM: Still manually constructs state (ignored advice)
Second Review: "You were asked to use operator evolution but still manually
                construct states. This is incorrect."
```

---

## Remaining Issues

### Designer Refinement (Lower Priority)

**Issue:** Designer may still ignore spatial layout constraints in cycle 3

**Potential Solutions:**
1. Make validation feedback more prescriptive:
   - Instead of: "Filters at same position is impossible"
   - Use: "Move Filter A to [6.0, 2.5] with angle 0°, Filter B to [6.0, 3.5] with angle 0°"

2. Add examples to validation feedback:
   ```json
   "Here's a valid layout:
   {
     'Narrowband Filter A': {'x': 6.0, 'y': 2.5, 'angle': 0},
     'Narrowband Filter B': {'x': 6.0, 'y': 3.5, 'angle': 0}
   }"
   ```

3. Increase max_refinement_cycles from 3 to 5 for complex designs

---

## Verification Status

- ✅ Code compiles without errors
- ✅ Review method signature updated
- ✅ Previous feedback correctly passed to second review
- ✅ Context section added to prompt
- ✅ Anti-manual-construction guidance strengthened
- ✅ Test demonstrates expected behavior
- ⏳ **Needs live testing**: Run actual simulation to verify behavior

---

## Files Modified

1. `simulation_agent.py` (5 changes):
   - Line 170-180: Pass previous_review_feedback to second review
   - Line 560-575: Update method signature
   - Line 580-595: Add context section for second reviews
   - Line 640-650: Strengthen anti-manual-construction guidance
   - Line 720-730: Update FAIL response format

2. `test_feedback_loops.py` (NEW):
   - Analysis script demonstrating the contradiction

3. `test_reviewer_consistency.py` (NEW):
   - Test demonstrating fix behavior

---

## Conclusion

**The fundamental architecture of feedback loops was correct.** The issue was:

1. **Reviewer quality:** Giving contradictory advice across iterations
2. **No memory:** Second review couldn't see first review's advice
3. **Weak constraints:** Didn't explicitly forbid bad practices (manual construction)

**All three issues are now fixed.** The reviewer will:
- See its previous advice (memory)
- Check for consistency with previous feedback
- Never suggest manual state construction
- Either approve correctly-implemented fixes OR self-correct if it was wrong

**Next Step:** Run actual simulation with HOM experiment to verify the reviewer now provides consistent, physics-correct feedback.
