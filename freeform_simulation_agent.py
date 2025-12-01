"""
Free-Form Simulation Agent - Physics-Aware Code Generation

Unlike the QuTiP-constrained simulation agent, this agent:
1. Chooses the appropriate physics formalism for each experiment
2. Can use temporal wavepackets, continuous variables, atomic physics
3. Has full freedom to use any scientific Python library
4. Learns from previous successful simulations

Based on analysis of 19 experiments, we identified:
- Fock states work for: discrete photonics, interferometry, polarization
- Temporal wavepackets needed for: HOM, time-bin, photon distinguishability
- Continuous variables needed for: squeezed light, CV teleportation, homodyne
- Atomic physics needed for: EIT, multilevel systems
"""

import json
import re
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import tempfile
import sys

class FreeFormSimulationAgent:
    """
    LLM-driven simulation with full freedom to choose physics formalism.
    Learns from successful simulations and guides towards appropriate methods.
    """
    
    def __init__(self, llm_client, simulation_toolbox_path: str = "./toolbox/simulation_toolbox.json"):
        """
        Args:
            llm_client: LLM client for code generation
            simulation_toolbox_path: Path to learned simulation patterns
        """
        self.llm = llm_client
        self.toolbox_path = Path(simulation_toolbox_path)
        self.toolbox = self._load_simulation_toolbox()
        
        # Initialize embedding retriever for semantic search
        try:
            from embedding_retriever import EmbeddingRetriever
            self.retriever = EmbeddingRetriever()
            print("✅ Simulation agent: Embedding retriever initialized")
        except Exception as e:
            print(f"⚠️  Simulation agent: Could not initialize retriever: {e}")
            self.retriever = None
        
    def _load_simulation_toolbox(self) -> Dict:
        """Load previously successful simulation approaches."""
        try:
            if self.toolbox_path.exists():
                with open(self.toolbox_path, 'r') as f:
                    return json.load(f)
            else:
                # Create empty toolbox
                default_toolbox = {
                    "successful_simulations": {},
                    "_description": "Successful simulation approaches for reuse",
                    "_categories": {
                        "discrete_photonic": "Fock states, photon counting",
                        "temporal": "Wavepacket propagation, timing",
                        "continuous_variable": "Quadratures, Wigner functions",
                        "atomic": "Density matrices, master equations"
                    }
                }
                self.toolbox_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.toolbox_path, 'w') as f:
                    json.dump(default_toolbox, f, indent=2)
                return default_toolbox
        except Exception as e:
            print(f"⚠️  Could not load simulation toolbox: {e}")
            return {"successful_simulations": {}}
    
    def validate_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and execute simulation code with iterative refinement.
        
        Args:
            design: Experiment design from LLMDesigner
            
        Returns:
            Dict with simulation results including code, outputs, and analysis
        """
        print(f"\n🔬 Free-Form Simulation: {design.get('title', 'Experiment')}")
        
        try:
            return self._run_convergent_refinement(design)
            
        except Exception as e:
            print(f"❌ Free-form simulation failed: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'valid': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _run_convergent_refinement(self, design: Dict) -> Dict:
        """
        Iterative convergence loop: Refine simulation until it faithfully models design.
        Each iteration builds on previous, not independent attempts.
        """
        print("\n" + "="*80)
        print("🔬 FREE-FORM SIMULATION VALIDATION (Convergent Refinement)")
        print("="*80)
        print("Goal: Converge simulation to faithfully model designer's intent\n")
        
        max_iterations = 3  # Limit to 3 iterations for cost control
        
        # State tracking
        current_code = None
        refinement_history = []
        converged = False
        
        # Track best working version in case refinement makes things worse
        best_working_code = None
        best_working_results = None
        best_working_analysis = None
        best_working_alignment = None
        best_alignment_score = 0
        best_iteration = 0
        
        # Track cumulative token usage across all iterations
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n{'='*80}")
            print(f"🔄 ITERATION {iteration}/{max_iterations}")
            print(f"{'='*80}\n")
            
            iteration_log = {'iteration': iteration}
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 1: CODE GENERATION/REFINEMENT
            # ═══════════════════════════════════════════════════════════════
            if iteration == 1:
                print("📝 PHASE 1: Generating initial simulation code from design...")
                current_code = self._generate_simulation_code(design)
                iteration_log['phase'] = 'initial_generation'
            else:
                print(f"🔧 PHASE 1: Refining code based on feedback...")
                last_feedback = refinement_history[-1].get('feedback', {})
                current_code = self._refine_simulation_code(
                    design=design,
                    current_code=current_code,
                    feedback=last_feedback
                )
                iteration_log['phase'] = 'refinement'
                iteration_log['feedback_addressed'] = last_feedback.get('instruction', '')
            
            # Track token usage from code generation/refinement
            if hasattr(self.llm, 'last_usage'):
                usage = self.llm.last_usage
                total_prompt_tokens += usage.get('prompt_tokens', 0)
                total_completion_tokens += usage.get('completion_tokens', 0)
                total_cost += usage.get('cost', 0.0)
            
            if not current_code:
                print(f"❌ FAILED: Could not generate/refine code")
                iteration_log['failed_at'] = 'generation'
                refinement_history.append(iteration_log)
                if iteration == 1:
                    return self._create_failure_result(
                        "Initial code generation failed", 
                        refinement_history
                    )
                else:
                    print("⚠️  Using code from previous iteration")
                    break
            
            print(f"✅ Code ready: {len(current_code)} chars\n")
            iteration_log['code'] = current_code
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 2: PRE-EXECUTION REVIEW (Design Alignment)
            # ═══════════════════════════════════════════════════════════════
            print("🔍 PHASE 2: PRE-EXECUTION REVIEW")
            print("   Question: Does this code correctly model the design?\n")
            
            code_review = self._review_code_before_execution(design, current_code)
            iteration_log['pre_review'] = code_review
            
            # Track token usage from pre-review
            if hasattr(self.llm, 'last_usage'):
                usage = self.llm.last_usage
                total_prompt_tokens += usage.get('prompt_tokens', 0)
                total_completion_tokens += usage.get('completion_tokens', 0)
                total_cost += usage.get('cost', 0.0)
            
            if not code_review.get('approved', False):
                confidence = code_review.get('confidence', 0)
                print(f"❌ REVIEW REJECTED (confidence: {confidence:.1%})")
                print(f"   Reason: {code_review.get('reason', 'Unknown')}")
                
                missing = code_review.get('missing_elements', [])
                if missing:
                    print(f"   Missing: {', '.join(missing)}")
                
                concerns = code_review.get('concerns', [])
                if concerns:
                    print(f"   Concerns: {', '.join(concerns)}")
                
                # Build specific refinement instructions inline
                instruction = f"CODE DOES NOT MODEL DESIGN CORRECTLY.\n\n"
                instruction += f"Problem: {code_review.get('reason', '')}\n\n"
                
                if missing:
                    instruction += "MISSING ELEMENTS (must add):\n"
                    for elem in missing:
                        instruction += f"- {elem}\n"
                
                if concerns:
                    instruction += "\nCONCERNS (must address):\n"
                    for concern in concerns:
                        instruction += f"- {concern}\n"
                
                instruction += "\nFix: Add missing components and address concerns. Keep existing correct code."
                
                feedback = {
                    'stage': 'pre_review',
                    'issue_type': 'design_mismatch',
                    'missing_elements': missing,
                    'concerns': concerns,
                    'reason': code_review.get('reason', ''),
                    'instruction': instruction
                }
                
                iteration_log['feedback'] = feedback
                iteration_log['outcome'] = 'needs_refinement'
                refinement_history.append(iteration_log)
                print(f"\n→ Will refine in iteration {iteration + 1}\n")
                continue
            
            print(f"✅ REVIEW APPROVED (confidence: {code_review.get('confidence', 0):.1%})")
            print("   Code correctly models design\n")
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 3: EXECUTION
            # ═══════════════════════════════════════════════════════════════
            print("⚙️  PHASE 3: EXECUTING SIMULATION\n")
            
            results = self._execute_simulation(current_code, design)
            iteration_log['execution'] = results
            
            if not results.get('success', False):
                print(f"❌ EXECUTION ERROR")
                print(f"   Error: {results.get('error', 'Unknown')}")
                stderr = results.get('stderr', '')
                if stderr:
                    print(f"   Stderr: {stderr[:200]}...")
                
                # Build refinement instructions for bug fix inline
                instruction = f"RUNTIME ERROR - CODE WON'T EXECUTE.\n\n"
                instruction += f"Error: {results.get('error', '')}\n"
                if stderr:
                    instruction += f"Stderr: {stderr[:300]}\n"
                instruction += "\nFix: Correct the bug. Don't change physics model, just fix syntax/imports/logic errors."
                
                feedback = {
                    'stage': 'execution',
                    'issue_type': 'runtime_error',
                    'error': results.get('error', ''),
                    'stderr': stderr,
                    'instruction': instruction
                }
                
                iteration_log['feedback'] = feedback
                iteration_log['outcome'] = 'needs_bug_fix'
                refinement_history.append(iteration_log)
                print(f"\n→ Will fix bugs in iteration {iteration + 1}\n")
                continue
            
            print(f"✅ EXECUTION SUCCESSFUL\n")
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 4: POST-EXECUTION ANALYSIS & ALIGNMENT CHECK
            # ═══════════════════════════════════════════════════════════════
            print("📊 PHASE 4: ANALYZING RESULTS\n")
            
            # Analyze physics correctness
            analysis = self._analyze_results(design, current_code, results)
            iteration_log['analysis'] = analysis
            
            # Track token usage from analysis
            if hasattr(self.llm, 'last_usage'):
                usage = self.llm.last_usage
                total_prompt_tokens += usage.get('prompt_tokens', 0)
                total_completion_tokens += usage.get('completion_tokens', 0)
                total_cost += usage.get('cost', 0.0)
            
            # Check if simulation output aligns with design intent
            alignment = self._check_design_alignment(design, current_code, results, analysis)
            iteration_log['alignment'] = alignment
            
            # Track token usage from alignment check
            if hasattr(self.llm, 'last_usage'):
                usage = self.llm.last_usage
                total_prompt_tokens += usage.get('prompt_tokens', 0)
                total_completion_tokens += usage.get('completion_tokens', 0)
                total_cost += usage.get('cost', 0.0)
            
            print(f"   Physics correctness: {analysis.get('rating', 0)}/10")
            print(f"   Design alignment: {alignment.get('alignment_score', 0)}/10")
            
            # Use Phase 4 analysis rating as the final quality rating
            final_rating = analysis.get('rating', 0)
            
            # Check convergence criteria
            alignment_score = alignment.get('alignment_score', 0)
            actually_models_design = alignment.get('actually_models_design', False)
            
            # Update best working version if this is better
            if actually_models_design and alignment_score > best_alignment_score:
                best_working_code = current_code
                best_working_results = results
                best_working_analysis = analysis
                best_working_alignment = alignment
                best_alignment_score = alignment_score
                best_iteration = iteration
                print(f"   📌 New best: alignment={alignment_score}/10 (iteration {iteration})")
            
            print(f"\n🎯 CONVERGENCE CHECK:")
            print(f"   ✓ Simulation faithfully models design: {actually_models_design}")
            print(f"   ✓ Alignment score: {alignment_score}/10")
            print(f"   ✓ Quality rating: {final_rating}/10")
            
            # PRIMARY CONVERGENCE: Does simulation model the design?
            # Accept if alignment >= 6 OR if it models design correctly (to avoid breaking working code)
            if actually_models_design and alignment_score >= 6:
                print(f"\n{'='*80}")
                print("✅ CONVERGED: Simulation faithfully models design")
                print(f"{'='*80}\n")
                
                # Check if quality is also good
                if final_rating >= 6:
                    print("✅ Quality is also good!")
                else:
                    print(f"⚠️  Note: Quality rating is {final_rating}/10")
                    print("    This reflects limitations of the design itself, not the simulation.")
                    print("    Simulation correctly models what was designed.")
                
                converged = True
                iteration_log['outcome'] = 'converged_faithful'
                refinement_history.append(iteration_log)
                
                # Return successful result
                return {
                    'valid': True,
                    'rating': final_rating,
                    'confidence': 'high',  # High confidence when aligned
                    'code': current_code,
                    'results': results,
                    'analysis': {
                        **analysis,
                        'alignment_check': alignment
                    },
                    'convergence_info': {
                        'iterations': iteration,
                        'converged': True,
                        'faithful': True,
                        'final_alignment': alignment_score,
                        'refinement_history': refinement_history,
                        'note': 'Simulation faithfully models design' if final_rating >= 6 else 'Simulation faithful but design has limitations',
                        'total_prompt_tokens': total_prompt_tokens,
                        'total_completion_tokens': total_completion_tokens,
                        'total_tokens': total_prompt_tokens + total_completion_tokens,
                        'total_cost': total_cost
                    }
                }
            
            # Not converged - alignment issues remain
            if alignment_score < 6 or not actually_models_design:
                print(f"\n⚠️  NOT CONVERGED: Simulation doesn't match design")
                
                # SAFETY: If this is iteration 2+ and we had a working version before, keep best
                if iteration > 1 and best_working_code is not None:
                    print(f"⚠️  WARNING: Refinement not improving. Keeping best working version from iteration {best_iteration}")
                    print(f"→ Best had alignment={best_alignment_score}/10, current has {alignment_score}/10")
                
                # Use analysis recommendations directly for refinement
                refinement_instructions = analysis.get('refinement_instructions', '')
                if not refinement_instructions:
                    # Build from alignment + recommendations if not provided
                    refinement_instructions = "CODE EXECUTES BUT OUTPUT DOESN'T MATCH DESIGN.\n\n"
                    missing = alignment.get('missing_from_code', [])
                    wrong = alignment.get('wrong_in_code', [])
                    
                    if missing:
                        refinement_instructions += "MISSING FROM CODE:\n"
                        for elem in missing:
                            refinement_instructions += f"- {elem}\n"
                    
                    if wrong:
                        refinement_instructions += "\nWRONG IN CODE:\n"
                        for elem in wrong:
                            refinement_instructions += f"- {elem}\n"
                    
                    # Add recommendations from analysis
                    recommendations = analysis.get('recommendations', [])
                    if recommendations:
                        refinement_instructions += "\nRECOMMENDATIONS:\n"
                        for rec in recommendations:
                            refinement_instructions += f"- {rec}\n"
                
                # Build refinement feedback
                feedback = {
                    'stage': 'post_execution',
                    'issue_type': 'alignment_mismatch',
                    'alignment_score': alignment_score,
                    'missing_from_code': alignment.get('missing_from_code', []),
                    'wrong_in_code': alignment.get('wrong_in_code', []),
                    'instruction': refinement_instructions
                }
                
                iteration_log['feedback'] = feedback
                iteration_log['outcome'] = 'needs_alignment_improvement'
                refinement_history.append(iteration_log)
                print(f"\n→ Will improve alignment in iteration {iteration + 1}\n")
                continue
            
            # If we get here, something unexpected happened
            print(f"\n⚠️  Unexpected state - accepting result")
            iteration_log['outcome'] = 'accepted_edge_case'
            refinement_history.append(iteration_log)
            break
        
        # ═══════════════════════════════════════════════════════════════
        # MAX ITERATIONS REACHED - RETURN BEST RESULT
        # ═══════════════════════════════════════════════════════════════
        if not converged:
            print(f"\n{'='*80}")
            print(f"⚠️  MAX ITERATIONS REACHED ({max_iterations}) - DID NOT CONVERGE")
            print(f"{'='*80}\n")
            
            # If we have a working version, use it instead of the last (possibly broken) iteration
            if best_working_code is not None:
                print(f"✅ Returning best working version from iteration {best_iteration}")
                print(f"   Alignment: {best_alignment_score}/10")
                print(f"   (Note: Later iterations did not improve upon this)\n")
                
                return {
                    'valid': True,  # We have a working version
                    'rating': best_working_analysis.get('rating', 5),
                    'confidence': 'medium',
                    'code': best_working_code,
                    'results': best_working_results,
                    'analysis': {
                        **best_working_analysis,
                        'alignment_check': best_working_alignment
                    },
                    'convergence_info': {
                        'iterations': max_iterations,
                        'converged': False,
                        'best_iteration': best_iteration,
                        'final_alignment': best_alignment_score,
                        'reason': 'max_iterations_but_found_working_version',
                        'refinement_history': refinement_history,
                        'note': f'Used iteration {best_iteration} result (later iterations broke or did not improve)',
                        'total_prompt_tokens': total_prompt_tokens,
                        'total_completion_tokens': total_completion_tokens,
                        'total_tokens': total_prompt_tokens + total_completion_tokens,
                        'total_cost': total_cost
                    }
                }
            
            # No working version at all - return last attempt
            print("⚠️  No successful iterations found. Returning last attempt.\n")
            
            # Use last iteration's results
            last_iter = refinement_history[-1] if refinement_history else {}
            
            return {
                'valid': False,  # Did not converge
                'rating': last_iter.get('reflection', {}).get('final_rating', 3),
                'confidence': 'low',
                'code': current_code,
                'results': last_iter.get('execution', {}),
                'analysis': {
                    **last_iter.get('analysis', {}),
                    'alignment_check': last_iter.get('alignment', {}),
                    'self_reflection': last_iter.get('reflection', {})
                },
                'convergence_info': {
                    'iterations': max_iterations,
                    'converged': False,
                    'reason': 'max_iterations_reached_no_working_version',
                    'refinement_history': refinement_history,
                    'total_prompt_tokens': total_prompt_tokens,
                    'total_completion_tokens': total_completion_tokens,
                    'total_tokens': total_prompt_tokens + total_completion_tokens,
                    'total_cost': total_cost
                }
            }
        
        # Fallback
        return self._create_failure_result("Unknown error", refinement_history)
    
    def _classify_experiment_physics(self, design: Dict[str, Any]) -> str:
        """Use LLM to classify the dominant physics domain for appropriate simulation approach."""
        
        title = design.get('title', '')
        description = design.get('description', '')
        physics_explanation = design.get('physics_explanation', '')
        
        prompt = f"""What type of quantum physics does this experiment primarily involve?

