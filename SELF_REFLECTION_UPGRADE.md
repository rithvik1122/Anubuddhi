# Self-Reflection and Error Feedback Integration

## Problem Statement

The initial free-form simulation system lacked critical quality control features:

❌ **No error feedback loop** - Execution failures weren't fed back for correction  
❌ **No design alignment check** - Code could generate unrelated simulations  
❌ **No self-reflection** - No critical assessment of simulation quality  
❌ **Single-shot execution** - One attempt, no retry with improvements  

## Solution: Agentic Self-Correction Loop

### Architecture Overview

```
Design Input
    ↓
[1. Classify Physics Domain]
    ↓
[2. Generate Code] ←─────┐
    ↓                     │
[3. Execute Code]         │
    ↓                     │
Success? ──NO→ [Error Feedback]──┘
    ↓ YES                 │
[4. Analyze Results]      │ (max 3 attempts)
    ↓                     │
[4.5 Check Design Alignment]
    ↓                     │
[4.75 Self-Reflect]       │
    ↓                     │
Rating ≥ 5? ──NO→────────┘
    ↓ YES
[5. Save if Rating ≥ 6]
    ↓
Return Results
```

### Key Components

#### 1. **Self-Correction Loop** (`validate_design`)

**Before:**
```python
def validate_design(design):
    code = generate_code(design)
    results = execute(code)
    analysis = analyze(results)
    return results
```

**After:**
```python
def validate_design(design, max_attempts=3):
    for attempt in range(1, max_attempts+1):
        code = generate_code(design, previous_error, attempt)
        results = execute(code)
        
        if execution_failed:
            previous_error = {'type': 'execution_error', 'stderr': ...}
            continue  # Try again
        
        analysis = analyze(results)
        alignment = check_design_alignment(design, code, results)
        reflection = self_reflect(design, code, analysis, alignment)
        
        if reflection['final_rating'] >= 5 or attempt == max_attempts:
            return results
        else:
            previous_error = {'type': 'low_quality', 'feedback': ...}
            continue  # Try again with feedback
    
    return failure_after_all_attempts
```

**Features:**
- Up to 3 correction attempts
- Tracks execution history
- Provides detailed error feedback
- Returns best attempt even if all fail

#### 2. **Error Feedback Integration** (`_generate_simulation_code`)

**New Parameters:**
- `previous_error: Optional[Dict]` - Contains feedback from failed attempt
- `attempt_number: int` - Current iteration (1, 2, or 3)

**Error Types:**

**A. Execution Errors** (syntax, imports, runtime)
```python
error_feedback = """
**PREVIOUS ATTEMPT FAILED - FIX THESE ERRORS:**

Execution error:
```
ModuleNotFoundError: No module named 'qutip'
```

Common fixes:
- Check import statements
- Verify all variables defined
- Fix syntax errors, indentation
- Use try-except for numerical issues
"""
```

**B. Low Quality Errors** (wrong physics, poor results)
```python
error_feedback = """
**PREVIOUS ATTEMPT LOW QUALITY (Rating: 3/10) - IMPROVE:**

Issues identified:
- Used photon counting instead of homodyne detection
- Squeezed states not properly modeled
- Fidelity calculation incorrect

Improvement suggestions:
- Switch to continuous-variable formalism
- Use QuTiP displacement/squeeze operators
- Calculate overlap in phase space
"""
```

#### 3. **Design Alignment Check** (`_check_design_alignment`)

**Purpose:** Verify simulation code actually implements the design

**Critical Questions:**

1. **Components Match**: Does code use all specified components?
   - Beam splitters, detectors, sources present?
   - Parameters (wavelengths, powers) consistent?

2. **Physics Match**: Does code implement intended quantum effect?
   - Correct theoretical framework (Fock/CV/temporal/atomic)?
   - Appropriate quantum mechanical calculations?

3. **Figures of Merit**: Does it calculate what design promised?
   - If design mentions "visibility", is it calculated?
   - If design mentions "fidelity", is it computed?

4. **Parameter Realism**: Are physical parameters sensible?
   - Wavelengths in optical range?
   - Powers/photon numbers realistic?

5. **Design Omissions**: What did design specify that code missed?

**Output Format:**
```json
{
  "alignment_score": 7,
  "components_match": true,
  "physics_match": true,
  "outputs_match": false,
  "missing_from_code": ["Homodyne detector for Bob"],
  "added_by_code": ["Assumed perfect efficiency"],
  "parameter_issues": ["LO power too low"],
  "overall_assessment": "Code implements 70% of design correctly"
}
```

#### 4. **Self-Reflection** (`_self_reflect`)

**Purpose:** Critically assess simulation quality combining all factors

**Inputs:**
- `initial_rating` - From basic analysis (1-10)
- `alignment_score` - From design alignment check (1-10)
- `physics_correctness` - Physics assessment string
- `limitations` - List of identified issues
- `missing_from_code` - Components not implemented

