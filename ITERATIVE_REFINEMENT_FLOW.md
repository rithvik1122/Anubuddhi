# Iterative Refinement System - Complete Flow

## Overview

The system now implements a comprehensive human-in-the-loop learning workflow with:
1. **Retrieval-First Design** - Check memory before generating
2. **Multi-Cycle Code Generation** - Review → Execute → Fix → Retry (up to 3 cycles)
3. **Human Approval Gate** - Only validated experiments enter knowledge base
4. **Deduplication** - Avoid storing redundant similar experiments

---

## 1. Design Generation Flow

### A. Retrieval-First Workflow

```
User Query → Memory Search
              ↓
         Found Similar? (similarity > 0.85)
         ↓YES              ↓NO
    Return Existing    Generate New
         ↓
    Show in UI with metadata:
    - Similarity score
    - Original query
    - Human approved?
    - Past verdict & confidence
         ↓
    User Choice:
    ├─ Accept → Use retrieved design
    └─ "Generate New" → Force generation (skip retrieval)
```

**Code Location**: `llm_designer.py` lines 290-340

**Key Logic**:
```python
# Check memory for existing experiments
similar_experiments = memory.retrieve_similar_experiments(query, n_results=1)
if similarity > 0.85:
    # Return existing design with metadata
    return convert_stored_to_optical_setup(stored_data)
else:
    # Proceed with generation using memory as context
    enhanced_query = memory.augment_prompt_with_memory(query)
```

### B. Generation with Memory Context

If no high-similarity match found, system enhances prompt with:
- Top 3 similar past experiments (context)
- Top 3 relevant building blocks (patterns)
- Past successes and failures

```
Query Enhancement:
├─ Original: "design hong ou mandel setup"
└─ Enhanced: [original] + 
             [3 similar HOM experiments] +
             [beam splitter patterns] +
             [detector configurations]
```

**Code Location**: `memory_system.py` `augment_prompt_with_memory()`

---

## 2. Simulation Validation Flow

### Multi-Cycle Refinement Process

```
Generated Design → Simulation Cycle (max 3 iterations)
                        ↓
                   ┌──────────────┐
                   │ Cycle Start  │
                   └──────┬───────┘
                          ↓
                   ┌──────────────────┐
                   │ 1. Code Review   │ ← LLM reviews physics
                   │    (Pre-exec)    │   before execution
                   └──────┬───────────┘
                          ↓
                   Review Pass?
                   ↓NO        ↓YES
             Revise Code   Execute
                   ↓          ↓
                   └──────────┤
                              ↓
                   ┌──────────────────┐
                   │ 2. Execution     │
                   │    (Safe sandbox)│
                   └──────┬───────────┘
                          ↓
                   Success?
                   ↓NO        ↓YES
                   │          ↓
                   │   ┌─────────────────┐
                   │   │ 3. Physics Check│
                   │   │    (Validate)   │
                   │   └──────┬──────────┘
                   │          ↓
                   │   All metrics valid?
                   │   (no NaN, negative, >1)
                   │   ↓NO        ↓YES
                   └───┴──────────┘
                       ↓          ↓
                  Retry with  Success!
                  error msg   ↓
                       ↓      Return results
                  Next cycle
                  (max 3)
```

**Code Location**: `simulation_agent.py` `_validate_with_code_generation()` lines 145-250

### Key Validation Steps

#### Step 1: Pre-Execution Code Review
```python
review_passed, feedback = _review_simulation_code(design, sim_code)
if not review_passed:
    # Regenerate with review feedback
    sim_code_revised = _generate_simulation_code_with_error(
        design, sim_code, f"Code review: {feedback}"
    )
```

**Checks**:
- Correct quantum operations for experiment type
- Proper state normalization
- Appropriate metric calculations
- Physics consistency (unitarity, conservation)

#### Step 2: Execution with Error Capture
```python
exec_success, results, error_msg = _execute_simulation(sim_code)
```

**Safe sandbox execution**:
- Isolated namespace
- Timeout protection
- Exception capture with full traceback
- Result validation

#### Step 3: Physics Validation
```python
physics_valid, physics_error = _validate_physics(results)
```

**Checks**:
- All variances ≥ 0
- All entropies ≥ 0
- All purities ∈ [0, 1]
- All fidelities ∈ [0, 1]
- No NaN or Inf values
- All metrics are real numbers

#### Step 4: Error-Driven Retry
```python
while not exec_success and retry_count < max_retries:
    sim_code_retry = _generate_simulation_code_with_error(
        design, 
        failed_code=sim_code,
        error_msg=error_msg  # Full traceback + physics errors
    )
    exec_success, results, error_msg = _execute_simulation(sim_code_retry)
```

**Error feedback includes**:
- Python exception type and message
- Line number where error occurred
- Full traceback
- Physics violation details (if applicable)
- Suggested fixes based on error type

---

## 3. Simulation Code Generation Prompts

### A. Initial Generation Prompt

**Key Sections** (see `simulation_agent.py` lines 250-400):