**Experiment:** {title}
**Description:** {description}
**Physics:** {physics_explanation}

Analyze what physical quantities are most important to model accurately:

**discrete_photonic** - Discrete photon number states and interference
- Key: Photon counting statistics, coincidences, polarization
- When: Clear photon number states matter (single photons, pairs, n-photon inputs)

**temporal** - Time-dependent wavefunctions and distinguishability  
- Key: Photon arrival times, temporal overlap, pulse shapes
- When: Timing/delays crucial, distinguishability from temporal structure

**continuous_variable** - Continuous amplitude/phase, quadrature measurements
- Key: Quadratures X and P, phase space, homodyne detection
- When: Squeezed states, EPR correlations, continuous observables

**atomic** - Atomic level structure and coherence
- Key: Energy levels, populations, Rabi dynamics, decoherence
- When: Atoms, ions, vapor cells, multilevel transitions

**hybrid** - Multiple domains needed
- When: Experiment fundamentally requires multiple formalisms

Think about: What measurements are made? What quantities determine the outcome?

**Response format (JSON only):**
```json
{{
  "category": "discrete_photonic|temporal|continuous_variable|atomic|hybrid",
  "reasoning": "Brief justification",
  "key_observable": "What physical quantity matters most"
}}
```

Respond with JSON only."""

        try:
            response = self.llm.predict(prompt).strip()
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                classification = json.loads(json_match.group(0))
                return classification.get('category', 'discrete_photonic')
            else:
                print(f"⚠️  Could not parse classification, defaulting to discrete_photonic")
                return 'discrete_photonic'
        except Exception as e:
            print(f"⚠️  Classification failed: {e}, defaulting to discrete_photonic")
            return 'discrete_photonic'
    
    def _generate_simulation_code(
        self, 
        design: Dict[str, Any], 
        previous_error: Optional[Dict[str, Any]] = None,
        attempt_number: int = 1
    ) -> Optional[str]:
        """Generate physics-appropriate Python simulation code with error feedback."""
        
        # Get relevant examples from toolbox using semantic search
        query = f"{design.get('title', '')} {design.get('description', '')}"
        toolbox_examples = self._get_similar_toolbox_examples(query)
        
        title = design.get('title', 'Experiment')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        components = design.get('experiment', {}).get('steps', design.get('components', []))
        
        # Build error feedback section
        error_feedback = ""
        if previous_error and attempt_number > 1:
            error_type = previous_error.get('type', 'unknown')
            if error_type == 'execution_error':
                stderr = previous_error.get('stderr', '')
                error_feedback = f"""