**Rating Adjustment Logic:**
```python
if alignment_score < initial_rating:
    final_rating = min(initial_rating, alignment_score + 1)

if critical_components_missing:
    final_rating -= 2  # Significant penalty

if physics_fundamentally_wrong:
    final_rating = min(final_rating, 3)

if results_unphysical:
    final_rating = min(final_rating, 4)
```

**Output Format:**
```json
{
  "final_rating": 6,
  "confidence_level": "medium",
  "rating_justification": "Physics correct but missing key components",
  "key_strengths": [
    "Correct CV formalism",
    "Realistic squeezing parameters"
  ],
  "critical_weaknesses": [
    "Missing Bob's homodyne detector",
    "No feedforward mechanism"
  ],
  "improvement_suggestions": [
    "Add second homodyne detector",
    "Implement classical feedforward",
    "Calculate teleportation fidelity"
  ],
  "should_retry": false,
  "retry_reason": ""
}
```

### Execution Flow Example

**Experiment:** CV Quantum Teleportation with Squeezed States

**Attempt 1:**
```
🔄 Attempt 1/3
📝 Generating code for continuous_variable...
✅ Code generation succeeded
⚙️  Executing simulation...
❌ Execution failed: ModuleNotFoundError: No module named 'strawberryfields'
```
→ **Error feedback**: "Import error - use QuTiP instead of strawberryfields"

**Attempt 2:**
```
🔄 Attempt 2/3 (addressing execution error)
📝 Generating code with error feedback...
✅ Code generation succeeded
⚙️  Executing simulation...
✅ Execution succeeded
📊 Analyzing results...
   Initial rating: 4/10
🎯 Checking design alignment...
   Alignment score: 3/10
   Missing: Bob's homodyne detector, feedforward
🧠 Self-reflection...
   Final rating: 3/10 (was 4/10)
   Critical weakness: Missing key components
⚠️  Quality rating 3/10 too low, retrying...
```
→ **Quality feedback**: "Add Bob's detector, implement feedforward"

**Attempt 3:**
```
🔄 Attempt 3/3 (addressing low quality)
📝 Generating improved code...
✅ Code generation succeeded
⚙️  Executing simulation...
✅ Execution succeeded
📊 Analyzing results...
   Initial rating: 7/10
🎯 Checking design alignment...
   Alignment score: 8/10
   All major components present
🧠 Self-reflection...
   Final rating: 7/10 (was 7/10)
   Confidence: medium
   Key strengths: Correct CV formalism, all components
   Minor issue: Assumes perfect efficiency
✅ Quality acceptable (7/10 ≥ 5), accepting results
💾 Saved successful simulation (rating ≥ 6)
```

### Benefits

#### 1. **Robustness**
- Handles import errors, syntax errors, runtime failures
- Doesn't give up after first failure
- Learns from mistakes within single run

#### 2. **Quality Assurance**
- Multiple checks: analysis → alignment → reflection
- Critical assessment of own work
- Honest rating adjustment based on all factors

#### 3. **Design Fidelity**
- Explicit check if code matches design
- Identifies missing components
- Prevents generating unrelated simulations

#### 4. **Transparency**
- Tracks all attempts with history
- Shows rating evolution
- Explains why rating changed (reflection justification)

#### 5. **Learning**
- Error patterns fed back for next attempt
- Successful simulations (≥6) saved to toolbox
- Failed attempts inform future generations

### Output Structure

**Success Case:**
```python
{
  'success': True,
  'physics_category': 'continuous_variable',
  'code': '# Python simulation code...',
  'output': 'Teleportation fidelity: 0.87\\n...',
  'execution_success': True,
  'analysis': {
    'rating': 7,
    'verdict': 'GOOD',
    'physics_correctness': '...',
    'alignment_check': {
      'alignment_score': 8,
      'components_match': True,
      'missing_from_code': [],
      ...
    },
    'self_reflection': {
      'final_rating': 7,
      'confidence_level': 'medium',
      'key_strengths': [...],
      'critical_weaknesses': [...],
      'improvement_suggestions': [...]
    }
  },
  'attempts': 3,
  'execution_history': [
    {'attempt': 1, 'success': False, 'stderr': '...'},
    {'attempt': 2, 'success': True, 'rating': 3},
    {'attempt': 3, 'success': True, 'rating': 7}
  ]
}
```

**Failure Case:**
```python
{
  'success': False,
  'error': 'Failed after maximum attempts',
  'physics_category': 'continuous_variable',
  'last_error': {
    'type': 'low_quality',
    'rating': 4,
    'issues': ['Wrong physics formalism', '...'],
    'feedback': ['Switch to phase space', '...']
  },
  'attempts': 3,
  'execution_history': [...]
}
```

### Comparison with QuTiP Agent