```
PART 1: UNDERSTAND DESIGNER'S INTENT
- What are they trying to achieve?
- What components did they specify?
- What parameters did they choose?

PART 2: IMPLEMENT FAITHFULLY
- Extract parameters from components
- Map optical elements to quantum operations
- Use THEIR sequence and parameters exactly

PART 3: VALIDATE IMPLEMENTATION
✓ Conservation laws (photon number, trace=1)
✓ Mathematical consistency (all positive metrics)
✓ Numerical hygiene (normalize, use abs())

PART 4: WORKING EXAMPLE
[Complete Mach-Zehnder code example]

PART 5: CODE STRUCTURE
[Template with exact format expected]
```

**Critical Instructions**:
- **DO NOT redesign** - implement exactly what designer specified
- Normalize after every operation: `state = state.unit()`
- All metrics must be real positive floats
- Visibility requires multiple phases (not single measurement)
- Use proper tensor products for multi-mode states

### B. Error Retry Prompt

**Structure** (see `simulation_agent.py` lines 726-850):

```
DEBUGGING PROTOCOL: ANALYZE BEFORE FIXING

1. IDENTIFY ROOT CAUSE
   - Syntax error?
   - Dimension mismatch?
   - Type error?
   - Physics violation?

2. TRACE THE PHYSICS
   - Which state caused error?
   - Which operation failed?
   - What were you computing?

3. COMMON MISTAKES TO CHECK
   ❌ Forgot normalization
   ❌ Complex treated as real
   ❌ Dimension mismatch
   ❌ Photon number exceeds cutoff
   ❌ Invalid variance calculation
   ❌ Entropy with negative eigenvalues
   ❌ Non-unitary operator

4. PHYSICS VALIDATION CHECKLIST
   ✓ States normalized
   ✓ Density matrices trace=1
   ✓ All variances ≥ 0
   ✓ All entropies ≥ 0
   ✓ All purities ∈ [0,1]
   ✓ Conservation laws respected
```

**Error-Specific Guidance**:
- For dimension errors → Check tensor product dimensions
- For negative values → Use `abs()` or validate calculation
- For NaN → Check for log(0) or divide by zero
- For complex → Use `.real` or `abs()` as appropriate

---

## 4. Human Approval & Memory Storage

### A. Post-Simulation UI Flow

```
Simulation Complete → Show Results
                      ↓
              ┌───────────────────┐
              │ Verdict Display   │
              │ - EXCELLENT/GOOD  │
              │ - Confidence: 87% │
              │ - Key Metrics     │
              │ - Recommendations │
              └────────┬──────────┘
                       ↓
              ┌───────────────────┐
              │ Human Decision    │
              │ ✅ Approve & Store│
              │ ❌ Discard        │
              └────────┬──────────┘
                       ↓
          Approved?    │    Discarded?
               ↓YES    │    ↓NO
          Store with   │    Don't store
          metadata:    │
          - human_approved: true
          - simulation_results
          - verdict & confidence
          - original query
```

**Code Location**: `app.py` lines 1545-1595

### B. Storage Structure

**What Gets Stored**:
```python
experiment_data = {
    # Design
    'title': "...",
    'description': "...",
    'components': [...],
    'beam_path': [...],
    'physics_explanation': "...",
    
    # Validation
    'simulation_results': {...},
    'verdict': 'EXCELLENT',
    'confidence': 0.87,
    
    # Human feedback
    'human_approved': True,
    'timestamp': "2025-11-19T...",
    
    # Context
    'user_query': "original user query",
    'conversation_context': [...]
}
```

**Storage Conditions**:
- User clicks "✅ Approve & Store"
- Simulation completed successfully
- Verdict available (EXCELLENT/GOOD/ACCEPTABLE)
- Not already stored (deduplication check)

### C. Deduplication Logic

```python
# Check if already stored this design
already_stored = st.session_state.get(f"stored_{title}", False)

if already_stored:
    st.success("✅ Already in knowledge base")
else:
    # Show approve/discard buttons
```

**Future Enhancement**: Semantic similarity check before storage
- Compare with existing experiments in memory
- If similarity > 0.95 → Ask "This is very similar to [existing]. Still store?"

---

## 5. Retrieval & Reuse

### A. Similarity Search

**When User Submits Query**:
```python
similar = memory.retrieve_similar_experiments(query, n_results=1)
if similar and similar[0]['similarity_score'] > 0.85:
    # High match - return existing design
    return existing_design
```

**Similarity Calculation**:
- Semantic embedding via ChromaDB
- Cosine similarity of query embeddings
- Considers: title, description, physics, user query

### B. UI Presentation

```
┌─────────────────────────────────────────┐
│ 📦 Retrieved from Memory                │
│                                         │
│ This experiment was previously          │
│ designed and validated:                 │
│                                         │
│ • Similarity: 92% match                 │
│ • Original: "hong ou mandel setup"     │
│ • Status: ✅ Human-Approved            │
│ • Past Verdict: EXCELLENT (94%)        │
│                                         │
│         [🔄 Generate New Instead]       │
└─────────────────────────────────────────┘
```

**User Options**:
1. **Accept** - Use the retrieved design (immediate, no cost)
2. **Generate New** - Force fresh generation with memory as context

---