**PREVIOUS ATTEMPT FAILED - FIX THESE ERRORS:**

Execution error occurred:
```
{stderr}
```

Common fixes:
- Check import statements (qutip, numpy, scipy, matplotlib)
- Verify all variables are defined before use
- Fix syntax errors, indentation, undefined functions
- Check array/tensor dimensions match
- Use try-except for numerical stability issues
"""
            elif error_type == 'low_quality':
                rating = previous_error.get('rating', 0)
                issues = previous_error.get('issues', [])
                feedback = previous_error.get('feedback', [])
                error_feedback = f"""
**PREVIOUS ATTEMPT LOW QUALITY (Rating: {rating}/10) - IMPROVE:**

Issues identified:
{chr(10).join([f"- {issue}" for issue in issues])}

Improvement suggestions:
{chr(10).join([f"- {item}" for item in feedback])}

Focus on:
- More accurate physics modeling
- Better parameter choices
- Clearer output format
- Realistic figures of merit
"""
        
        prompt = f"""Generate complete, executable Python code to simulate this quantum experiment.
{f'(Attempt {attempt_number} - addressing previous issues)' if attempt_number > 1 else ''}

**Experiment:** {title}
**Description:** {description}
**Physics:** {physics}

**Components:**
{json.dumps(components, indent=2)}