| Feature | QuTiP Agent | Free-Form Agent (Old) | Free-Form Agent (New) |
|---------|-------------|----------------------|----------------------|
| Error correction | ❌ None | ❌ None | ✅ Up to 3 attempts |
| Design alignment check | ❌ No | ❌ No | ✅ Yes |
| Self-reflection | ❌ No | ❌ No | ✅ Yes |
| Error feedback | ❌ No | ❌ No | ✅ Yes |
| Physics flexibility | 🟡 Fock only | ✅ All domains | ✅ All domains |
| Quality rating | ✅ 1-10 scale | ✅ 1-10 scale | ✅ Multi-layer (3 checks) |
| Execution history | ❌ No | ❌ No | ✅ Full tracking |
| Improvement suggestions | ✅ Yes | ✅ Yes | ✅ Yes + actionable |

### UI Display Integration

The UI now shows:

**For successful simulations:**
- Physics domain classification
- Final rating with quality label (🟢🟡🟠🔴)
- Verdict string
- Generated code (expandable)
- Execution output
- Detailed analysis:
  - Physics correctness
  - Limitations
  - Recommendations
  - **NEW:** Design alignment check
  - **NEW:** Self-reflection insights
  - **NEW:** Attempt history

**For failed simulations:**
- Error message
- Last error details
- All attempt history
- Execution logs for debugging

### Testing Strategy

#### Test on Failed QuTiP Experiments:

1. **CV Teleportation** (temporal/CV mismatch)
   - Expected: Detects CV physics, generates quadrature code
   - First attempt may use Fock states (wrong)
   - Alignment check catches missing homodyne
   - Self-reflection adjusts rating down
   - Retry with better formalism

2. **Franson Interferometer** (temporal physics)
   - Expected: Detects temporal physics, uses wavepackets
   - First attempt may use Fock states (wrong)
   - Alignment check catches missing timing
   - Retry with Gaussian pulses

3. **EIT System** (atomic physics)
   - Expected: Detects atomic physics, uses Lindblad
   - First attempt may have wrong density formula
   - Execution succeeds but results unphysical
   - Self-reflection catches this, retries with corrections

### Code Changes Summary

**Modified Methods:**

1. **`validate_design()`** - Added retry loop, error tracking
2. **`_generate_simulation_code()`** - Added error feedback parameters
3. **NEW: `_check_design_alignment()`** - Verify code matches design
4. **NEW: `_self_reflect()`** - Critical quality assessment

**Lines of Code:**
- Before: ~470 lines
- After: ~750 lines
- Net addition: ~280 lines (60% increase)

**Function Call Depth:**
```
validate_design()
├── _classify_experiment_physics()
├── LOOP (max 3 attempts):
│   ├── _generate_simulation_code()      [with error feedback]
│   ├── _execute_simulation()
│   ├── _analyze_results()               [existing]
│   ├── _check_design_alignment()        [NEW]
│   ├── _self_reflect()                  [NEW]
│   └── _save_successful_simulation()    [if rating ≥ 6]
└── return best_result
```

### Known Limitations

1. **Max 3 Attempts**: Could still fail on very complex experiments
2. **LLM Dependence**: All checks use LLM (could be expensive/slow)
3. **No Human Feedback**: Can't ask user to clarify design ambiguities
4. **Parameter Sensitivity**: Rating thresholds (5 for accept, 6 for save) arbitrary

### Future Enhancements

1. **Adaptive Attempts**: Use more attempts for complex physics categories
2. **Human-in-Loop**: Ask user questions if design ambiguous
3. **Caching**: Save generated code patterns to reduce LLM calls
4. **Confidence Calibration**: Track if self-reflection ratings correlate with ground truth
5. **Multi-Approach**: Try both QuTiP and free-form, compare results

### Impact on Publication

This self-reflection system strengthens the paper's argument:

**Before:**
- "We built an AI that designs experiments"
- "Simulations sometimes fail due to framework limitations"

**After:**
- "We built an AI that designs, validates, **and self-corrects**"
- "The system recognizes when its simulations are inadequate"
- "Agentic loop includes error feedback and design alignment checks"
- **"Demonstrates metacognition - AI evaluating its own work quality"**

This is a much stronger story for Nature/Science-tier journals:
- Shows true intelligence beyond pattern matching
- Demonstrates self-awareness of limitations
- Implements scientific rigor (multiple checks, honest assessment)
- Could be applied to other domains (chemistry, materials science)

### Conclusion

The upgraded free-form simulation agent now exhibits:

✅ **Error resilience** - Learns from execution failures  
✅ **Design fidelity** - Verifies code matches intent  
✅ **Self-awareness** - Critically assesses own quality  
✅ **Honest evaluation** - Adjusts ratings based on alignment  
✅ **Continuous improvement** - Retries with specific feedback  

This transforms it from a single-shot code generator into a true agentic validation system with quality control and self-reflection capabilities.
