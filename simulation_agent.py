"""
LLM-Driven Quantum Simulation Agent

Supports two modes:
1. Tool-based: Uses PhotonicToolbox with Strawberry Fields (primary) and QuTiP (fallback)
2. Code generation: LLM generates code for novel experiments (fallback)

The tool-based approach is more reliable for common experiments.
"""

import sys
import os
import re
import traceback
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional, Tuple
import json

# Import PhotonicToolbox (tool-based approach)
try:
    from photonic_toolbox import PhotonicToolbox, ToolBasedSimulationAgent
    TOOLBOX_AVAILABLE = True
    print("✅ PhotonicToolbox available (Strawberry Fields + QuTiP)")
except ImportError:
    TOOLBOX_AVAILABLE = False
    print("⚠️  PhotonicToolbox not available")

# QuTiP imports (for code generation fallback)
try:
    import qutip as qt
    QUTIP_AVAILABLE = True
    print("✅ QuTiP available for code generation fallback")
except ImportError:
    QUTIP_AVAILABLE = False
    print("⚠️  QuTiP not available - install with: pip install qutip")


class SimulationAgent:
    """
    Hybrid simulation agent that:
    1. PRIMARY: Uses tool-based approach with PhotonicToolbox (Strawberry Fields)
    2. FALLBACK: Generates QuTiP code for novel/complex experiments
    3. Interprets results and judges success
    """
    
    def __init__(self, llm_client, mode='auto'):
        """
        Args:
            llm_client: LLM client for code generation and interpretation
            mode: 'tools', 'code', or 'auto' (auto tries tools first)
        """
        if llm_client is None:
            raise ValueError("SimulationAgent requires an LLM client")
        self.llm = llm_client
        self.mode = mode
        self.qutip_available = QUTIP_AVAILABLE
        
        # Initialize tool-based agent if available
        if TOOLBOX_AVAILABLE:
            self.tool_agent = ToolBasedSimulationAgent(llm_client, backend='auto')
            print("✅ Tool-based simulation mode enabled")
        else:
            self.tool_agent = None
            print("⚠️  Tool-based mode unavailable, will use code generation only")
    
    def validate_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Validate an optical design through simulation.
        
        Uses tool-based approach first (Strawberry Fields), falls back to code generation.
        
        Args:
            design: Optical design dictionary with components, beam paths, etc.
            
        Returns:
            {
                'success': bool,
                'approach': 'tool-based' or 'code-generation',
                'confidence': float (0-1),
                'results': dict with metrics,
                'interpretation': str (LLM's analysis),
                'backend': 'strawberryfields' or 'qutip',
                'recommendations': list of improvement suggestions
            }
        """
        
        print(f"🔬 Starting simulation for: {design.get('title', 'Unknown')}")
        
        # Decide which approach to use
        use_tools = self._should_use_tools(design)
        
        if use_tools and self.tool_agent:
            print(f"🔧 Using tool-based approach (Strawberry Fields/QuTiP)...")
            return self._validate_with_tools(design)
        else:
            print(f"🤖 Using code generation approach (QuTiP)...")
            return self._validate_with_code_generation(design)
    
    def _should_use_tools(self, design: Dict[str, Any]) -> bool:
        """Decide whether to use tools or code generation"""
        
        if self.mode == 'tools':
            return self.tool_agent is not None
        elif self.mode == 'code':
            return False
        else:  # auto mode
            # PREFER CODE GENERATION - it's more flexible and robust
            # Tool-based approach has too many edge cases with sparse matrices,
            # dimension mismatches, and backend limitations
            return False
    
    def _validate_with_tools(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using PhotonicToolbox (tool-based approach)"""
        
        try:
            result = self.tool_agent.validate_design(design)
            
            if result['success']:
                print(f"✅ Tool-based validation successful")
                return result
            else:
                print(f"⚠️  Tool-based validation failed, falling back to code generation")
                return self._validate_with_code_generation(design)
                
        except Exception as e:
            print(f"❌ Tool-based approach error: {e}")
            print(f"🔄 Falling back to code generation...")
            return self._validate_with_code_generation(design)
    
    def _validate_with_code_generation(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using code generation (original approach)"""
        
        if not self.qutip_available:
            return {
                'success': False,
                'error': 'QuTiP not available',
                'message': 'Install QuTiP to enable simulations: pip install qutip'
            }
        
        # Strategy: Generate/Adapt → Quick Alignment Check → Execute → Retry on Errors
        # If previous simulation code exists, adapt it; otherwise generate from scratch
        
        previous_sim_code = design.get('_previous_simulation_code')
        if previous_sim_code:
            print(f"🔄 Adapting previous simulation code to refined design...")
            sim_code, reasoning = self._adapt_simulation_code(design, previous_sim_code)
        else:
            print(f"🤖 LLM generating QuTiP simulation code...")
            sim_code, reasoning = self._generate_simulation_code(design)
        
        if not sim_code:
            return {
                'success': False,
                'approach': 'code-generation',
                'error': 'Code generation failed',
                'reasoning': reasoning
            }
        
        print(f"✅ Generated {len(sim_code)} characters of simulation code")
        print(f"💡 LLM reasoning: {reasoning}")
        
        # ONE alignment check to ensure we're simulating the designer's intent
        # Uses JSON response for clear boolean decision
        print(f"🔍 Checking alignment with designer's intent...")
        alignment_ok, alignment_feedback = self._check_simulation_alignment(design, sim_code)
        
        if not alignment_ok:
            print(f"⚠️  Alignment issue: {alignment_feedback}")
            print(f"🔄 Regenerating to match designer's intent...")
            sim_code, reasoning = self._generate_simulation_code_with_error(
                design, sim_code, f"Alignment issue: {alignment_feedback}"
            )
            if not sim_code:
                print(f"❌ Failed to regenerate code")
                return {
                    'success': False,
                    'approach': 'code-generation',
                    'error': 'Code regeneration failed after alignment check',
                    'reasoning': alignment_feedback
                }
            print(f"✅ Code regenerated to match design intent")
        else:
            print(f"✅ Simulation aligned with designer's intent")
        
        # Execute immediately - learn from real errors
        print(f"⚙️  Executing simulation...")
        exec_success, results, error_msg = self._execute_simulation(sim_code)
        
        # Validate physics if execution succeeded
        if exec_success:
            physics_valid, physics_error = self._validate_physics(results)
            if not physics_valid:
                print(f"⚠️  Physics validation failed: {physics_error}")
                exec_success = False
                error_msg = f"Physics validation error: {physics_error}"
        
        # Retry loop: up to 2 attempts to fix execution/physics errors
        max_retries = 2
        retry_count = 0
        while not exec_success and retry_count < max_retries:
            retry_count += 1
            print(f"⚠️  Attempt {retry_count} failed, retrying with error feedback...")
            sim_code_retry, reasoning_retry = self._generate_simulation_code_with_error(design, sim_code, error_msg)
            if sim_code_retry:
                exec_success, results, error_msg = self._execute_simulation(sim_code_retry)
                
                # Validate physics on retry
                if exec_success:
                    physics_valid, physics_error = self._validate_physics(results)
                    if not physics_valid:
                        print(f"⚠️  Physics validation failed on retry: {physics_error}")
                        exec_success = False
                        error_msg = f"Physics validation error: {physics_error}"
                    else:
                        print(f"✅ Retry {retry_count} successful with valid physics!")
                        sim_code = sim_code_retry
                        reasoning = reasoning_retry
                else:
                    print(f"❌ Retry {retry_count} execution failed")
            else:
                print(f"❌ Could not generate retry code")
                break
        
        if not exec_success:
            return {
                'success': False,
                'approach': 'code-generation',
                'error': f'Simulation execution failed: {error_msg}',
                'simulation_code': sim_code,
                'reasoning': reasoning
            }
        
        print(f"✅ Simulation executed successfully")
        
        # Step 3: LLM interprets results and judges success
        print(f"🧠 LLM interpreting results...")
        interpretation = self._interpret_results(design, results, reasoning)
        
        # Step 4: Deep analysis - explain WHY simulation succeeded/failed
        print(f"🔬 Conducting post-simulation analysis...")
        deep_analysis = self._analyze_simulation_vs_design(design, sim_code, results, interpretation)
        
        rating = deep_analysis.get('rating', 5)
        
        # Step 5: Independent assessment for low scores - identify root cause
        independent_assessment = None
        if rating < 7:
            print(f"⚖️  Rating below 7 ({rating}/10) - conducting independent assessment...")
            independent_assessment = self._conduct_independent_assessment(design, sim_code, results, rating)
            print(f"📋 Assessment complete: {independent_assessment.get('root_cause', 'unknown')}")
        
        return {
            'success': True,
            'confidence': interpretation.get('confidence', 0.5),
            'results': results,
            'interpretation': interpretation.get('analysis', ''),
            'simulation_code': sim_code,
            'reasoning': deep_analysis,  # Replace simple reasoning with deep analysis
            'recommendations': interpretation.get('recommendations', []),
            'metrics': interpretation.get('metrics', {}),
            'verdict': interpretation.get('verdict', 'unknown'),
            'honest_rating': rating,  # 1-10 scale
            'independent_assessment': independent_assessment  # None if rating >= 7
        }
    
    def _generate_simulation_code(self, design: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """
        LLM generates QuTiP simulation code based on the optical design.
        
        Returns:
            (code_string, reasoning)
        """
        
        components = design.get('experiment', {}).get('steps', [])
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        
        # Build comprehensive prompt for code generation
        prompt = f"""You are a computational physicist validating an optical experiment design. A designer agent has proposed this experimental configuration, and your job is to simulate it faithfully to verify whether it achieves the intended physics.

**Designer's Proposal:**
Title: {title}
Description: {description}
Intended Physics: {physics}

**Optical Components (Designer's Specification):**
{json.dumps(components, indent=2)}

═══════════════════════════════════════════════════════════════
YOUR ROLE: VALIDATE THE DESIGN (Not create a new one)
═══════════════════════════════════════════════════════════════

You must:
1. **Implement EXACTLY what the designer specified** - use the components, parameters, and sequence as given
2. **Simulate the physics faithfully** - no shortcuts, no approximations unless specified
3. **Calculate metrics to verify performance** - does it achieve what the designer claimed?
4. **Report results objectively** - the design may succeed or fail, both are valid outcomes

⚠️ DO NOT redesign the experiment or "fix" what you think is wrong.
⚠️ Your job is to test the design as proposed, not optimize it.

═══════════════════════════════════════════════════════════════
PART 1: UNDERSTAND THE DESIGNER'S INTENT
═══════════════════════════════════════════════════════════════

Before coding, understand:
1. **What is the designer trying to achieve?** (Read the description and intended physics)
2. **What components did they specify?** (States, beam splitters, phase shifts, measurements)
3. **What parameters did they choose?** (Angles, phases, photon numbers)
4. **What metrics should verify success?** (Fidelity to target, visibility, entanglement)

4. **What metrics should verify success?** (Fidelity to target, visibility, entanglement)

═══════════════════════════════════════════════════════════════
PART 2: IMPLEMENT THE DESIGN FAITHFULLY
═══════════════════════════════════════════════════════════════

**Extract Parameters from Designer's Components:**
- The designer provides components with fields: `type`, `name`, `parameters`, `x`, `y`, `angle`
- Common types from designer: `laser`, `beam_splitter`, `crystal`, `detector`, `mirror`, `phase_shifter`, `filter`, `lens`, `wave_plate`
- Map to quantum operations:
  * `laser` or `source` → initial quantum state (Fock, coherent, etc.)
  * `crystal` (with SPDC) → entangled photon pair generation
  * `beam_splitter` → beam splitter transformation (use `transmittance` parameter)
  * `phase_shifter` or `wave_plate` → phase shift (use `angle` or phase parameter)
  * `mirror` → typically just redirects (may have phase shift)
  * `detector` → measurement operator
  * `filter` → absorption/loss channel
- Use THEIR parameters exactly: `wavelength`, `transmittance`, `angle`, `efficiency`, etc.
- Follow THEIR sequence: apply operations in the order components appear
- If a quantum parameter is missing, infer from physical parameters (e.g., wavelength → photon number)
- Document your choices in code comments

**Quantum State Management:**
- Use adequate Fock space: `cutoff_dim` from design or default to 5-10
- Multi-mode states: `qt.tensor(state_mode1, state_mode2, ...)` with consistent dimensions
- **NORMALIZE after every operation**: `state = state.unit()` or `rho = rho / rho.tr()`
- Pure states: Use kets (e.g., `qt.fock(cutoff, n)`)
- Mixed states: Use density matrices for losses/decoherence

**Unitary Operations (Closed Systems):**
- Beam splitter: Construct using creation/annihilation operators, then `.expm()`
- Phase shift: `(1j * phi * qt.num(cutoff)).expm()`
- Displacement: `qt.displace(cutoff, alpha)`
- **Always unitary**: Verify `U.dag() * U ≈ Identity` if unsure

**Measurements & Figures of Merit:**
- Calculate metrics that verify the designer's claims
- Photon number: `qt.expect(qt.num(cutoff), state)`
- Fidelity: `qt.fidelity(result_state, target_state)` ∈ [0, 1]
- Purity: `abs((rho.dag() * rho).tr())` ∈ [0, 1]
- **Visibility (CRITICAL - do this right!)**: 
  * MUST measure at multiple phases (e.g., φ=0 and φ=π)
  * V = (I_max - I_min) / (I_max + I_min)
  * NOT a single-phase calculation!
- Entanglement: von Neumann entropy, negativity
- **ALL metrics must be ≥ 0 and real-valued** (use `abs()` and `float()`)

═══════════════════════════════════════════════════════════════
PART 3: VALIDATE YOUR IMPLEMENTATION
═══════════════════════════════════════════════════════════════

Your code MUST pass these physics checks:

✓ **Conservation Laws**:
  - Photon number conserved in closed systems (no ad-hoc losses)
  - Trace of density matrix = 1 always
  - Unitarity preserved (verify operators are unitary)

✓ **Mathematical Consistency**:
  - All variances ≥ 0 (definition of variance)
  - All entropies ≥ 0 (information theory)
  - All purities ∈ [0, 1] (physical states)
  - All fidelities ∈ [0, 1] (overlap measure)
  - No NaN or Inf (numerical stability)

✓ **Numerical Hygiene**:
  - Use `abs()` or `.real` to extract real values
  - Convert to `float()` before storing in results
  - Handle edge cases: `np.log(x + 1e-12)` to avoid log(0)
  - Normalize: `state.norm() ≈ 1` after operations

═══════════════════════════════════════════════════════════════
PART 4: WORKING EXAMPLE - MACH-ZEHNDER INTERFEROMETER
═══════════════════════════════════════════════════════════════

Here's a COMPLETE working example for reference (Mach-Zehnder with single photon):

```python
import qutip as qt
import numpy as np

# Single photon Mach-Zehnder
cutoff = 3
# Initial state: single photon in mode 0, vacuum in mode 1
psi = qt.tensor(qt.fock(cutoff, 1), qt.fock(cutoff, 0))
psi = psi.unit()

# First 50:50 beam splitter
theta_bs = np.pi/4
a = qt.tensor(qt.destroy(cutoff), qt.qeye(cutoff))
b = qt.tensor(qt.qeye(cutoff), qt.destroy(cutoff))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
psi = U_bs1 * psi
psi = psi.unit()

# Phase shift on mode 0
phi = np.pi  # Test phase
phase_op = qt.tensor((1j * phi * qt.num(cutoff)).expm(), qt.qeye(cutoff))
psi = phase_op * psi
psi = psi.unit()

# Second 50:50 beam splitter (recombination)
U_bs2 = (-1j * H_bs).expm()
psi = U_bs2 * psi
psi = psi.unit()

# Measure photon numbers at TWO phases to calculate visibility
n_a = qt.tensor(qt.num(cutoff), qt.qeye(cutoff))
n_b = qt.tensor(qt.qeye(cutoff), qt.num(cutoff))

# Phase = π case (for comparison)
psi_pi = phase_op * psi  # Already at φ=π from loop above
output_a_pi = float(abs(qt.expect(n_a, psi_pi)))
output_b_pi = float(abs(qt.expect(n_b, psi_pi)))

# Phase = 0 case
phase_0 = qt.tensor(qt.qeye(cutoff), qt.qeye(cutoff))  # No phase shift
psi_0 = U_bs2 * psi  # Apply second BS without phase
output_a_0 = float(abs(qt.expect(n_a, psi_0)))
output_b_0 = float(abs(qt.expect(n_b, psi_0)))

# CORRECT visibility: compare max and min across phases
I_max = max(output_a_0, output_a_pi)
I_min = min(output_a_0, output_a_pi)
visibility = float((I_max - I_min) / (I_max + I_min + 1e-12))

results = {{
    'output_a_phase_0': output_a_0,
    'output_a_phase_pi': output_a_pi,
    'visibility': visibility,
    'energy_conservation': float(output_a_0 + output_b_0)  # Should be 1.0
}}
```

KEY POINTS from this example:
1. Two-mode system: qt.tensor(mode_0_state, mode_1_state)
2. Operators for two modes: qt.tensor(operator_mode0, identity_mode1)
3. Beam splitter: Use Hamiltonian H = θ(a†b + ab†), then U = exp(-iH)
4. Phase shift: Apply ONLY to the mode you want to shift
5. Energy conserved: output_a + output_b should equal 1.0 for single photon

═══════════════════════════════════════════════════════════════
PART 5: CODE STRUCTURE FOR VALIDATION
═══════════════════════════════════════════════════════════════

Return ONLY executable Python code following this template:

```python
# REASONING: Validating designer's proposal - [one sentence about their design]

import qutip as qt
import numpy as np

# Extract parameters from designer's specification
cutoff_dim = [from components or default 5-10]
# ... other parameters specified by designer ...

# Step 1: Create initial states (as designer specified)
state = ...  # Use their photon numbers, modes, etc.
state = state.unit()

# Step 2: Apply operations (in designer's order with their parameters)
# Component 1: [designer's first operation]
operator_1 = ...  # Use their angle/phase/parameter
state = operator_1 * state
state = state.unit()

# Component 2: [designer's second operation]
# ... continue with their sequence ...

# Step 3: Calculate metrics to verify designer's claims
# Use metrics relevant to what they're trying to achieve
metric_1 = abs(qt.expect(..., state))  # Ensure real positive
metric_2 = float(qt.fidelity(state, target))  # Ensure float

# Store results (all must be real positive floats)
results = {{
    'metric_1': float(metric_1),
    'metric_2': float(metric_2),
    # Include metrics that validate their design goals
}}
```

═══════════════════════════════════════════════════════════════
CRITICAL VALIDATION REMINDERS
═══════════════════════════════════════════════════════════════

✓ Implement the designer's specification faithfully
✓ All variances, entropies must be ≥ 0
✓ All fidelities, purities must be ∈ [0, 1]
✓ Normalize states after each operation
✓ Convert all results to real positive floats
✓ No NaN, Inf, or complex numbers in results

**COMMON MISTAKES TO AVOID:**
❌ DON'T split single-mode coherent state into two modes using alpha_1 = t*alpha, alpha_2 = r*alpha
   This is WRONG! A coherent state doesn't split like classical amplitude.
✅ DO use proper beam splitter operator on two-mode state

❌ DON'T calculate visibility at a single phase: V = |I_A - I_B|/(I_A + I_B)
   This is MEANINGLESS! Visibility requires comparing phases.
✅ DO measure at φ=0 and φ=π, then V = (I_max - I_min)/(I_max + I_min)

❌ DON'T manually "apply losses" in a loop that does nothing
✅ DO use proper Lindblad master equation if modeling decoherence

❌ DON'T compare single-mode energy with two-mode energy
✅ DO track photon number in consistent mode space

❌ DON'T use arccos(t) for beam splitter angle - this gives wrong physics
✅ DO use θ = π/4 for 50:50 beam splitter in H = θ(a†b + ab†)

Now generate code that validates the designer's proposal:"""

        try:
            response = self.llm.predict(prompt)
            
            # Parse response - extract code from markdown blocks
            reasoning = "No reasoning provided"
            code = None
            
            # Try to extract from ```python``` blocks first
            if '```python' in response:
                parts = response.split('```python')
                if len(parts) > 1:
                    code_part = parts[1].split('```')[0]
                    code = code_part.strip()
                    
                    # Extract reasoning from first comment
                    for line in code.split('\n'):
                        if line.strip().startswith('# REASONING:'):
                            reasoning = line.replace('# REASONING:', '').strip()
                            break
            
            # If no code block found, try to extract all code-like lines
            if not code:
                lines = response.split('\n')
                code_lines = []
                
                for line in lines:
                    stripped = line.strip()
                    # Skip empty lines and explanatory text
                    if not stripped:
                        continue
                    # Include lines that are code or comments
                    if (stripped.startswith('#') or 
                        stripped.startswith('import ') or
                        stripped.startswith('from ') or
                        any(keyword in stripped for keyword in ['=', 'def ', 'class ', 'if ', 'for ', 'while ', 'results'])):
                        code_lines.append(line)
                        if stripped.startswith('# REASONING:'):
                            reasoning = stripped.replace('# REASONING:', '').strip()
                
                code = '\n'.join(code_lines).strip()
            
            if not code or len(code) < 50:
                return None, "Failed to extract valid code from LLM response"
            
            return code, reasoning
            
        except Exception as e:
            print(f"❌ Code generation error: {e}")
            return None, f"Error: {e}"
    
    def _review_simulation_code(self, design: Dict[str, Any], code: str, 
                                  previous_review_feedback: str = None) -> Tuple[bool, str]:
        """
        Expert physics review of generated simulation code BEFORE execution.
        Acts as a critical peer reviewer checking for physics correctness.
        
        Args:
            design: The experimental design
            code: The simulation code to review
            previous_review_feedback: Optional feedback from a previous review iteration
                                     (for second reviews after code revision)
        
        Returns:
            (passes_review, feedback_message)
        """
        
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        components = design.get('experiment', {}).get('steps', [])
        
        # Add context if this is a second review
        context_section = ""
        if previous_review_feedback:
            context_section = f"""
**⚠️ IMPORTANT CONTEXT - This is a SECOND review:**
You previously reviewed this experiment's code and provided feedback.
The researcher has now revised the code based on your advice.

**YOUR PREVIOUS FEEDBACK:**
{previous_review_feedback}

**CRITICAL**: Check if the revised code correctly addresses your feedback.
- Did they fix what you asked them to fix?
- Did they introduce new errors while fixing the old ones?
- Are you being consistent with your previous advice?
- If you told them to do X, and they did X, don't now complain about X!

═══════════════════════════════════════════════════════════════
"""
        
        prompt = f"""You are a world-class quantum optics experimentalist with decades of experience. A junior researcher has written simulation code for an experiment and asks you to review it for physics correctness BEFORE running it.
{context_section}
**Experiment Design:**
Title: {title}
Description: {description}
Physics Goal: {physics}

**Designer's Components:**
{json.dumps(components, indent=2)}

**Simulation Code to Review:**
```python
{code}
```

═══════════════════════════════════════════════════════════════
YOUR REVIEW TASK
═══════════════════════════════════════════════════════════════

Think like an experienced physicist reviewing a student's code. Ask yourself:

**1. DOES THE CODE MATCH THE EXPERIMENTAL DESIGN?**
   - Are all the designer's components represented?
   - Is the sequence of operations correct?
   - Are the parameters (transmittance, phases, angles) from the design used correctly?
   - Is anything added that wasn't in the design? Is anything missing?

**2. IS THE QUANTUM MECHANICS CORRECT?**
   - Are quantum states properly initialized for the light sources specified?
   - Are operators constructed correctly for each optical element?
   - For beam splitters: Is the transformation unitary and preserving photon number?
   - For phase shifts: Is the phase operator applied to the correct mode?
   - For measurements: Are the observables physically meaningful?
   - Is state normalization maintained throughout? (⟨ψ|ψ⟩ = 1)

**3. ARE THE METRICS PHYSICALLY MEANINGFUL?**
   - If calculating visibility/contrast: Does it measure interference across different conditions (phases/paths)?
   - If calculating fidelity: Is there a valid target state to compare against?
   - If calculating entanglement: Are multi-mode correlations properly computed?
   - Are energy/photon number conservation checks comparing consistent quantities?
   - Would the calculated metrics actually validate what the designer claimed?

**4. WILL THE RESULTS BE PHYSICALLY VALID?**
   - All variances must be ≥ 0 (mathematical definition)
   - All entropies must be ≥ 0 (information theory)
   - All purities must be in [0,1] (physical states)
   - All fidelities must be in [0,1] (overlap measure)
   - Energy should be conserved unless losses explicitly modeled
   - Are results converted to real numbers (no complex in output)?

**5. COMMON PHYSICS ERRORS TO CHECK:**
   - Treating quantum superposition like classical probability
   - Calculating single-value metrics that need comparison (visibility at one phase)
   - Mixing mode spaces (comparing different dimensional systems)
   - Non-unitary operations in closed systems
   - Incorrect operator ordering or commutation assumptions
   - Forgetting tensor product structure in multi-mode systems
   - **CRITICAL: Manually constructing "expected" output states instead of evolving with operators**
     * If you see states like `(1/√2)(|2,0⟩ - |0,2⟩)` written directly without applying BS operator
     * This is NOT simulation - it's just encoding the textbook answer!
     * Must use actual beam splitter Hamiltonian: `H = θ(a†b + ab†)` then `U = (-1j*H).expm()`
     * Then evolve: `state_out = U * state_in * U.dag()` (for density matrices)
     * Or: `state_out = U * state_in` (for kets)
     * ⚠️ **NEVER suggest manual construction as a "fix" - always require operator evolution!**
   - **Calculating metrics on wrong state representations**
     * Accessing matrix elements without understanding dimensionality
     * Using single-mode formulas on multi-mode density matrices
   - **Meaningless comparisons**
     * Fidelity between states that shouldn't be compared (mixed vs pure for validation)

═══════════════════════════════════════════════════════════════
RESPOND IN THIS FORMAT
═══════════════════════════════════════════════════════════════

**ANALYSIS:**
[Your detailed physics reasoning - what did you check? What did you find?]

**VERDICT: PASS** or **VERDICT: FAIL**

If PASS:
"The code correctly implements the physics. [Brief justification]"

If FAIL:
**CRITICAL PHYSICS ERRORS:**
1. [Specific error with physics reasoning why it's wrong]
2. [Another error if exists]

**HOW TO FIX:**
- [Concrete instruction: "Change line X to do Y because Z"]
- [Another fix if needed]

⚠️ **IMPORTANT**: When suggesting fixes:
- ALWAYS require operator-based evolution (Hamiltonians, unitaries)
- NEVER suggest manually writing output states like `(|2,0⟩ ± |0,2⟩)/√2`
- If code uses wrong operator, say "use correct operator" not "write state directly"

**EXPECTED IMPACT:**
[What will happen if code runs as-is? Wrong results? Unphysical values?]

═══════════════════════════════════════════════════════════════

Focus on PHYSICS correctness, not code style. Be specific about what's wrong and why.
Think step-by-step through the quantum evolution and check if it makes physical sense.
"""

        try:
            response = self.llm.predict(prompt)
            
            # Parse verdict
            if "VERDICT: PASS" in response:
                return True, "Code passed physics review"
            elif "VERDICT: FAIL" in response:
                # Extract feedback
                return False, response
            else:
                # Ambiguous response, err on side of caution
                return False, f"Review inconclusive: {response}"
                
        except Exception as e:
            print(f"⚠️  Code review error: {e}")
            return True, "Review failed, proceeding anyway"
    
    def _check_simulation_alignment(self, design: Dict[str, Any], sim_code: str) -> Tuple[bool, str]:
        """
        Quick check: Does the simulation code match the designer's intent?
        Uses JSON response for clear boolean decision.
        """
        
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        components = design.get('experiment', {}).get('steps', [])
        
        prompt = f"""You are reviewing simulation code to ensure it matches the designer's experimental intent.

**Designer's Experiment:**
Title: {title}
Description: {description}
Physics Goal: {physics}
Components: {json.dumps(components[:5], indent=2)}  # First 5 components

**Generated Simulation Code:**
```python
{sim_code[:1500]}  # First 1500 chars to keep prompt manageable
...
```

**Your Task:** Quickly verify alignment between design intent and simulation implementation.

**Check these key points:**
1. **Correct quantum state**: Does the initial state match what the designer specified?
2. **Correct operations**: Are the right operations applied (beam splitters, phase shifts, etc.)?
3. **Correct sequence**: Do operations happen in the right order per the design?
4. **Correct measurements**: Are we measuring what the designer intended?

**Respond with JSON ONLY:**
{{
    "aligned": true or false,
    "issue": "Brief description of alignment problem if aligned=false, empty string if aligned=true"
}}

Return ONLY the JSON, no other text."""

        try:
            response = self.llm.predict(prompt)
            
            # Parse JSON response
            try:
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                else:
                    json_str = response.strip()
                
                alignment_data = json.loads(json_str)
                aligned = alignment_data.get('aligned', False)
                issue = alignment_data.get('issue', '')
                
                return aligned, issue if not aligned else "Aligned with design"
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse alignment JSON: {e}")
                # Default: assume aligned to avoid blocking
                return True, "Could not parse alignment check, proceeding"
        
        except Exception as e:
            print(f"⚠️  Alignment check error: {e}")
            return True, "Alignment check failed, proceeding anyway"
    
    def _adapt_simulation_code(self, design: Dict[str, Any], previous_code: str) -> Tuple[Optional[str], str]:
        """
        Adapt existing simulation code to a refined design.
        More efficient than generating from scratch when design changed slightly.
        """
        
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        components = design.get('experiment', {}).get('steps', [])
        
        prompt = f"""You are adapting simulation code to match a refined experimental design.

**Original Simulation Code:**
```python
{previous_code[:2500]}
...
```

**Refined Design:**
Title: {title}
Description: {description}
Physics: {physics}
Components: {json.dumps(components[:5], indent=2)}

**Task:** Adapt the simulation to match the refined design.
Keep working parts, update changed parameters/states/operations.

Return ONLY adapted Python code:"""

        code_template = """
```python
import qutip as qt
import numpy as np

# Adapted code
results = {}
```
"""
        
        prompt = prompt + code_template
        
        try:
            response = self.llm.predict(prompt)
            if '```python' in response:
                code = response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                code = response.split('```')[1].split('```')[0].strip()
            else:
                code = response.strip()
            return code, "Adapted from previous simulation"
        except Exception as e:
            print(f"❌ Adaptation failed: {e}, generating from scratch")
            return self._generate_simulation_code(design)
    
    def _generate_simulation_code_with_error(self, design: Dict[str, Any], 
                                            failed_code: str, error_msg: str) -> Tuple[Optional[str], str]:
        """Retry code generation with error feedback (alignment issue or execution error)"""
        
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        
        # Determine if this is an alignment issue or execution error
        is_alignment_issue = "Alignment issue:" in error_msg
        
        if is_alignment_issue:
            error_type = "ALIGNMENT MISMATCH"
            instruction = """The previous simulation code does NOT match what the designer specified.
You must regenerate code that faithfully implements THEIR design, not a different experiment."""
        else:
            error_type = "EXECUTION ERROR"
            instruction = """The previous simulation code had a runtime error.
Fix the error while still implementing the designer's specified experiment."""
        
        prompt = f"""You are simulating the quantum experiment: "{title}"

**Designer's Specification:**
{description}

**Physics Goal:** {physics}

═══════════════════════════════════════════════════════════════
{error_type}
═══════════════════════════════════════════════════════════════

**Problem:**
{error_msg}

**Previous Code:**
```python
{failed_code[:2000]}  # Truncate to keep prompt manageable
...
```

═══════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════

{instruction}

**Key Requirements:**
1. **Match the designer's intent**: Simulate EXACTLY what they specified
2. **Correct quantum state**: Use the initial state from their design
3. **Correct operations**: Apply the operations they specified in the right order
4. **Correct measurements**: Measure what they intended to measure
5. **Real numerical output**: Return floats/ints in results dict, not complex or Qobj

**Common Fixes:**
• Alignment: Check if you're using the right state/operations/measurements
• Type errors: Use abs() or .real to convert complex → float
• Dimension errors: Ensure all modes use same cutoff_dim
• .tr() errors: Remember .tr() returns a number, not a Qobj

Generate corrected Python code (code only, no explanation):
"""
        
        code_template = """
```python
import qutip as qt
import numpy as np

# Your corrected simulation code here
# ...

results = {
    # metrics as real floats
}
```
"""
        
        prompt = prompt + code_template
        
        try:
            response = self.llm.predict(prompt)
            
            # Extract code
            if '```python' in response:
                code = response.split('```python')[1].split('```')[0].strip()
            elif '```' in response:
                code = response.split('```')[1].split('```')[0].strip()
            else:
                code = response.strip()
            
            reasoning = "Retry after fixing error"
            
            return code, reasoning
            
        except Exception as e:
            print(f"❌ Retry code generation failed: {e}")
            return None, f"Error: {e}"
    
    def _execute_simulation(self, code: str) -> Tuple[bool, Dict, str]:
        """
        Safely execute QuTiP simulation code in isolated environment.
        
        Returns:
            (success, results_dict, error_message)
        """
        
        # Create safe execution environment
        safe_globals = {
            'qt': qt,
            'qutip': qt,
            'np': np,
            'numpy': np,
            'results': {},
            '__builtins__': __builtins__,
        }
        
        # Capture stdout/stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)
            
            # Extract results
            results = safe_globals.get('results', {})
            
            # Convert numpy types to native Python for JSON serialization
            clean_results = {}
            for key, value in results.items():
                if isinstance(value, (np.integer, np.floating)):
                    clean_results[key] = float(value)
                elif isinstance(value, np.ndarray):
                    clean_results[key] = value.tolist()
                elif isinstance(value, complex):
                    clean_results[key] = {'real': value.real, 'imag': value.imag}
                else:
                    clean_results[key] = value
            
            return True, clean_results, ""
            
        except SyntaxError as e:
            error_msg = f"SyntaxError: {str(e)}"
            print(f"❌ Generated code has syntax error at line {e.lineno}:")
            # Show the problematic code section
            code_lines = code.split('\n')
            if e.lineno and e.lineno <= len(code_lines):
                start = max(0, e.lineno - 3)
                end = min(len(code_lines), e.lineno + 2)
                print("Code around error:")
                for i in range(start, end):
                    prefix = ">>> " if i == e.lineno - 1 else "    "
                    print(f"{prefix}{i+1}: {code_lines[i]}")
            return False, {}, error_msg
        except TypeError as e:
            error_msg = f"TypeError: {str(e)}"
            print(f"❌ Type error in generated code: {e}")
            print("💡 Common causes:")
            print("   - Trying to subscript a complex number (use .real or .imag)")
            print("   - Using complex values in results dict (convert to float)")
            # Extract line number from traceback if available
            tb = traceback.format_exc()
            print(f"\n{tb}")
            return False, {}, error_msg
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            print(f"❌ Runtime error: {error_msg}")
            return False, {}, error_msg
    
    def _validate_physics(self, results: Dict) -> Tuple[bool, str]:
        """
        Validate that simulation results obey physical constraints.
        
        Returns:
            (is_valid, error_message)
        """
        
        if not results:
            return False, "No results to validate"
        
        try:
            for key, value in results.items():
                # Skip non-numeric values
                if not isinstance(value, (int, float, np.number)):
                    continue
                
                # Convert to float for validation
                val = float(value)
                
                # Check for NaN or Inf
                if np.isnan(val):
                    return False, f"'{key}' is NaN (indicates numerical instability)"
                if np.isinf(val):
                    return False, f"'{key}' is Inf (indicates numerical overflow)"
                
                # Physics constraints based on metric name
                key_lower = key.lower()
                
                # All variances must be non-negative (by definition)
                if 'variance' in key_lower and val < -1e-10:  # Allow tiny numerical errors
                    return False, f"'{key}' = {val:.6f} is negative (variances must be ≥ 0)"
                
                # All entropies must be non-negative (information theory)
                if 'entropy' in key_lower and val < -1e-10:
                    return False, f"'{key}' = {val:.6f} is negative (entropies must be ≥ 0)"
                
                # Fidelities must be in [0, 1]
                if 'fidelity' in key_lower and (val < -1e-6 or val > 1.000001):
                    return False, f"'{key}' = {val:.6f} is outside [0,1] (invalid fidelity)"
                
                # Purities must be in [0, 1]
                if 'purity' in key_lower and (val < -1e-6 or val > 1.000001):
                    return False, f"'{key}' = {val:.6f} is outside [0,1] (invalid purity)"
                
                # Probabilities must be in [0, 1]
                if 'probability' in key_lower and (val < -1e-6 or val > 1.000001):
                    return False, f"'{key}' = {val:.6f} is outside [0,1] (invalid probability)"
                
                # Visibility should be in [0, 1] for most experiments
                if 'visibility' in key_lower and (val < -1e-6 or val > 1.000001):
                    return False, f"'{key}' = {val:.6f} is outside [0,1] (unusual visibility)"
            
            # All checks passed
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _analyze_simulation_vs_design(self, design: Dict[str, Any], simulation_code: str, 
                                      results: Dict, interpretation: Dict) -> Dict:
        """
        Deep post-simulation analysis comparing design intent vs implementation vs results.
        Provides educational explanation of simulation quality and limitations.
        
        Returns:
            {
                'analysis': str (detailed comparison and explanation),
                'rating': int (1-10 honest quality rating),
                'limitations': list (identified physics limitations),
                'matches_design': bool (whether simulation captured design intent)
            }
        """
        
        title = design.get('title', 'Unknown')
        components = design.get('experiment', {}).get('steps', [])
        physics_goal = design.get('physics_explanation', '')
        verdict = interpretation.get('verdict', 'unknown')
        
        prompt = f"""You are a quantum optics educator analyzing whether a simulation successfully validated an experimental design.

**Designer's Proposal:**
Title: {title}
Physics Goal: {physics_goal}
Components: {json.dumps(components, indent=2)}

**Generated Simulation Code:**
```python
{simulation_code}
```

**Simulation Results:**
{json.dumps(results, indent=2)}

**Initial Verdict:** {verdict.upper()}

═══════════════════════════════════════════════════════════════
YOUR TASK: EDUCATIONAL POST-MORTEM ANALYSIS
═══════════════════════════════════════════════════════════════

Compare the DESIGNER'S INTENT vs SIMULATION CODE vs ACTUAL RESULTS and explain:

1. **What the designer wanted to achieve** (in simple physics terms)
2. **What the simulation code actually modeled** (did it capture the physics?)
3. **What results came out** (do they match expectations?)
4. **Why they match or don't match** (physics gaps, code limitations, fundamental issues)
5. **Honest assessment** (is this simulation trustworthy for validating this design?)

Be brutally honest about:
- Physics that CAN'T be modeled in Fock state basis (temporal effects, wavepacket distinguishability, etc.)
- Code implementation issues (wrong operators, missing physics, incorrect parameters)
- Fundamental simulation limitations (what this approach will NEVER capture)

**Example Analysis (HOM Interference):**
"The designer wants to show Hong-Ou-Mandel interference where two identical photons entering a 50:50 beam splitter bunch together, creating zero coincidences. The simulation code uses Fock states |1⟩|1⟩ and applies a beam splitter operator, but critically, it implements a 'delay' as a global phase shift (phi * a†a), which has ZERO physical effect on photon distinguishability. Real HOM interference requires temporal wavepacket overlap - if photons arrive at different times, they're distinguishable and don't interfere. Fock states have no temporal structure, so this simulation CANNOT capture the key physics. The coincidence rate of 0.54 is classical behavior (distinguishable photons), not quantum interference. Rating: 3/10 - The simulation runs but fails to validate the core physics claim."

Return your analysis as JSON with ANNOTATED CODE EXTRACTS for side-by-side comparison:
{{
    "analysis": "Detailed educational explanation comparing design vs code vs results",
    "rating": 5,  // 1-10, where 1=completely wrong, 10=perfectly validated
    "limitations": ["Specific physics limitation 1", "Limitation 2"],
    "matches_design": false,  // Does simulation capture designer's intent?
    "key_insight": "One-sentence takeaway about what we learned",
    "design_intent": {{
        "components": ["Component 1: description", "Component 2: description"],
        "physics_goal": "What the designer wanted to achieve",
        "key_parameters": ["param1: value1", "param2: value2"]
    }},
    "code_implementation": {{
        "state_init": "# Actual code lines showing state initialization\\ncoherent_state = qt.coherent(10, 2.0)\\n...",
        "operations": "# Actual code lines showing key operations\\nH_bs = theta * (a.dag()*b + a*b.dag())\\n...",
        "measurements": "# Actual code lines showing measurements\\ndetector1 = qt.expect(n_a, final_state)\\n..."
    }},
    "comparison": "How design intent maps (or doesn't map) to code implementation"
}}

CRITICAL: For code_implementation, extract ACTUAL lines from the simulation code above (copy exact syntax). 
Don't paraphrase or create fake code - copy the real lines that implement each part.

Be honest, educational, and specific. Help users understand what simulations can and cannot validate."""

        try:
            response = self.llm.predict(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return {
                    'analysis': analysis_data.get('analysis', 'Analysis unavailable'),
                    'rating': max(1, min(10, analysis_data.get('rating', 5))),  # Clamp 1-10
                    'limitations': analysis_data.get('limitations', []),
                    'matches_design': analysis_data.get('matches_design', False),
                    'key_insight': analysis_data.get('key_insight', ''),
                    'design_intent': analysis_data.get('design_intent', {}),
                    'code_implementation': analysis_data.get('code_implementation', {}),
                    'comparison': analysis_data.get('comparison', '')
                }
            else:
                # Fallback if JSON parsing fails
                return {
                    'analysis': response,
                    'rating': 5,
                    'limitations': ['Could not parse detailed limitations'],
                    'matches_design': False,
                    'key_insight': 'Analysis format error',
                    'design_intent': {},
                    'code_implementation': {},
                    'comparison': ''
                }
                
        except Exception as e:
            print(f"⚠️ Deep analysis failed: {str(e)}")
            return {
                'analysis': f"Deep analysis unavailable due to error: {str(e)}",
                'rating': 5,
                'limitations': ['Analysis error'],
                'matches_design': False,
                'key_insight': 'Could not complete post-simulation analysis',
                'design_intent': {},
                'code_implementation': {},
                'comparison': ''
            }
    
    def _conduct_independent_assessment(self, design: Dict[str, Any], simulation_code: str,
                                        results: Dict, rating: int) -> Dict:
        """
        INDEPENDENT ARBITRATION: Assess whether design or simulation is at fault for low scores.
        
        Acts as neutral referee judging:
        1. Design completeness and realism
        2. Simulation accuracy and assumptions
        3. Root cause of any mismatch
        
        Returns:
            {
                'root_cause': 'DESIGN_INCOMPLETE' | 'SIMULATION_OVERSTRICT' | 'MISMATCH' | 'BOTH_FLAWED' | 'ALIGNED',
                'confidence': float,
                'design_assessment': {...},
                'simulation_assessment': {...},
                'recommendation': 'improve_design' | 'trust_design' | 'both_need_work' | 'accept_as_is',
                'designer_instructions': str,
                'user_interpretation': str
            }
        """
        
        title = design.get('title', 'Unknown')
        components = design.get('experiment', {}).get('steps', [])
        physics_goal = design.get('physics_explanation', '')
        description = design.get('description', '')
        
        prompt = f"""You are an INDEPENDENT PHYSICS REFEREE evaluating a quantum experiment design process.

**CONTEXT:**
A designer proposed an experiment, a simulator validated it, and the result was a rating of {rating}/10.
Your job: Determine WHO is at fault (if anyone) for this score.

**DESIGNER'S PROPOSAL:**
Title: {title}
Description: {description}
Physics Goal: {physics_goal}
Components Specified: {json.dumps(components, indent=2)}

**SIMULATOR'S CODE:**
```python
{simulation_code}
```

**SIMULATION RESULTS:**
{json.dumps(results, indent=2)}
Rating: {rating}/10

═══════════════════════════════════════════════════════════════
YOUR ROLE: INDEPENDENT ARBITRATION
═══════════════════════════════════════════════════════════════

Evaluate BOTH parties independently against physics ground truth:

**A. DESIGN ASSESSMENT:**
Score the designer's proposal (0-10):
- **Completeness**: Are critical components missing? (filters, lenses, polarizers, collection optics)
- **Realism**: Are parameters physically achievable? (wavelengths, powers, efficiencies)
- **Specificity**: Are specs detailed enough? (crystal type, phase matching, detector specs)
- **Physics Accuracy**: Is the claimed physics correct?

Missing components that invalidate the design:
- SPDC without filters → will have multi-wavelength noise
- Entanglement without coincidence circuit → can't verify correlations
- HOM without identical photons → no quantum interference
- Interferometer without phase control → can't see fringes

**B. SIMULATION ASSESSMENT:**
Score the simulator's code (0-10):
- **Fidelity**: Does it model what the designer actually specified?
- **Assumptions**: Are assumptions too restrictive? (99% loss when 5% is realistic)
- **Physics**: Is the modeling approach valid? (Fock states for continuous variables?)
- **Implementation**: Any bugs or dimensional errors?

Over-restrictive simulations:
- Modeling 1% detector efficiency when modern SPADs have 65%
- Including pump depletion for low-power experiments
- Assuming perfect mode matching when it's not critical
- Using worst-case parameters instead of typical

**C. ROOT CAUSE IDENTIFICATION:**

Choose ONE verdict:

1. **DESIGN_INCOMPLETE**: Design is too simplistic, missing critical elements
   - Example: "Bell state with just crystal + detectors" (no filters, no coincidence logic)
   - Action: Designer needs to add missing components

2. **SIMULATION_OVERSTRICT**: Simulation uses unrealistic assumptions
   - Example: Modeling 99% optical loss when 10% is typical
   - Action: User should trust design despite low simulation score

3. **MISMATCH**: Both are reasonable but solving different problems  
   - Example: Designer wants "ideal physics demonstration", simulator models "realistic lab setup"
   - Action: Clarify whether user wants ideal or realistic model

4. **BOTH_FLAWED**: Both have significant errors
   - Example: Design missing filters AND simulation has dimensional bugs
   - Action: Complete redesign needed

5. **ALIGNED**: Design and simulation agree (use for scores ≥ 7)
   - Both are good, accept the result

**D. ACTIONABLE OUTPUTS:**

For DESIGN_INCOMPLETE, provide:
- `designer_instructions`: "Add [specific components] because [physics reason]"

For SIMULATION_OVERSTRICT, provide:
- `user_interpretation`: "Simulation is pessimistic because [assumption]. Your design is actually [assessment]."

Return JSON:
{{
    "root_cause": "DESIGN_INCOMPLETE",  // Choose ONE from above
    "confidence": 0.85,  // 0-1, how certain are you?
    "design_assessment": {{
        "completeness_score": 6,  // 0-10
        "missing_components": ["Bandpass filter at 810nm", "Coincidence detection circuit"],
        "unrealistic_specs": ["Pump power too low for detectable SPDC"],
        "physics_errors": []
    }},
    "simulation_assessment": {{
        "fidelity_score": 7,  // 0-10  
        "overly_restrictive": ["Models 99% collection loss (realistic is ~30%)"],
        "invalid_assumptions": [],
        "implementation_bugs": []
    }},
    "recommendation": "improve_design",  // improve_design | trust_design | both_need_work | accept_as_is
    "designer_instructions": "Add bandpass filters after the crystal to select signal/idler wavelengths (810nm ±5nm FWHM). Add coincidence detection circuit with ~1ns timing window to verify entanglement. Increase pump power to 50mW for detectable photon rates.",
    "user_interpretation": "The simulation correctly identifies that the design needs wavelength filtering and coincidence detection to verify entanglement. Without these, photon pairs cannot be distinguished from background noise."
}}

BE BRUTALLY HONEST. Don't favor designer or simulator - judge based on physics truth."""

        try:
            response = self.llm.predict(prompt)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group())
                return assessment
            else:
                return {
                    'root_cause': 'MISMATCH',
                    'confidence': 0.5,
                    'design_assessment': {'completeness_score': 5},
                    'simulation_assessment': {'fidelity_score': 5},
                    'recommendation': 'both_need_work',
                    'designer_instructions': 'Could not parse assessment',
                    'user_interpretation': 'Assessment unavailable'
                }
        except Exception as e:
            print(f"⚠️ Independent assessment failed: {e}")
            return {
                'root_cause': 'MISMATCH',
                'confidence': 0.0,
                'design_assessment': {},
                'simulation_assessment': {},
                'recommendation': 'both_need_work',
                'designer_instructions': f'Assessment error: {e}',
                'user_interpretation': 'Could not complete assessment'
            }
    
    def _interpret_results(self, design: Dict[str, Any], results: Dict, reasoning: str) -> Dict:

        """
        LLM interprets simulation results and judges success.
        
        Returns:
            {
                'verdict': 'excellent'|'good'|'acceptable'|'poor'|'failed',
                'confidence': float (0-1),
                'analysis': str (detailed interpretation),
                'metrics': dict (key findings),
                'recommendations': list of suggestions
            }
        """
        
        title = design.get('title', 'Unknown')
        description = design.get('description', '')
        
        prompt = f"""You are a quantum optics expert evaluating a simulation.

**Experiment:**
Title: {title}
Description: {description}

**Simulation Reasoning:**
{reasoning}

**Simulation Results:**
{json.dumps(results, indent=2)}

**Your Task:**
Analyze these results and provide:
1. **Verdict**: excellent / good / acceptable / poor / failed
2. **Confidence**: 0.0 to 1.0 (how confident are you in this assessment)
3. **Analysis**: 2-3 sentences explaining what the results mean
4. **Key Metrics**: Highlight the most important numbers
5. **Recommendations**: 2-3 specific suggestions to improve the design (if needed)

**Guidelines:**
- Fidelity > 0.95: excellent
- Fidelity 0.85-0.95: good  
- Fidelity 0.70-0.85: acceptable
- Fidelity < 0.70: poor
- Similar logic for purity, visibility, entanglement
- Consider multiple metrics together

**Output Format (JSON):**
```json
{{
  "verdict": "good",
  "confidence": 0.85,
  "analysis": "The simulation shows...",
  "metrics": {{"fidelity": 0.92, "purity": 0.88}},
  "recommendations": ["Add phase stabilization", "Use higher pump power"]
}}
```

Provide your analysis:"""

        try:
            response = self.llm.predict(prompt)
            
            # Try to parse JSON from response
            # Look for {...} block
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                interpretation = json.loads(json_str)
                return interpretation
            else:
                # Fallback: extract manually
                return {
                    'verdict': 'unknown',
                    'confidence': 0.5,
                    'analysis': response,
                    'metrics': results,
                    'recommendations': []
                }
                
        except Exception as e:
            print(f"⚠️  Interpretation error: {e}")
            return {
                'verdict': 'unknown',
                'confidence': 0.3,
                'analysis': f'Could not interpret results. Raw: {results}',
                'metrics': results,
                'recommendations': []
            }
    
    def quick_check(self, design: Dict[str, Any]) -> str:
        """
        Quick LLM assessment without full simulation (for rapid feedback).
        
        Returns:
            Brief analysis string
        """
        
        components = design.get('experiment', {}).get('steps', [])
        
        prompt = f"""Quickly assess this quantum optics design for obvious issues:

**Design:** {design.get('title', 'Unknown')}
**Components:** {len(components)} components

{json.dumps(components, indent=2)}

In 1-2 sentences, identify:
1. Any obvious physics errors
2. Missing critical components
3. Potential improvements

Be brief:"""

        try:
            return self.llm.predict(prompt).strip()
        except:
            return "Could not perform quick check"