{error_feedback}

{toolbox_examples}

**YOUR TASK:**

Write Python code that accurately simulates the quantum physics described in this experiment. 

**CORE PRINCIPLE: MODEL THE ACTUAL PHYSICS**

Read the experiment description carefully. What physical process is happening? What measurements are being made? Your simulation must model THAT, not some textbook template.

**Available Tools (use whatever works):**
- **NumPy/SciPy**: Arrays, linear algebra, numerical integration, FFTs, signal processing
- **QuTiP**: Quantum operators (creation/annihilation, Pauli matrices, tensor products, time evolution)
- **Custom implementations**: Build operators from scratch if needed (beam splitters, phase shifts, Hamiltonians)

Don't restrict yourself to one library. Use the right tool for the physics:
- Temporal overlap integrals? → NumPy arrays and integration
- Fock state interference? → QuTiP quantum objects
- Wigner functions? → Grid-based calculation with NumPy
- Master equations? → QuTiP mesolve or manual integration
- Classical fields? → NumPy complex arrays

**PHYSICAL CONSTRAINTS (Reality Check):**

Your results must be physically realistic. Here are typical laboratory values:

- **Wavelengths**: 200-2000 nm (UV to near-IR). Common: 405, 532, 780, 810, 1550 nm
- **Photon numbers**: Single photon ~1, weak coherent ~10-100, laser ~10^12-10^18 photons/pulse
- **Squeezing**: 3-10 dB achievable, world record ~15 dB. NOT 68 dB (impossible)
- **Local oscillator**: 10^6-10^9 photons minimum for homodyne (strong classical field)
- **Timescales**: Ultrafast ~fs, single photon coherence ~ps, detector response ~ns
- **Visibility/Fidelity**: Bounded between 0 and 1. V>1 or F>1 means bug
- **Efficiencies**: Detectors 20-95%, transmission 50-99%, never assume 100% unless stated

**MATHEMATICAL CONSISTENCY (Debug Checks):**