## 6. Complete Workflow Example

### Example: User asks "design hong ou mandel interference"

```
Step 1: Retrieval Check
├─ Search memory for "hong ou mandel"
├─ Found: "Hong-Ou-Mandel Interference Setup" (similarity: 0.91)
├─ Status: Human-approved, EXCELLENT verdict
└─ Action: Return existing design

Step 2: User sees retrieved design
├─ Optical table diagram
├─ "📦 Retrieved from Memory" banner
├─ Metadata: 91% match, human-approved
└─ Option: "🔄 Generate New"

Step 3a: User accepts retrieved design
├─ No API calls
├─ Can run simulation immediately
├─ Can refine with chat questions
└─ Design is production-ready

Step 3b: User clicks "Generate New"
├─ Force regeneration flag set
├─ Skip retrieval, proceed to generation
├─ Use memory as context (not exact match)
├─ LLM generates fresh design
├─ Multi-cycle validation runs
└─ New design presented

Step 4: Run Simulation (if new design)
├─ Cycle 1: Generate code → Review → Execute
│   ├─ Review found issues → Revise
│   └─ Execute → Success
├─ Physics validation: All checks pass
└─ Results: Visibility = 0.95, EXCELLENT

Step 5: Human Decision
├─ User reviews: "This is better than stored version"
├─ Clicks "✅ Approve & Store"
├─ System stores with human_approved=True
└─ Next user will see THIS version (higher quality)

Result: Knowledge base grows with validated experiments
```

---

## 7. Configuration & Tuning

### Adjustable Parameters

#### Retrieval Threshold
```python
# llm_designer.py line 315
if similarity > 0.85:  # Adjust this threshold
```
- **0.95+**: Only exact matches (strict)
- **0.85-0.90**: High similarity (recommended)
- **0.75-0.85**: Moderate similarity (more retrieval)
- **< 0.75**: Low bar (may retrieve irrelevant)

#### Refinement Cycles
```python
# llm_designer.py init
self.max_refinement_cycles = 3  # Default: 3
```
- **1**: Fast but may miss errors
- **2**: Balanced
- **3**: Thorough (recommended)
- **5+**: Expensive, diminishing returns

#### Physics Validation Tolerances
```python
# simulation_agent.py _validate_physics()
if variance < -1e-10:  # Negative check
if entropy < -1e-10:   # Negative check
if purity < 0 or purity > 1.01:  # Range check
```

---

## 8. Monitoring & Debugging

### Key Log Messages

**Retrieval**:
```
🔍 Checking memory for existing similar experiments...
✅ Found highly similar experiment (similarity: 0.92)
📦 Returning existing design
```

**Generation**:
```
🤖 Starting design for: [query]
💡 No directly relevant past work found - designing from scratch
✅ Found relevant past work - using experience to enhance design!
```

**Simulation**:
```
👨‍🔬 Conducting physics code review...
✅ Code passed physics review!
⚙️  Executing simulation...
⚠️  Attempt 1 failed, retrying with error feedback...
✅ Retry 2 successful with valid physics!
```

**Storage**:
```
💾 User approved design for storage
✅ Stored as exp_1732046234.567
📚 Knowledge base: 25 experiments, 30 building blocks
```

### Debug Checks

**If designs not being retrieved**:
1. Check memory is enabled: `use_memory=True`
2. Verify experiments stored: `memory.get_statistics()`
3. Check similarity threshold (may be too high)
4. Inspect embedding quality: `memory.retrieve_similar_experiments(query, n=5)`

**If simulations always failing**:
1. Check QuTiP installed: `import qutip`
2. Review error messages in terminal
3. Check physics validation tolerances
4. Examine generated code in UI "View Simulation Code"

**If memory growing too large**:
1. Implement semantic deduplication before storage
2. Archive old experiments (timestamp-based)
3. Manually prune low-quality experiments
4. Adjust approval threshold

---

## 9. Future Enhancements

### Short Term
- [ ] Semantic deduplication check before storage
- [ ] User feedback comments on designs
- [ ] Design versioning (track iterations)
- [ ] Export/import knowledge base

### Medium Term
- [ ] Collaborative memory (share across users)
- [ ] Design ratings (5-star system)
- [ ] Automatic building block extraction improvements
- [ ] A/B testing of similar designs

### Long Term
- [ ] Active learning: Ask user clarifying questions
- [ ] Design optimization: Suggest parameter improvements
- [ ] Experiment planning: Multi-stage protocols
- [ ] Integration with lab equipment APIs

---

## Summary

The iterative refinement system provides:

✅ **Retrieval-First** - Reuse validated experiments (zero cost, instant)  
✅ **Multi-Cycle Generation** - Review → Execute → Fix → Validate (3 cycles)  
✅ **Human-in-the-Loop** - Expert approval before knowledge storage  
✅ **Deduplication** - Avoid redundant similar experiments  
✅ **Error-Driven Learning** - LLM learns from execution failures  
✅ **Physics Validation** - Comprehensive checks on all metrics  

**Result**: A continuously improving AI that learns from validated successes and human expert feedback, building a curated knowledge base of proven quantum experiment designs.