- States normalized: `np.abs(np.vdg(psi) @ psi) ≈ 1` or `np.trace(rho) ≈ 1`
- Probabilities sum to 1: `np.sum(prob_array) ≈ 1`
- Unitarity: `U @ U.conj().T ≈ Identity` for closed evolution
- Hermiticity: `H == H.conj().T` for observables
- Energy/photon conservation (unless there's explicit pumping/loss)
- Dimensions match: Can't add 2x2 matrix to 3x3 matrix

**COMMON MISTAKES TO AVOID:**

1. **Wrong Bell states**: |Φ+⟩=(|HH⟩+|VV⟩)/√2, |Ψ-⟩=(|HV⟩-|VH⟩)/√2 [check signs]
2. **Tensor product errors**: For N-mode system, all operators must be NxN dimensional
3. **Arbitrary rescaling**: If result is 10^-12 and you multiply by 10^12, why? Find the physics error
4. **Ignoring temporal structure**: Can't model time-dependent physics with static Fock states
5. **Wrong measurement basis**: Homodyne measures quadratures, not photon number

**WHAT TO CALCULATE:**

Look at the experiment description. What does it claim to demonstrate?

- "visibility" → Calculate V = (I_max - I_min)/(I_max + I_min)
- "fidelity" → Calculate F = |⟨ψ_target|ψ_actual⟩|²
- "entanglement" → Calculate concurrence, negativity, or witness value  
- "squeezing" → Calculate ΔX²/ΔX²_vacuum (in dB: 10*log10)
- "coincidences" → Calculate joint detection probability
- Custom metrics? Calculate them properly

Print intermediate values so we can verify the physics is correct.

**CODE REQUIREMENTS:**

```python
# 1. Import what you need
import numpy as np
from scipy import ...  # if needed
import qutip as qt     # if needed

# 2. Extract physical parameters from experiment design
# wavelength, power, timescales, component specs

# 3. Model the quantum state/field appropriately
# Could be: Fock states, wavefunctions, density matrices, 
# classical fields, phase space distributions, etc.

# 4. Apply the physics
# Evolution, operations, interactions - model what actually happens

# 5. Perform the measurement
# Simulate what the detectors see

# 6. Calculate figures of merit
# Whatever the experiment claims to measure

# 7. Print results with labels and units
print("Visibility:", visibility)
print("Fidelity:", fidelity)
# Include warnings about approximations
```

**OUTPUT FORMAT:**
Return ONLY executable Python code. No markdown, no ``` blocks, no explanations.
Code must be self-contained and print results clearly to stdout.

**IMPORTANT:** Generate the COMPLETE simulation from start to finish:
- All imports at the top
- Define all parameters and states  
- Implement ALL operations and measurements
- Calculate ALL figures of merit
- Print ALL results with clear labels
Do NOT truncate or abbreviate. Write the full working simulation.

Generate the simulation code:"""

        try:
            response = self.llm.predict(prompt).strip()
            
            # Extract Python code from markdown if present
            code_match = re.search(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            else:
                # Assume entire response is code
                code = response
            
            # Basic validation
            if 'import' not in code or 'print' not in code:
                print(f"⚠️  Generated code seems incomplete")
                return None
            
            return code
            
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
            traceback.print_exc()
            return None
    
    def _execute_simulation(self, code: str, design: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generated Python code and capture output + plots."""
        
        try:
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Modify code to save all matplotlib figures
                modified_code = f"""import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import os

# Override plt.show() to save figures instead
_original_show = plt.show
_figure_counter = [0]
_output_dir = r'{tmpdir_path}'

def _custom_show(*args, **kwargs):
    for fignum in plt.get_fignums():
        fig = plt.figure(fignum)
        _figure_counter[0] += 1
        filepath = os.path.join(_output_dir, f'figure_{{_figure_counter[0]:02d}}.png')
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f'[FIGURE_SAVED: {{filepath}}]')
    plt.close('all')

plt.show = _custom_show

# Original simulation code
{code}

# Save any remaining figures
if plt.get_fignums():
    _custom_show()
"""
                
                # Write modified code to temp file
                code_file = tmpdir_path / 'simulation.py'
                code_file.write_text(modified_code)
                
                # Set environment to suppress tokenizer warning
                import os
                env = os.environ.copy()
                env['TOKENIZERS_PARALLELISM'] = 'false'
                
                # Execute with timeout
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(tmpdir_path),
                    env=env
                )
                
                # Collect generated figures
                figures = []
                for fig_file in sorted(tmpdir_path.glob('figure_*.png')):
                    with open(fig_file, 'rb') as f:
                        import base64
                        fig_data = base64.b64encode(f.read()).decode('utf-8')
                        figures.append({
                            'filename': fig_file.name,
                            'data': fig_data
                        })
                
                # Clean output (remove figure save notifications)
                stdout_clean = '\n'.join([
                    line for line in result.stdout.split('\n')
                    if not line.startswith('[FIGURE_SAVED:')
                ])
                
                return {
                    'stdout': stdout_clean,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                    'success': result.returncode == 0,
                    'figures': figures
                }
            
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Simulation timeout (>30s)',
                'returncode': -1,
                'success': False,
                'figures': []
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False,
                'figures': []
            }
    
    def _analyze_results(self, design: Dict[str, Any], code: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze simulation results and generate comprehensive report."""
        
        title = design.get('title', 'Experiment')
        physics = design.get('physics_explanation', '')
        stdout = results.get('stdout', '')
        stderr = results.get('stderr', '')
        figures = results.get('figures', [])
        success = results.get('success', False)
        
        if not success:
            return {
                'rating': 0,
                'verdict': 'FAILED',
                'analysis': f'Simulation execution failed: {stderr}',
                'recommendations': ['Fix code errors', 'Check imports and dependencies']
            }
        
        prompt = f"""Analyze this quantum experiment simulation and rate its quality.

**Experiment:** {title}
**Physics Intent:** {physics}

**Simulation Code:**
```python
{code}
```

**Simulation Output:**
```
{stdout}
```

**Analysis Task:**

1. **Physics Correctness:**
   - Does it model the right quantum effects?
   - Are the operators/states appropriate?
   - Any unphysical results (negative probabilities, visibility > 1, impossible values)?

2. **Implementation Quality:**
   - Code structure and clarity
   - Proper use of libraries
   - Error handling

3. **Results Validity:**
   - Do numbers make physical sense?
   - Consistent with theoretical expectations?
   - Useful figures of merit calculated?

**Rating Scale:**
- 9-10: Excellent - correct physics, clean code, physical results
- 7-8: Good - mostly correct, minor issues
- 5-6: Fair - right approach but implementation problems
- 3-4: Poor - wrong physics or major bugs
- 1-2: Failed - doesn't model the experiment correctly

**Response format (JSON only):**
```json
{{
  "rating": 7,
  "verdict": "GOOD|FAIR|POOR|FAILED",
  "physics_correctness": "Assessment of quantum mechanics",
  "implementation_quality": "Code quality assessment",
  "results_validity": "Are numbers physical?",
  "key_findings": ["Finding 1", "Finding 2"],
  "limitations": ["Limitation 1", "Limitation 2"],
  "recommendations": ["General advice 1", "General advice 2"],
  "refinement_instructions": "If rating < 7: Provide SPECIFIC, ACTIONABLE code improvements. Be direct. Examples: 'Line 45: Change beam splitter coefficient from 0.7 to 1/sqrt(2)', 'Add phase calculation: phase = 2*pi*path_diff/wavelength', 'Fix visibility formula to (Imax-Imin)/(Imax+Imin)'. If rating >= 7: leave empty or say 'Code quality is good'."
}}
```

Respond with JSON only."""

        try:
            response = self.llm.predict(prompt).strip()
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                analysis = {
                    'rating': 5,
                    'verdict': 'UNKNOWN',
                    'analysis': 'Could not parse LLM analysis',
                    'recommendations': []
                }
            
            # Generate comprehensive simulation report
            report = self._generate_simulation_report(design, stdout, stderr, figures, analysis)
            analysis['report'] = report
            analysis['figures'] = figures
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  Analysis failed: {e}")
            return {
                'rating': 5,
                'verdict': 'UNKNOWN',
                'analysis': f'Analysis error: {str(e)}',
                'recommendations': [],
                'figures': figures,
                'report': f"## Simulation Report\n\nAnalysis failed: {str(e)}"
            }
    
    def _generate_simulation_report(self, design: Dict, stdout: str, stderr: str, 
                                     figures: List[Dict], analysis: Dict) -> str:
        """Generate formatted simulation report combining output and analysis."""
        
        title = design.get('title', 'Quantum Experiment')
        rating = analysis.get('rating', 'N/A')
        verdict = analysis.get('verdict', 'UNKNOWN')
        
        report = f"""# Simulation Report: {title}

## Overall Assessment
**Quality Rating:** {rating}/10 | **Verdict:** {verdict}

---

## Simulation Output

"""
        
        # Add text output
        if stdout.strip():
            report += f"""### Console Output
```
{stdout.strip()}
```

"""
        
        # Reference figures (separate files in figures/ folder)
        if figures:
            report += f"""### Generated Figures

This simulation produced {len(figures)} figure(s). See the `figures/` folder:

"""
            for i, fig_data in enumerate(figures, 1):
                report += f"- **Figure {i}:** `figures/figure_{i:02d}.png`\n"
            report += "\n"
        
        # Add errors if any
        if stderr.strip():
            report += f"""### Errors/Warnings
```
{stderr.strip()}
```

"""
        
        # Add LLM analysis
        report += f"""---

## Physics Analysis

### Physics Correctness
{analysis.get('physics_correctness', 'No assessment available')}

### Implementation Quality
{analysis.get('implementation_quality', 'No assessment available')}

### Results Validity
{analysis.get('results_validity', 'No assessment available')}

"""
        
        # Add key findings
        if analysis.get('key_findings'):
            report += "### Key Findings\n"
            for finding in analysis['key_findings']:
                report += f"- {finding}\n"
            report += "\n"
        
        # Add limitations
        if analysis.get('limitations'):
            report += "### Limitations\n"
            for limitation in analysis['limitations']:
                report += f"- {limitation}\n"
            report += "\n"
        
        # Add recommendations
        if analysis.get('recommendations'):
            report += "### Recommendations for Improvement\n"
            for rec in analysis['recommendations']:
                report += f"- {rec}\n"
            report += "\n"
        
        report += f"""---

## Design Alignment

This simulation was designed to model:
> {design.get('physics_explanation', 'No description available')}

The simulation {'successfully captures' if rating >= 7 else 'partially captures' if rating >= 5 else 'does not adequately capture'} the intended quantum physics.

---

*Report generated by Aṇubuddhi (अणुबुद्धि) Free-Form Simulation System*
*Designed by S. K. Rithvik*
"""
        
        return report
    
    def _get_similar_toolbox_examples(self, query: str) -> str:
        """
        Get relevant simulation examples from toolbox using semantic search.
        
        Args:
            query: Search query (typically design title + description)
            
        Returns:
            Formatted text of top-3 most relevant examples
        """
        
        toolbox_sims = self.toolbox.get('successful_simulations', {})
        
        if not toolbox_sims:
            return "\n**No previous simulation examples available.**\n"
        
        # Try semantic retrieval first
        if self.retriever:
            try:
                similar_ids = self.retriever.retrieve_similar_simulations(query, top_k=3)
                
                if similar_ids:
                    examples_text = f"\n**Most Relevant Previous Simulations:**\n\n"
                    for sim_id in similar_ids:
                        sim_data = toolbox_sims.get(sim_id)
                        if sim_data:
                            examples_text += f"**{sim_data.get('title')}** (Rating: {sim_data.get('rating')}/10)\n"
                            examples_text += f"Approach: {sim_data.get('approach', 'N/A')}\n"
                            examples_text += f"Key insight: {sim_data.get('key_insight', 'N/A')}\n\n"
                    
                    return examples_text
            except Exception as e:
                print(f"⚠️  Embedding retrieval failed, using fallback: {e}")
        
        # Fallback: return first 3 examples
        examples_text = f"\n**Recent Simulation Examples:**\n\n"
        for sim_id, sim_data in list(toolbox_sims.items())[:3]:
            examples_text += f"**{sim_data.get('title')}** (Rating: {sim_data.get('rating')}/10)\n"
            examples_text += f"Approach: {sim_data.get('approach', 'N/A')}\n"
            examples_text += f"Key insight: {sim_data.get('key_insight', 'N/A')}\n\n"
        
        return examples_text
    
    def _save_successful_simulation(self, design: Dict, code: str, analysis: Dict) -> None:
        """Save successful simulation to toolbox for future reuse."""
        
        try:
            sim_id = design.get('title', 'experiment').lower().replace(' ', '_')
            
            entry = {
                'title': design.get('title'),
                'rating': analysis.get('rating'),
                'approach': analysis.get('physics_correctness', ''),
                'key_insight': analysis.get('key_findings', [''])[0] if analysis.get('key_findings') else '',
                'code_snippet': code[:500],  # First 500 chars
                'saved_date': str(Path.ctime(Path(__file__)))
            }
            
            self.toolbox['successful_simulations'][sim_id] = entry
            
            # Save to file
            with open(self.toolbox_path, 'w') as f:
                json.dump(self.toolbox, f, indent=2)
            
            print(f"💾 Saved successful simulation: {sim_id}")
            
        except Exception as e:
            print(f"⚠️  Could not save simulation: {e}")
    
    def _review_code_before_execution(self, design: Dict, code: str) -> Dict:
        """
        Pre-execution code review: Check if code actually models the design BEFORE running it.
        Critical gate to prevent wasting compute on irrelevant simulations.
        """
        
        title = design.get('title', 'Experiment')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        
        prompt = f"""CRITICAL PRE-EXECUTION REVIEW

You are reviewing simulation code BEFORE execution. Your job: Does this code actually model the designed experiment?

**Design Intent:**
Title: {title}
Description: {description}
Physics: {physics}

**Generated Code:**
```python
{code}
```

**Review Checklist:**

1. **Does code model the RIGHT experiment?**
   - Not a template or generic example
   - Actually implements THIS specific design
   
2. **Are key components present in code?**
   - Design mentions squeezed states → Code must create/model squeezed states
   - Design mentions homodyne → Code must implement quadrature measurement
   - Design mentions cavity → Code must model cavity dynamics
   
3. **Do parameters match or have realistic defaults?**
   - Wavelengths, powers, timescales from design or physics literature
   - Not placeholder values like "1.0" for everything
   
4. **Will execution produce meaningful results?**
   - Code calculates relevant figures of merit
   - Not just "print('hello world')" or trivial calculation
   
5. **Physics sanity:**
   - Uses appropriate formalism for domain
   - Not fundamentally wrong approach (e.g., using Fock states for temporal physics)

**APPROVE ONLY IF:**
- Code clearly attempts to model THIS experiment
- Key physics elements are present
- Will produce interpretable results

**REJECT IF:**
- Wrong experiment entirely
- Missing critical components
- Trivial/placeholder implementation
- Fundamentally wrong physics approach

**Response (JSON only):**
```json
{{
  "approved": true,
  "confidence": 0.8,
  "matches_design": true,
  "key_elements_present": ["element1", "element2"],
  "missing_elements": [],
  "concerns": [],
  "reason": "Brief justification for approve/reject decision"
}}
```

Respond with JSON only."""

        try:
            response = self.llm.predict(prompt).strip()
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group(0))
                if review.get('approved'):
                    print(f"✅ Code review: {review.get('reason', 'Approved')}")
                else:
                    print(f"❌ Code review: {review.get('reason', 'Rejected')}")
                return review
            else:
                # Default to rejecting if can't parse
                return {
                    'approved': False,
                    'reason': 'Could not parse review response'
                }
        except Exception as e:
            print(f"⚠️  Code review failed: {e}")
            # Be conservative - reject on error
            return {
                'approved': False,
                'reason': f'Review error: {str(e)}'
            }
    
    def _refine_simulation_code(self, design: Dict, current_code: str, feedback: Dict) -> str:
        """
        Refine existing code based on specific feedback.
        DO NOT regenerate from scratch - make targeted improvements.
        """
        feedback_type = feedback.get('stage', 'unknown')
        instruction = feedback.get('instruction', '')
        
        # Extract only essential design info to save tokens
        design_summary = f"""Experiment: {design.get('title', 'Unknown')}
Components: {len(design.get('components', []))} items
Key: {', '.join([c.get('name', 'unknown') for c in design.get('components', [])[:5]])}"""
        
        prompt = f"""Refine quantum simulation code based on feedback.

**Experiment:**
{design_summary}

**Current Code ({len(current_code)} chars):**
```python
{current_code}
```

**Issue:** {feedback.get('issue_type', 'unknown')}

**Instructions:**
{instruction}

**Fix ONLY what's broken. Keep working parts intact.**

**What to change:**
"""
        
        # Add stage-specific guidance
        if feedback_type == 'pre_review':
            prompt += f"""
- Add missing components: {feedback.get('missing_elements', [])}
- Address concerns: {feedback.get('concerns', [])}
- Keep existing correct implementations
"""
        elif feedback_type == 'execution':
            stderr_full = feedback.get('stderr', '')
            error_msg = feedback.get('error', '')
            
            # Extract line number from traceback if available
            line_number = "Unknown"
            if stderr_full:
                # Look for "line XX" pattern
                line_match = re.search(r'line (\d+)', stderr_full)
                if line_match:
                    line_number = line_match.group(1)
            
            # Check if it's a QuTiP error to decide how much guidance to include
            is_qutip_error = 'qutip' in stderr_full.lower() or 'Qobj' in stderr_full or '.dag()' in stderr_full
            
            prompt += f"""
- Fix this error: {error_msg}
- Line {line_number} in traceback:
```
{stderr_full[:500]}
```

**Quick Fix:**
1. Check line {line_number}
2. Identify the operation causing error
3. Fix it"""
            
            # Only include QuTiP guide if it's actually a QuTiP error
            if is_qutip_error:
                prompt += """

**QuTiP Quick Fixes:**
- `.dag() * state` → Returns NUMBER not Qobj. Use `.overlap()` or `.norm()`
- Tensor products: `qt.tensor(a, b)` for composite systems
- Type errors: Check if variable is Qobj vs complex number"""
        elif feedback_type == 'post_execution':
            prompt += f"""
- Improve alignment with design
- Missing from code: {feedback.get('missing_from_code', [])}
- Wrong in code: {feedback.get('wrong_in_code', [])}
"""
        elif feedback_type == 'quality':
            prompt += f"""
- Address weaknesses: {feedback.get('weaknesses', [])}
- Implement suggestions: {feedback.get('suggestions', [])}
"""
        
        prompt += """

Return ONLY the improved Python code, no explanations."""
        
        try:
            refined_code = self.llm.predict(prompt).strip()
            # Extract code block if wrapped
            code_match = re.search(r'```python\n(.*?)\n```', refined_code, re.DOTALL)
            if code_match:
                refined = code_match.group(1)
            else:
                # Remove markdown if present
                refined = refined_code.replace('```python', '').replace('```', '').strip()
            
            # Verify refinement actually changed something
            if refined == current_code:
                print(f"⚠️  Refinement returned identical code - LLM may not have understood instructions")
            elif len(refined) < len(current_code) * 0.5:
                print(f"⚠️  Refined code much shorter ({len(refined)} vs {len(current_code)} chars) - may be incomplete")
            
            return refined
        except Exception as e:
            print(f"⚠️  Code refinement failed: {e}")
            import traceback
            traceback.print_exc()
            return current_code  # Return unchanged on error
    
    def _build_refinement_instruction(self, stage: str, **kwargs) -> str:
        """Build specific, actionable refinement instructions based on failure stage."""
        
        if stage == 'pre_review':
            missing = kwargs.get('missing', [])
            concerns = kwargs.get('concerns', [])
            reason = kwargs.get('reason', '')
            
            instruction = f"CODE DOES NOT MODEL DESIGN CORRECTLY.\n\n"
            instruction += f"Problem: {reason}\n\n"
            
            if missing:
                instruction += "MISSING ELEMENTS (must add):\n"
                for elem in missing:
                    instruction += f"- {elem}\n"
            
            if concerns:
                instruction += "\nCONCERNS (must address):\n"
                for concern in concerns:
                    instruction += f"- {concern}\n"
            
            instruction += "\nFix: Add missing components and address concerns. Keep existing correct code."
            return instruction
        
        elif stage == 'execution':
            error = kwargs.get('error', '')
            stderr = kwargs.get('stderr', '')
            
            instruction = f"RUNTIME ERROR - CODE WON'T EXECUTE.\n\n"
            instruction += f"Error: {error}\n"
            if stderr:
                instruction += f"Stderr: {stderr[:300]}\n"
            instruction += "\nFix: Correct the bug. Don't change physics model, just fix syntax/imports/logic errors."
            return instruction
        
        elif stage == 'post_execution':
            alignment = kwargs.get('alignment', {})
            missing = alignment.get('missing_from_code', [])
            wrong = alignment.get('wrong_in_code', [])
            
            instruction = "CODE EXECUTES BUT OUTPUT DOESN'T MATCH DESIGN.\n\n"
            
            if missing:
                instruction += "MISSING FROM CODE:\n"
                for elem in missing:
                    instruction += f"- {elem}\n"
            
            if wrong:
                instruction += "\nWRONG IN CODE:\n"
                for elem in wrong:
                    instruction += f"- {elem}\n"
            
            instruction += "\nFix: Adjust code to correctly model design intent. Output should match what design describes."
            return instruction
        
        elif stage == 'quality':
            reflection = kwargs.get('reflection', {})
            weaknesses = reflection.get('critical_weaknesses', [])
            suggestions = reflection.get('improvement_suggestions', [])
            
            instruction = "CODE WORKS BUT QUALITY TOO LOW.\n\n"
            
            if weaknesses:
                instruction += "CRITICAL WEAKNESSES:\n"
                for weak in weaknesses:
                    instruction += f"- {weak}\n"
            
            if suggestions:
                instruction += "\nIMPROVEMENT SUGGESTIONS:\n"
                for sug in suggestions:
                    instruction += f"- {sug}\n"
            
            instruction += "\nFix: Improve code quality and physics accuracy."
            return instruction
        
        else:
            return "Improve code quality and alignment with design."
    
    def _create_failure_result(self, reason: str, history: list) -> Dict:
        """Create standardized failure result."""
        return {
            'valid': False,
            'rating': 2,
            'confidence': 'low',
            'code': None,
            'results': {},
            'analysis': {
                'physics_correctness': reason,
                'verdict': 'FAILED',
                'limitations': ['Could not generate working simulation'],
                'recommendations': ['Review design and try again']
            },
            'convergence_info': {
                'iterations': len(history),
                'converged': False,
                'reason': reason,
                'refinement_history': history
            }
        }
    
    def _check_design_alignment(self, design: Dict, code: str, results: Dict, analysis: Dict) -> Dict:
        """
        Check if the simulation code actually implements what the design specifies.
        Critical quality check to ensure code matches design intent.
        """
        
        title = design.get('title', 'Experiment')
        description = design.get('description', '')
        physics = design.get('physics_explanation', '')
        components = design.get('components', [])
        
        prompt = f"""Review if this simulation code correctly implements the experimental design.

**Original Design:**
Title: {title}
Description: {description}
Physics: {physics}

Components specified:
{json.dumps(components, indent=2)}

**Generated Simulation Code:**
```python
{code}
```

**Execution Output:**
{results.get('stdout', '')}

**Critical Alignment Questions:**

Your job: Determine if this code actually simulates the designed experiment or if it's "arbitrary jazz."

1. **Does the code model the EXACT physics described in the design?**
   - Not "similar" physics - the ACTUAL phenomenon described
   - If design says "time-bin entanglement", code must model temporal correlations
   - If design says "squeezed states", code must model quadrature noise reduction
   - If design says "Bell measurement", code must implement proper projective measurement

2. **Are ALL key components from design actually used in simulation?**
   - Beam splitters → Code should have beam splitter operators/matrices
   - Phase shifters → Code should apply phase shifts
   - Detectors → Code should simulate measurement process
   - Homodyne → Code should calculate quadrature measurements, not photon counts
   - Don't accept generic "placeholder" implementations

3. **Do parameters match design specifications?**
   - Wavelength: If design specifies 810nm, code can't use 532nm
   - Crystal type: BBO vs PPLN have different properties
   - Cavity finesse: F=1000 vs F=10000 dramatically changes behavior
   - Can't just "make up" parameters - must come from design or be realistic defaults

4. **Does output match claimed observable?**
   - Design promises "visibility" → Code must calculate V = (Imax-Imin)/(Imax+Imin)
   - Design promises "fidelity" → Code must calculate |⟨target|actual⟩|²
   - Design promises "squeezing dB" → Code must calculate 10*log10(ΔX²/ΔX²_vac)
   - Not acceptable: Calculate something else and call it by wrong name

5. **Physics sanity check:**
   - Are results physically possible? (0≤F≤1, 0≤V≤1, squeezing<15dB)
   - Does code conserve quantum numbers appropriately?
   - Are there nonsensical approximations? (treating 1550nm photon as if it's 532nm)

**RED FLAGS (automatic low score):**
- Code simulates a different experiment entirely
- Ignores key components (e.g., no homodyne in homodyne experiment)
- Parameters wildly wrong (68 dB squeezing, 0.3 photon LO)
- Calculates wrong figures of merit
- Results violate physical bounds
- Generic template not adapted to this specific design

**Response format (JSON only):**
```json
{{
  "alignment_score": 7,
  "actually_models_design": true,
  "physics_match_quality": "exact|close|approximate|wrong",
  "all_components_used": false,
  "missing_from_code": ["Specific component/feature"],
  "wrong_in_code": ["Specific error/mismatch"],
  "parameter_accuracy": "matches|realistic_defaults|invented|wrong",
  "outputs_correct_observables": true,
  "is_arbitrary_jazz": false,
  "overall_assessment": "Does code actually model THIS design?"
}}
```

Respond with JSON only."""

        try:
            response = self.llm.predict(prompt).strip()
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                alignment = json.loads(json_match.group(0))
                print(f"🎯 Design alignment score: {alignment.get('alignment_score', '?')}/10")
                return alignment
            else:
                return {
                    'alignment_score': 5,
                    'overall_assessment': 'Could not parse alignment check'
                }
        except Exception as e:
            print(f"⚠️  Alignment check failed: {e}")
            return {
                'alignment_score': 5,
                'overall_assessment': f'Alignment check error: {str(e)}'
            }
    
    def _self_reflect(self, design: Dict, code: str, results: Dict, 
                      analysis: Dict, alignment: Dict) -> Dict:
        """
        Self-reflection: critically assess own simulation quality.
        Combines initial analysis + alignment check for final rating.
        """
        
        initial_rating = analysis.get('rating', 5)
        alignment_score = alignment.get('alignment_score', 5)
        physics_correct = analysis.get('physics_correctness', '')
        limitations = analysis.get('limitations', [])
        missing_from_code = alignment.get('missing_from_code', [])
        
        prompt = f"""Self-reflect on this simulation's quality and provide final assessment.

**Context:**
- Initial quality rating: {initial_rating}/10
- Design alignment score: {alignment_score}/10
- Physics correctness: {physics_correct}

**Identified Issues:**
Limitations: {json.dumps(limitations, indent=2)}
Missing from code: {json.dumps(missing_from_code, indent=2)}

**Self-Reflection Questions:**

1. **Honest Quality**: Given all factors, what is the TRUE quality rating?
   - Was initial rating too generous or harsh?
   - Does alignment check reveal missing pieces?
   - Are there hidden flaws in the approach?

2. **Design Capture**: Did this simulation actually model what was designed?
   - If alignment_score < initial_rating, should final rating be lower?
   - Were critical components or effects omitted?

3. **Improvement Potential**: What would make this simulation better?
   - Specific code changes needed?
   - Different physics approach?
   - Better parameter choices?

4. **Confidence Level**: How confident are you in this simulation?
   - High confidence (8-10): Would publish results
   - Medium confidence (5-7): Good for prototyping
   - Low confidence (1-4): Major concerns remain

**Rating Adjustment Logic:**
- If alignment_score < initial_rating: Final rating should be lower
- If critical components missing: Reduce rating by 2-3 points
- If physics approach fundamentally wrong: Rating ≤ 3
- If execution successful but results unphysical: Rating ≤ 4

**Response format (JSON only):**
```json
{{
  "final_rating": 6,
  "confidence_level": "medium",
  "rating_justification": "Why this final rating",
  "key_strengths": ["Strength 1", "Strength 2"],
  "critical_weaknesses": ["Weakness 1", "Weakness 2"],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
  "should_retry": false,
  "retry_reason": "If should_retry=true, explain why"
}}
```

Respond with JSON only."""

        try:
            response = self.llm.predict(prompt).strip()
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                reflection = json.loads(json_match.group(0))
                final_rating = reflection.get('final_rating', initial_rating)
                print(f"🧠 Self-reflection final rating: {final_rating}/10 (was {initial_rating}/10)")
                return reflection
            else:
                return {
                    'final_rating': initial_rating,
                    'confidence_level': 'medium',
                    'rating_justification': 'Could not parse self-reflection'
                }
        except Exception as e:
            print(f"⚠️  Self-reflection failed: {e}")
            return {
                'final_rating': initial_rating,
                'confidence_level': 'low',
                'rating_justification': f'Self-reflection error: {str(e)}'
            }
