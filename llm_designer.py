"""
LLM-Driven Quantum Experiment Designer with Memory
Let the LLM learn from experience and build upon past work
"""

import json
import re
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Add src to path for memory import
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from agentic_quantum.memory.memory_system import ExperimentMemory
    MEMORY_AVAILABLE = True
    print("✅ Memory module loaded successfully")
except ImportError as e:
    MEMORY_AVAILABLE = False
    print(f"⚠️  Memory system not available - running without memory features: {e}")

# Toolbox system replaces memory (no ChromaDB needed)
try:
    from toolbox_loader import get_toolbox, ToolboxLoader
    TOOLBOX_AVAILABLE = True
    print("✅ Toolbox loader imported successfully")
except ImportError as e:
    TOOLBOX_AVAILABLE = False
    get_toolbox = None
    ToolboxLoader = None
    print(f"⚠️  Toolbox system not available: {e}")

try:
    from simulation_agent import SimulationAgent
    SIMULATION_AVAILABLE = True
    print("✅ Simulation agent loaded successfully")
except ImportError as e:
    SIMULATION_AVAILABLE = False
    print(f"⚠️  Simulation agent not available: {e}")


@dataclass
class OpticalSetup:
    """The LLM's complete optical table design."""
    title: str
    description: str
    components: List[Dict[str, Any]]
    beam_path: List[tuple[int, int]] = field(default_factory=list)
    physics_explanation: str = ""
    expected_outcome: str = ""
    component_justifications: Dict[str, str] = field(default_factory=dict)
    # Debug fields
    raw_llm_response: str = ""
    parsed_design_json: Dict[str, Any] = field(default_factory=dict)
    web_search_used: bool = False
    web_search_context: str = ""
    # Simulation results
    simulation_results: Optional[Dict[str, Any]] = None


class LLMDesigner:
    """
    LLM-driven designer with self-correction loop and memory system.
    Generates design → validates → refines if needed → max 3 cycles.
    Learns from past experiments and reuses building blocks.
    """
    
    def __init__(self, llm_client, max_refinement_cycles: int = 3, web_search_tool=None, use_memory: bool = True, use_simulation: bool = True):
        """
        Requires LLM client to work. Optionally provide web search tool.
        
        Args:
            llm_client: LLM client for generation
            max_refinement_cycles: Maximum self-correction cycles
            web_search_tool: Optional web search function
            use_memory: Enable memory system for learning
            use_simulation: Enable LLM-driven quantum simulations
        """
        if llm_client is None:
            raise ValueError("LLMDesigner requires an LLM client")
        self.llm = llm_client
        self.max_refinement_cycles = max_refinement_cycles
        self.web_search = web_search_tool
        self.use_memory = use_memory  # Store the flag
        self.use_toolbox = use_memory and TOOLBOX_AVAILABLE  # Reuse use_memory param for backwards compat
        
        # Initialize memory system for experiment retrieval
        if use_memory and MEMORY_AVAILABLE:
            try:
                self.memory = ExperimentMemory()
                print(f"✅ Memory system initialized for experiment retrieval")
            except Exception as e:
                print(f"⚠️  Could not initialize memory system: {e}")
                self.memory = None
        else:
            self.memory = None
        
        # Initialize toolbox system (primitives + learned composites)
        if self.use_toolbox:
            try:
                self.toolbox = get_toolbox()
                print(f"✅ Toolbox system initialized - AI can use learned building blocks!")
                composites = self.toolbox.list_all_composites()
                print(f"🧰 Toolbox: {len(composites)} learned composite blocks available")
                
                # Initialize embedding retriever for efficient semantic search
                from embedding_retriever import EmbeddingRetriever
                self.retriever = EmbeddingRetriever()
                print(f"✅ Embedding retriever initialized for semantic search")
            except Exception as e:
                print(f"⚠️  Could not initialize toolbox: {e}")
                self.use_toolbox = False
                self.toolbox = None
                self.retriever = None
        else:
            self.toolbox = None
            self.retriever = None
        
        # Initialize simulation agent
        self.use_simulation = use_simulation and SIMULATION_AVAILABLE
        if self.use_simulation:
            try:
                self.simulator = SimulationAgent(llm_client)
                print(f"✅ Simulation agent initialized - designs will be validated!")
            except Exception as e:
                print(f"⚠️  Could not initialize simulation agent: {e}")
                self.use_simulation = False
                self.simulator = None
        else:
            self.simulator = None
    
    def route_user_message(self, query: str, current_design: Optional[Dict] = None) -> tuple[str, str]:
        """
        Intelligently determine if user wants to chat or modify the design using LLM.
        
        Returns:
            (mode, reason) where mode is 'chat' or 'design'
        """
        
        # Build routing prompt
        design_status = "A design currently exists." if current_design else "No design exists yet."
        design_info = ""
        if current_design:
            design_info = f"\nCurrent design: {current_design.get('title', 'Untitled')}"
        
        routing_prompt = f"""You are a routing assistant. Classify the user's intent as either 'CHAT' or 'DESIGN'.

**DESIGN**: User wants to CREATE a new experiment or MODIFY the existing optical table setup
- Examples: 
  - "design an interferometer"
  - "design hong ou mandel setup"
  - "create a bell state experiment"
  - "add a filter"
  - "remove the mirror"
  - "make it more sensitive"
  - "setup for EIT"
  - "build a squeezed light source"

**CHAT**: User wants to ASK QUESTIONS, get EXPLANATIONS, or discuss PRACTICAL ASPECTS (not modifying the design)
- Examples: 
  - "what is quantum entanglement?"
  - "why does this work?"
  - "how can I build this in real life?"
  - "where can I buy these components?"
  - "explain the physics"
  - "what equipment do I need?"

Current situation: {design_status}{design_info}

User message: "{query}"

CRITICAL: If the user says "design X" or "create X" or "setup for X", this is ALWAYS DESIGN mode!

Respond with ONLY ONE WORD: either "CHAT" or "DESIGN" """

        try:
            # Use LLM for intelligent routing
            response = self.llm.predict(routing_prompt).strip().upper()
            
            # Parse response
            if 'CHAT' in response:
                return ('chat', f'LLM classified as question/discussion')
            elif 'DESIGN' in response:
                return ('design', f'LLM classified as design modification')
            else:
                # Fallback to simple heuristics
                print(f"⚠️  Unexpected routing response: {response}, using fallback")
                return self._fallback_routing(query, current_design)
                
        except Exception as e:
            print(f"⚠️  LLM routing failed: {e}, using fallback")
            return self._fallback_routing(query, current_design)
    
    def _fallback_routing(self, query: str, current_design: Optional[Dict] = None) -> tuple[str, str]:
        """Simple keyword-based fallback routing if LLM fails."""
        query_lower = query.lower()
        
        # Strong design modification indicators
        design_keywords = [
            'add', 'remove', 'replace', 'change', 'modify', 'adjust', 'move',
            'increase', 'decrease', 'swap', 'switch', 'insert', 'delete',
            'make it', 'convert to', 'turn it into', 'transform'
        ]
        
        # Strong chat/question indicators  
        chat_keywords = [
            'what is', 'why', 'how does', 'how do', 'how can', 'explain', 'tell me',
            'can you explain', 'describe', 'what are', 'what would',
            'is this', 'does this', 'will this', 'could this',
            'show me', 'help me understand', 'where can', 'where do',
            'what happens if', 'what\'s the', 'whats the'
        ]
        
        # Check for chat/question intent FIRST (higher priority)
        for keyword in chat_keywords:
            if keyword in query_lower:
                return ('chat', f'Question keyword detected: "{keyword}"')
        
        # Check for design modification intent
        for keyword in design_keywords:
            if keyword in query_lower:
                return ('design', f'Design keyword detected: "{keyword}"')
        
        # Special cases
        if 'design' in query_lower and 'setup' in query_lower and not current_design:
            return ('design', 'New design request detected')
        
        # If no design exists, assume they want to create one
        if not current_design:
            return ('design', 'No current design - assuming new design request')
        
        # Default: if design exists and no clear indicators, assume chat
        return ('chat', 'Ambiguous - defaulting to chat mode')
    
    def chat_about_design(self, query: str, current_design: Optional[Dict] = None, conversation_context: Optional[List[Dict]] = None) -> str:
        """
        Conversational Q&A about quantum optics, physics, or the current design.
        Uses memory to provide informed answers.
        
        Args:
            query: User's question
            current_design: Current experiment design (if any)
            conversation_context: Conversation history
            
        Returns:
            Conversational response (not a design modification)
        """
        print(f"💬 Chat mode: {query}")
        
        # Build context from current design
        design_context = ""
        if current_design:
            # Get component list with numbers for easy reference
            components = current_design.get('experiment', {}).get('steps', [])
            component_list = ""
            if components:
                component_list = "\n**Component List (by number):**\n"
                for i, comp in enumerate(components, 1):
                    comp_name = comp.get('description', comp.get('type', 'Component'))
                    comp_type = comp.get('type', 'unknown')
                    pos = comp.get('position', (0, 0))
                    component_list += f"{i}. {comp_name} ({comp_type}) at position ({pos[0]:.1f}, {pos[1]:.1f})\n"
            
            design_context = f"""
**Current Design Context:**
- Title: {current_design.get('title', 'N/A')}
- Description: {current_design.get('description', 'N/A')}
- Components: {len(components)} optical components
- Physics: {current_design.get('physics_explanation', 'N/A')}
{component_list}
**NOTE**: User may refer to components by their numbers (e.g., "components 5 and 6" or "#3") - use the numbered list above to understand which components they mean.

"""
        
        # Search memory for relevant information
        memory_context = ""
        if self.use_memory and self.memory:
            try:
                print(f"🧠 Searching memory for relevant knowledge...")
                # Get similar experiments
                similar = self.memory.retrieve_similar_experiments(query, n_results=3)
                if similar:
                    memory_context = "\n**Relevant Past Experiments:**\n"
                    for exp in similar:
                        memory_context += f"- {exp.get('title', 'Untitled')}: {exp.get('description', '')}\n"
            except Exception as e:
                print(f"⚠️  Memory search failed: {e}")
        
        # Detect if this is a practical "how to build/buy" question
        is_practical_question = any(keyword in query.lower() for keyword in 
            ['how can i build', 'where can i', 'how to build', 'what equipment', 
             'where to buy', 'where do i', 'how do i build', 'what do i need',
             'shopping list', 'purchase', 'vendor', 'supplier'])
        
        practical_instruction = ""
        if is_practical_question and current_design:
            practical_instruction = """
**IMPORTANT**: The user is asking about PRACTICAL implementation (building/buying). Provide:
1. Recommended vendors/suppliers (e.g., Thorlabs, Edmund Optics, Newport)
2. Approximate costs for key components
3. Difficulty level and required expertise
4. Step-by-step assembly guidance if relevant
5. Safety considerations or alignment tips
"""
        
        chat_prompt = f"""You are an expert quantum optics consultant. The user is asking you a question about quantum experiments, physics, or the current design.

{design_context}{memory_context}{practical_instruction}

**User Question:** {query}

**Instructions:**
- Provide a clear, conversational answer (3-5 sentences for complex questions)
- If asking about the current design, reference its components and physics
- If asking about quantum physics concepts, explain them clearly
- If asking "why" or "how", provide educational explanations
- If asking about practical implementation (buying/building), suggest vendors and give practical tips
- Be friendly, informative, and helpful
- DO NOT output JSON - just natural conversational text

Respond conversationally:"""

        try:
            response = self.llm.predict(chat_prompt)
            print(f"✅ Chat response: {len(response)} characters")
            return response.strip()
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return "I apologize, but I encountered an error while processing your question. Could you try rephrasing it?"
    
    def design_experiment(self, query: str, conversation_context: Optional[List[Dict]] = None) -> OpticalSetup:
        """
        Ask LLM to design complete optical experiment with self-correction and memory.
        
        Process:
        1. FIRST: Search memory for existing similar experiments (retrieval-first)
        2. If found: Return existing design directly (user can approve/reject in UI)
        3. If not satisfied or not found: Generate new design
        4. Search memory for relevant past experiments and building blocks
        5. Augment query with memory context if available
        6. Optionally search web for context if needed
        7. LLM generates initial design (using past experience)
        8. Validator LLM reviews design for errors
        9. If errors found, refiner LLM corrects them
        10. Repeat up to max_refinement_cycles times
        11. Store successful design in memory for future use (with human approval)
        12. Return best design
        """
        
        print(f"🤖 Starting design for: {query}")
        
        # Note: Memory retrieval removed - toolbox provides learned composites in prompt instead
        # No need for semantic search since LLM sees all learned blocks directly
        
        # Web search is now LLM-controlled - it can request searches via <WEB_SEARCH> tags
        self._last_web_context = ""  # Track web search context for this design
        self._last_web_source = None
        
        # Initial design generation (with memory-augmented prompt and conversation context)
        
        design_prompt = self._build_comprehensive_prompt(query, conversation_context)
        
        for cycle in range(self.max_refinement_cycles):
            print(f"\n{'='*70}")
            print(f"🔄 Refinement Cycle {cycle + 1}/{self.max_refinement_cycles}")
            print(f"{'='*70}")
            
            try:
                # Generate/refine design
                if cycle == 0:
                    print(f"🤖 Generating initial design...")
                    response = self.llm.predict(design_prompt)
                    
                    # Check if LLM requested a web search
                    if self.web_search and '<WEB_SEARCH>' in response:
                        search_query = self._extract_search_query(response)
                        if search_query:
                            print(f"🔍 LLM requested web search: '{search_query}'")
                            web_context, web_source = self._search_for_context(search_query)
                            if web_context:
                                self._last_web_context = web_context
                                self._last_web_source = web_source
                                if web_source == 'web':
                                    print(f"✅ Found information from web")
                                else:
                                    print(f"📚 Using curated knowledge")
                                # Provide results back to LLM
                                search_results_prompt = f"""{design_prompt}

**WEB SEARCH RESULTS FOR: "{search_query}"**
{web_context}

Now design the experiment using this information."""
                                response = self.llm.predict(search_results_prompt)
                else:
                    print(f"🔧 Refining design based on feedback...")
                    refinement_prompt = self._build_refinement_prompt(query, response, validation_feedback)
                    response = self.llm.predict(refinement_prompt)
                
                # Check for API errors
                if response.startswith("Error:"):
                    print(f"❌ LLM API Error: {response}")
                    if "402" in response:
                        print(f"💳 OpenRouter credits exhausted - please add credits at https://openrouter.ai/")
                    elif "429" in response:
                        print(f"⏰ Rate limit exceeded - please wait and try again")
                    raise Exception(response)
                
                print(f"✅ LLM responded with {len(response)} characters")
                
                # Check if LLM wants to use existing composite
                design = self._parse_llm_response(response)
                
                # Special case: LLM decided to use existing design
                if design.get('use_existing') and design.get('composite_id'):
                    print(f"🔍 LLM suggests using existing composite: {design.get('composite_id')}")
                    print(f"   Reason: {design.get('reason', 'N/A')}")
                    
                    # Load the composite design
                    try:
                        composite_design = self.toolbox.get_composite(design['composite_id'])
                        if composite_design:
                            print(f"✅ Loaded composite design: {composite_design.get('name', 'N/A')}")
                            
                            # Get full_design which has all the data
                            full_design = composite_design.get('full_design', {})
                            
                            # Extract components from experiment.steps (the format used by renderer)
                            experiment = full_design.get('experiment', {})
                            components = experiment.get('steps', [])
                            
                            # Convert steps back to component format
                            if components:
                                # Steps format: {type, description, position, angle, parameters}
                                # Component format: {type, name, x, y, angle, parameters}
                                converted_components = []
                                for step in components:
                                    comp = {
                                        'type': step.get('type'),
                                        'name': step.get('description', step.get('type', 'Component')),
                                        'x': step.get('position', (0, 0))[0],
                                        'y': step.get('position', (0, 0))[1],
                                        'angle': step.get('angle', 0),
                                        'parameters': step.get('parameters', {})
                                    }
                                    converted_components.append(comp)
                                components = converted_components
                            
                            print(f"   Extracted {len(components)} components")
                            
                            # Return special marker so UI can show three-button choice
                            result = OpticalSetup(
                                title=composite_design.get('name', 'Existing Design'),
                                description=composite_design.get('description', ''),
                                components=components,
                                beam_path=experiment.get('beam_path', []),
                                physics_explanation=composite_design.get('physics_explanation', ''),
                                expected_outcome=full_design.get('expected_outcome', ''),
                                component_justifications=full_design.get('component_justifications', {}),
                                raw_llm_response=response,
                                parsed_design_json=composite_design,
                                web_search_used=False,
                                web_search_context=""
                            )
                            print(f"   OpticalSetup created with {len(result.components)} components")
                            # Mark as retrieved so UI can show choice buttons
                            result.from_toolbox = True
                            result.toolbox_metadata = {
                                'composite_id': design['composite_id'],
                                'reason': design.get('reason', ''),
                                'user_query': query
                            }
                            return result
                    except Exception as e:
                        print(f"⚠️  Could not load composite, generating new design instead: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fall through to normal generation
                
                print(f"✅ Parsed design with {len(design.get('components', []))} components")
                
                # Validate design
                print(f"🔍 Validating design...")
                is_valid, validation_feedback = self._validate_design(query, design, response)
                
                if is_valid:
                    print(f"✅ Design validated successfully!")
                    print(f"🎉 Final design ready after {cycle + 1} cycle(s)")
                    break
                else:
                    print(f"⚠️  Validation issues found:")
                    for issue in validation_feedback.split('\n'):
                        if issue.strip():
                            print(f"    • {issue.strip()}")
                    
                    if cycle < self.max_refinement_cycles - 1:
                        print(f"🔄 Proceeding to refinement...")
                    else:
                        print(f"⚠️  Max refinement cycles reached, using current design")
            
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error in cycle {cycle + 1}: {e}")
                # Always retry with stricter JSON instructions (not just cycle 0)
                print(f"🔄 Retrying with stricter JSON formatting instructions...")
                
                retry_prompt = f"""
PREVIOUS ATTEMPT FAILED - JSON WAS MALFORMED. TRY AGAIN WITH PERFECT JSON.

Original request: {query}

CRITICAL ERROR: Your previous response had a JSON syntax error: "{e.msg}" at position {e.pos}.

The most common cause is UNTERMINATED STRINGS due to hitting token limits mid-response.
If your design is very complex, SIMPLIFY it to fit within the response limit.
Reduce the number of components or shorten descriptions if needed.

You MUST return ONLY valid JSON with NO syntax errors.

Common mistakes to avoid:
1. Unescaped quotes in strings (use \\" not ")
2. Actual newlines in strings (use \\n not real newlines)
3. Trailing commas before closing brackets
4. Unclosed brackets or braces
5. Missing closing quotes (CHECK THE END of your response)
6. Stopping mid-sentence (complete ALL strings and close ALL brackets)

VALIDATE YOUR JSON: Make sure every opening brace {{ has a closing }}, every opening bracket [ has a closing ], and every string starts and ends with quotes.

Generate the design again with PERFECT JSON formatting:
"""
                try:
                    retry_response = self.llm.predict(retry_prompt)
                    design = self._parse_llm_response(retry_response)
                    response = retry_response
                    print(f"✅ Retry successful! Parsed design with {len(design.get('components', []))} components")
                    
                    # Validate the retry design
                    print(f"🔍 Validating design...")
                    is_valid, validation_feedback = self._validate_design(query, design, response)
                    
                    if is_valid:
                        print(f"✅ Design validated successfully!")
                        print(f"🎉 Final design ready after retry")
                        break  # Exit the loop with valid design
                    else:
                        print(f"⚠️  Retry design has validation issues, will refine in next cycle")
                        # Continue to next cycle for refinement
                        continue
                        
                except Exception as retry_error:
                    print(f"❌ Retry also failed: {retry_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # If on initial cycle, use fallback
                    if cycle == 0:
                        print(f"⚠️  Using emergency fallback for query: {query}")
                        return self._emergency_fallback(query)
                    else:
                        # Use previous design if refinement fails
                        print(f"⚠️  Using design from previous cycle")
                        break
            
            except Exception as e:
                print(f"❌ Error in cycle {cycle + 1}: {e}")
                if cycle == 0:
                    # Can't recover from initial design failure
                    import traceback
                    traceback.print_exc()
                    print(f"⚠️  Using emergency fallback for query: {query}")
                    return self._emergency_fallback(query)
                # Use previous design if refinement fails
                break
        
        # After loop completes, return the final design
        # Validate structure (not physics, just format)
        if not self._has_valid_structure(design):
            print(f"⚠️  Invalid design structure, using emergency fallback")
            return self._emergency_fallback(query)
        
        # Create the optical setup
        optical_setup = OpticalSetup(
            title=design.get('title', 'Quantum Experiment'),
            description=design.get('description', ''),
            components=design.get('components', []),
            beam_path=_normalize_beam_path(design.get('beam_path', [])),
            physics_explanation=design.get('physics_explanation', ''),
            expected_outcome=design.get('expected_outcome', ''),
            component_justifications=design.get('component_justifications', {}),
            raw_llm_response=response,
            parsed_design_json=design,
            web_search_used=bool(self._last_web_context),
            web_search_context=self._last_web_context
        )
        
        # Extract and save any custom components for future reuse
        self._extract_and_save_custom_components(design)
        
        # NOTE: Simulation is now run on-demand via run_simulation() method
        # when user clicks the "Run Simulation" button in the UI
        
                # Simulation is triggered separately by user interaction
        # when user clicks the "Run Simulation" button in the UI
        
        # NOTE: Memory storage moved to human approval step in UI
        # This ensures only validated, human-approved designs are stored
        # preventing duplicate low-quality experiments from cluttering memory

        
        return optical_setup
    
    def run_simulation(self, optical_setup: OpticalSetup) -> Dict:
        """
        Run quantum simulation on an existing design (on-demand).
        Called when user clicks 'Run Simulation' button in UI.
        
        Args:
            optical_setup: The OpticalSetup object from design_experiment()
            
        Returns:
            Dict with simulation results (verdict, confidence, interpretation, etc.)
        """
        if not self.use_simulation or not self.simulator:
            return {
                'success': False,
                'error': 'Simulation not enabled. Install QuTiP: pip install qutip'
            }
        
        try:
            print(f"🔬 Running LLM-driven quantum simulation...")
            simulation_results = self.simulator.validate_design({
                'title': optical_setup.title,
                'description': optical_setup.description,
                'experiment': {'steps': optical_setup.components},
                'physics_explanation': optical_setup.physics_explanation
            })
            
            if simulation_results.get('success'):
                verdict = simulation_results.get('verdict', 'unknown')
                confidence = simulation_results.get('confidence', 0)
                print(f"✅ Simulation verdict: {verdict.upper()} (confidence: {confidence:.1%})")
                print(f"💡 {simulation_results.get('interpretation', 'No interpretation')}")
                
                # Show recommendations if any
                recommendations = simulation_results.get('recommendations', [])
                if recommendations:
                    print(f"🔧 Recommendations:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec}")
            else:
                print(f"⚠️  Simulation could not validate design: {simulation_results.get('error', 'Unknown')}")
            
            return simulation_results
            
        except Exception as e:
            print(f"⚠️  Simulation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_search_query(self, response: str) -> str:
        """Extract search query from LLM's <WEB_SEARCH> tags."""
        import re
        match = re.search(r'<WEB_SEARCH>(.*?)</WEB_SEARCH>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_search_query(self, response: str) -> str:
        """
Extract search query from LLM's <WEB_SEARCH> tags.
        """
        import re
        match = re.search(r'<WEB_SEARCH>(.*?)</WEB_SEARCH>', response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _should_search(self, query: str) -> bool:
        """Legacy method - web search is now LLM-controlled via <WEB_SEARCH> tags.
        Kept for backward compatibility but not actively used.
        """
        return False  # LLM decides when to search
    
    def _search_for_context(self, query: str) -> tuple[str, str]:
        """Search web for relevant context about the experiment.
        Returns (context_string, source) where source is 'web' or 'curated'.
        """
        if not self.web_search:
            return "", None
        
        try:
            # Build search query focused on quantum optics
            search_query = f"{query} quantum optics experiment setup"
            
            print(f"   🔎 Query: {search_query}")
            results = self.web_search(search_query)
            
            if not results or 'results' not in results:
                return "", None
            
            source = results.get('source', 'unknown')
            
            # Extract and format relevant information
            context_parts = []
            for i, result in enumerate(results.get('results', [])[:3], 1):  # Top 3 results
                title = result.get('title', 'Unknown')
                snippet = result.get('description', result.get('snippet', ''))
                url = result.get('url', '')
                
                if snippet:
                    context_parts.append(f"[{i}] {title}\n{snippet}\nSource: {url}\n")
            
            if context_parts:
                return "\n".join(context_parts), source
            
        except Exception as e:
            print(f"   ⚠️  Web search failed: {e}")
        
        return "", None
    
    def _build_comprehensive_prompt(self, query: str, conversation_context: Optional[List[Dict]] = None) -> str:
        """
        Build comprehensive prompt with toolbox, conversation, and optional web search tool.
        LLM gets complete freedom to design with access to learned composites and web search.
        """
        
        # Add web search tool availability
        web_search_tool = ""
        if self.web_search:
            web_search_tool = """

═══════════════════════════════════════════════════════════════
**OPTIONAL TOOL: WEB SEARCH**
═══════════════════════════════════════════════════════════════

If you need additional context about specific experiments, techniques, or standard configurations that you're not confident about, you can request a web search.

**To use the tool, include this EXACT format in your response:**
<WEB_SEARCH>your search query here</WEB_SEARCH>

**When to search:**
- Unfamiliar experiment configurations (e.g., "typical Franson interferometer setup")
- Specific technical parameters you're unsure about
- Recent techniques or methods you haven't encountered

**When NOT to search:**
- Standard experiments you know well (Mach-Zehnder, HOM, Bell states)
- Basic quantum optics concepts (beam splitters, phase shifters, etc.)
- Information already available in the toolbox below

**Use sparingly** - most designs don't need web search.
"""
        
        # Load toolbox information
        toolbox_section = ""
        has_composites = False
        if self.use_toolbox and self.toolbox:
            try:
                # Add custom components first
                custom_section = self.toolbox.get_custom_components_for_llm()
                if custom_section:
                    toolbox_section += custom_section
                
                # Then add composites using semantic search
                composites = self.toolbox.list_all_composites()
                if composites and self.retriever:
                    # Use embedding retriever to get only relevant composites (top-5)
                    try:
                        similar_ids = self.retriever.retrieve_similar_composites(query, top_k=5)
                        if similar_ids:
                            has_composites = True
                            toolbox_section += "\n\n**🧰 RELEVANT COMPOSITE BLOCKS (Previous User-Approved Designs):**\n"
                            toolbox_section += "These are proven, human-approved designs similar to your request:\n\n"
                            for comp_id in similar_ids:
                                comp = next((c for c in composites if c['id'] == comp_id), None)
                                if comp:
                                    toolbox_section += f"• **{comp['name']}** (`{comp['id']}`)\n"
                                    toolbox_section += f"  Description: {comp['description']}\n"
                                    toolbox_section += f"  Approved: {comp['approved_date'][:10]}, Components: {comp['num_components']}\n\n"
                    except Exception as e:
                        print(f"Warning: Embedding retrieval failed, falling back to recent composites: {e}")
                        # Fallback: show last 5 composites
                        has_composites = True
                        toolbox_section += "\n\n**🧰 RECENT COMPOSITE BLOCKS (Previous User-Approved Designs):**\n"
                        toolbox_section += "These are proven, human-approved designs from previous sessions:\n\n"
                        for comp in composites[-5:]:
                            toolbox_section += f"• **{comp['name']}** (`{comp['id']}`)\n"
                            toolbox_section += f"  Description: {comp['description']}\n"
                            toolbox_section += f"  Approved: {comp['approved_date'][:10]}, Components: {comp['num_components']}\n\n"
                    
                    toolbox_section += """
**IMPORTANT DECISION RULE:**
1. If one of these composites is a CLOSE MATCH (>80% similarity) to the user's request:
   - Return ONLY: {"use_existing": true, "composite_id": "the_id", "reason": "why it matches"}
   - This will show the user three options: "Use This", "Auto-Improve", or "Generate New"
   
2. If the request is DIFFERENT or requires significant modifications:
   - Generate a NEW design from scratch (normal JSON response)
   - You can still incorporate elements/ideas from the composites if relevant

Example of using existing:
User asks: "Design a Mach Zehnder interferometer"
You see: "Mach-Zehnder Interferometer" composite exists
Response: {"use_existing": true, "composite_id": "mach_zehnder_001", "reason": "Exact match - existing Mach-Zehnder design perfectly matches the request"}

Example of generating new:
User asks: "Design a Mach Zehnder with delay stage for timing measurements"
Response: [Generate NEW design incorporating delay stage - the existing one doesn't have this]

"""
            except Exception as e:
                print(f"Warning: Could not load toolbox composites: {e}")
        
        # Build conversation history section if available
        conversation_section = ""
        if conversation_context and len(conversation_context) > 1:
            # Get last few messages (excluding the current query)
            recent_messages = conversation_context[-6:-1] if len(conversation_context) > 6 else conversation_context[:-1]
            if recent_messages:
                conversation_section = "\n**Recent Conversation Context:**\n"
                for msg in recent_messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        conversation_section += f"User: {content}\n"
                    else:
                        conversation_section += f"Assistant: {content}\n"
                conversation_section += "\n**Current Request:** " + query + "\n\n"
                conversation_section += "IMPORTANT: Design the experiment based on the CURRENT REQUEST above, taking into account the conversation context (e.g., if they asked about EIT and now want you to design it, design an EIT experiment).\n\n---\n\n"
        
        return f"""You are an expert quantum optics experimentalist. Design a complete optical table setup for this request:

{conversation_section if conversation_section else f'"{query}"'}
{web_search_tool}

{toolbox_section}

Provide a detailed JSON design with ALL of the following:

1. **title**: A clear, concise title for the experiment

2. **description**: One-sentence description of what this setup does

3. **components**: Array of optical components on the table, each with:
   - type: Component type from this COMPREHENSIVE list:
     * **Light Sources**: laser, source, point_source
     * **Beam Splitting**: beam_splitter, dichroic_mirror, dichroic, pellicle_beam_splitter, polarizing_beam_splitter, pbs
     * **Mirrors**: mirror, concave_mirror, curved_mirror, faraday_mirror, piezo_mirror
     * **Lenses**: lens, convex_lens, concave_lens, cylindrical_lens
     * **Phase/Polarization**: phase_shifter, polarizer, wave_plate, waveplate, half_wave_plate, hwp, quarter_wave_plate, qwp, rotator, faraday_rotator, pockels_cell
     * **Intensity Control**: filter, attenuator, nd_filter, beam_dump, absorber, isolator, optical_isolator, circulator
     * **Beam Shaping**: aperture, iris, spatial_filter, pinhole, beam_expander, telescope, collimator, spatial_light_modulator, slm, dmd
     * **Nonlinear Optics**: crystal, bbo_crystal, ppln_crystal, ktp_crystal, lbo_crystal, bibo_crystal
     * **Detection**: detector, screen, photodiode, apd, spad, pmt, photomultiplier, snspd, sipm, hpd, homodyne_detector, heterodyne_detector, camera, ccd, cmos
     * **Interference/Diffraction**: slit, double_slit, grating, diffraction_grating, etalon, fabry_perot, prism
     * **Timing/Delay**: delay, delay_stage
     * **Modulation**: modulator, eom, aom
     * **Coupling**: fiber, fiber_coupler
     * **Cavities**: optical_cavity, reference_cavity, ring_cavity, fabry_perot_cavity
     * **Atomic Systems**: vapor_cell, atomic_filter
     * **Measurement**: spectrometer
     * **CUSTOM COMPONENTS** (for components NOT in above list):
       - Use type format: `custom_<descriptive_name>` (e.g., `custom_coincidence_counter`, `custom_timing_unit`, `custom_lc_retarder`)
       - Custom components render as labeled boxes marked with 'C' on the optical table
       - MUST include detailed `description` in parameters explaining what it does
       - Example:
         ```json
         {{
           \"type\": \"custom_coincidence_counter\",
           \"name\": \"4-Ch Coincidence Counter\",
           \"x\": 9.0,
           \"y\": 3.0,
           \"angle\": 0,
           \"parameters\": {{
             \"description\": \"Electronic unit processing 4 SPAD outputs to identify coincidence events within 1ns window\",
             \"channels\": 4,
             \"timing_resolution\": \"1ns\"
           }}
         }}
         ```
       - Use for: coincidence counters, timing electronics, control systems, specialized filters, non-standard equipment
   - name: Descriptive name (e.g., "Pump Laser", "50:50 BS", "PPLN Crystal", "SNSPD Detector")
   - x: X-coordinate on optical table (0-10 range, left to right)
   - y: Y-coordinate on optical table (0-6 range, where HIGHER y = TOP/UPPER, LOWER y = BOTTOM/LOWER)
     * **IMPORTANT**: y=5 is UPPER path, y=1 is LOWER path, y=3 is CENTER
     * For interferometer arms: upper arm uses y≈4-5, lower arm uses y≈1-2
   - angle: Rotation angle in degrees (0 for horizontal/right-facing)
   - parameters: Dict with component-specific values like:
     * For lasers: wavelength (nm), power (mW), linewidth (kHz optional)
     * For beam_splitters: transmittance (0-1), e.g., 0.5 for 50:50, type (e.g., "cube", "pellicle", "polarizing")
     * For crystals: type (e.g., "PPLN", "BBO", "KTP", "LBO", "BiBO"), interaction (e.g., "SPDC", "SHG", "SFG", "DFG"), length (mm), poling_period (μm for PPLN), phase_matching (e.g., "type-I", "type-II")
     * For detectors: type (e.g., "SPAD", "APD", "PMT", "SNSPD", "SiPM", "HPD", "homodyne", "heterodyne"), efficiency (%), dark_count_rate (Hz optional), timing_resolution (ps optional)
     * For slits: spacing (μm), width (μm)
     * For lenses: focal_length (mm), diameter (mm optional)
     * For filters: wavelength (nm), bandwidth (nm), optical_depth (OD optional)
     * For gratings: lines_per_mm, blaze_angle (degrees)
     * For modulators: frequency (MHz), voltage (V), type (e.g., "EOM", "AOM", "Pockels")
     * For waveplates: order (e.g., "zero-order", "multi-order"), wavelength (nm)
     * For pockels_cells: voltage (V), aperture (mm), rise_time (ns)
     * For vapor_cells: atomic_species (e.g., "Rb-87", "Cs-133"), temperature (°C), length (mm)
     * For cavities: finesse, fsr (GHz), length (mm optional), mirror_reflectivity (optional)

4. **beam_path**: Light path(s) through the setup. **CRITICAL: ALL components must appear in at least one beam path!**
   - Single path: [[x, y], [x, y], ...] for simple linear setups
   - Multiple paths: [[[x,y],...], [[x,y],...]] when light takes different routes
   
   **IMPORTANT RULES:**
   - **Every component MUST be connected**: All components must appear in beam paths (source → optics → detector)
   - Beam paths should pass through ALL optical elements, not skip any
   - For components not on main path, add separate paths or branch points
   - Coordinates in beam_path should match component (x, y) positions (within 0.2 units)
   
   **TIP**: Showing multiple distinct light paths makes the physics clearer when:
   - Beams split or diverge (beam splitters, gratings, slits, prisms)
   - Different outputs or detection points exist
   - Light can reach the same component via different routes
   - It helps visualize interference, diffraction, or superposition
   - Example: For Hong-Ou-Mandel with 2 photon arms meeting at BS:
     ```
     "beam_path": [
       [[crystal_x, crystal_y], [mirror1_x, mirror1_y], [bs_x, bs_y], [det1_x, det1_y]],
       [[crystal_x, crystal_y], [mirror2_x, mirror2_y], [bs_x, bs_y], [det2_x, det2_y]]
     ]
     ```
   - Example: For Mach-Zehnder with upper/lower arms:
     ```
     "beam_path": [
       [[laser_x, laser_y], [bs1_x, bs1_y], [upper_mirror_x, upper_mirror_y], [bs2_x, bs2_y], [det_x, det_y]],
       [[laser_x, laser_y], [bs1_x, bs1_y], [lower_mirror_x, lower_mirror_y], [bs2_x, bs2_y], [det_x, det_y]]
     ]
     ```
   - DO NOT concatenate separate physical paths into one array
   - Each photon/beam that can be distinguished gets its own path array

5. **physics_explanation**: Detailed explanation (2-4 sentences) of:
   - What quantum state is prepared
   - How each component modifies the state
   - What physics principle is demonstrated

6. **component_justifications**: A dictionary explaining why each component was chosen and its specific role.
   Format: {{
     "Component Name": "Explanation of why this component is needed and what it does",
     ...
   }}
   Example: {{
     "Pump Laser": "Provides 405nm photons to pump the nonlinear crystal for SPDC process",
     "BBO Crystal": "Type-II SPDC source that generates entangled photon pairs at 810nm",
     "50:50 BS": "Enables Hong-Ou-Mandel interference by bringing both photon paths together",
     "SPAD Detector 1": "Single-photon avalanche photodiode for detecting coincidence events"
   }}

7. **expected_outcome**: What measurements/results would you expect from this setup

**Design Guidelines:**
- Use realistic optical table coordinates (spread components out, typical spacing 1-3 units)
- Ensure beam paths are physically realistic (light travels in straight lines or reflects)
- When multiple light paths would clarify the physics, show them (makes visualization more informative)

**Common Interferometer Layouts:**
- **Michelson**: Source (left, ~x=1) → BS (center, ~x=4, y=3) → Mirror1 (right, ~x=7) & Mirror2 (top, y=5) → back to BS → Detector (bottom or output port, ~y=1)
- **Mach-Zehnder**: Source → BS1 → Upper arm (mirrors/phase shifter) → BS2 → Detectors at outputs (forward flow)
- **HOM/SPDC**: Source → Optics → BS → Detectors at both output ports (forward flow)

**CRITICAL JSON FORMATTING RULES:**
- Return ONLY valid JSON - no markdown, no extra text, just the JSON object
- All strings must use escaped quotes if they contain quotes: use \\" not "
- Multi-line text must use \\n not actual newlines
- No trailing commas after last item in arrays or objects
- Ensure all braces and brackets are properly closed

Example format:
{{
  "title": "Bell State Generator",
  "description": "Creates maximally entangled photon pairs via SPDC",
  "components": [
    {{
      "type": "laser",
      "name": "Pump Laser",
      "x": 1.0,
      "y": 3.0,
      "angle": 0,
      "parameters": {{"wavelength": 405, "power": 100}}
    }},
    {{
      "type": "crystal",
      "name": "BBO Crystal",
      "x": 3.0,
      "y": 3.0,
      "angle": 0,
      "parameters": {{"type": "BBO", "interaction": "SPDC"}}
    }},
    {{
      "type": "detector",
      "name": "Detector A",
      "x": 6.0,
      "y": 2.0,
      "angle": 0,
      "parameters": {{"type": "SPAD"}}
    }},
    {{
      "type": "detector",
      "name": "Detector B",
      "x": 6.0,
      "y": 4.0,
      "angle": 0,
      "parameters": {{"type": "SPAD"}}
    }}
  ],
  "beam_path": [
    [[1.0, 3.0], [3.0, 3.0], [6.0, 2.0]],
    [[1.0, 3.0], [3.0, 3.0], [6.0, 4.0]]
  ],
  "physics_explanation": "Pump photons undergo spontaneous parametric down-conversion in BBO crystal, creating entangled photon pairs. Conservation of energy and momentum ensures the photons are in a Bell state |ψ⟩ = (|HV⟩ + |VH⟩)/√2. Coincidence detection at both detectors verifies entanglement.",
  "component_justifications": {{
    "Pump Laser": "405nm pump laser provides the energy for SPDC process - blue photons split into two red photons",
    "BBO Crystal": "Type-II Beta Barium Borate crystal generates entangled photon pairs through spontaneous parametric down-conversion",
    "Detector A": "Single-photon avalanche photodiode (SPAD) measures arrival times of photons in upper path",
    "Detector B": "Second SPAD detector for lower path enables coincidence counting to verify entanglement"
  }},
  "expected_outcome": "Coincidence counts violate Bell inequality, confirming quantum entanglement"
}}

Now design the experiment for: "{query}"
"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with error recovery."""
        
        # Try to find JSON in response
        text = response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        text = text.strip()
        
        # Try to parse JSON
        try:
            design = json.loads(text)
            return design
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"   Error at position {e.pos}: {text[max(0, e.pos-50):min(len(text), e.pos+50)]}")
            
            # Attempt to repair common issues
            # 1. Try to find complete JSON by looking for matching braces
            brace_count = 0
            last_valid_pos = 0
            for i, char in enumerate(text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_valid_pos = i + 1
                        break
            
            if last_valid_pos > 0 and last_valid_pos < len(text):
                print(f"   Attempting to use truncated JSON (first {last_valid_pos} chars)")
                try:
                    design = json.loads(text[:last_valid_pos])
                    print(f"✅ Successfully parsed truncated JSON")
                    return design
                except json.JSONDecodeError:
                    pass
            
            # If repair failed, re-raise original error
            raise
    
    def _extract_and_save_custom_components(self, design: Dict[str, Any]) -> None:
        """
        Extract custom components from design and save to toolbox for future reuse.
        Called automatically after successful design generation.
        
        Args:
            design: The parsed design dictionary
        """
        try:
            components = design.get('components', [])
            custom_found = []
            
            for comp in components:
                comp_type = comp.get('type', '')
                
                # Check if this is a custom component
                if comp_type.startswith('custom_'):
                    name = comp.get('name', comp_type)
                    description = comp.get('parameters', {}).get('description', 'Custom component')
                    parameters = comp.get('parameters', {})
                    
                    # Save to toolbox
                    success = self.toolbox.add_custom_component(
                        component_type=comp_type,
                        name=name,
                        description=description,
                        parameters=parameters
                    )
                    
                    if success:
                        custom_found.append(comp_type)
            
            if custom_found:
                print(f"📦 Saved {len(custom_found)} custom component(s) to toolbox: {', '.join(custom_found)}")
                
        except Exception as e:
            print(f"⚠️  Failed to extract custom components: {e}")
            # Non-critical error - don't block design return

    def _has_valid_structure(self, design: Dict[str, Any]) -> bool:
        """Check if design has required fields."""
        
        required_fields = ['title', 'components']
        if not all(field in design for field in required_fields):
            return False
        
        # Check components structure
        components = design.get('components', [])
        if not components:
            return False
        
        for comp in components:
            if 'type' not in comp or 'x' not in comp or 'y' not in comp:
                return False
        
        return True

    def _validate_design(self, query: str, design: Dict[str, Any], design_json: str) -> tuple[bool, str]:
        """
        Use LLM to validate the design for physics accuracy and completeness.
        Returns (is_valid, feedback_message)
        """
        # First, check for disconnected components programmatically
        from simple_optical_table import check_disconnected_components
        
        steps = design.get('components', [])
        beam_paths = design.get('beam_path', [])
        disconnected = check_disconnected_components(steps, beam_paths if isinstance(beam_paths[0][0], list) else [beam_paths] if beam_paths else [])
        
        disconnected_warning = ""
        if disconnected:
            disconnected_warning = f"\n\n**CRITICAL ISSUE - DISCONNECTED COMPONENTS:**\nThe following components are NOT connected by any beam path: {', '.join(disconnected)}\nYou MUST add beam path segments that pass through these components (within 0.3 units of their positions).\n"
        
        validation_prompt = f"""You are a quantum optics expert reviewing an experimental design for PHYSICAL CORRECTNESS.

ORIGINAL REQUEST:
{query}

PROPOSED DESIGN:
{design_json}
{disconnected_warning}

**CRITICAL VALIDATION CHECKS - ALL MUST PASS:**

1. **OPTICAL PATH LOGIC AND COMPONENT ORDERING**:
   - Trace light through the beam_path arrays step by step
   - Does light flow through components in the PHYSICALLY CORRECT ORDER for this experiment?
   - Are component (x, y) coordinates positioned WHERE the beam path actually goes?
   
   Examples of CORRECT designs:
   * **HOM**: SPDC crystal (x=2, y=3) → beam paths split → both go to BS (x=5, y=3) → Detectors at BS outputs (x=6, y=4) and (x=6, y=2)
   * **Bell state**: Pump laser (x=1, y=3) → Crystal (x=3, y=3) → entangled pairs split → Det1 (x=6, y=4), Det2 (x=6, y=2)
   * **Mach-Zehnder**: Source (x=1, y=3) → BS1 (x=3, y=3) → Upper mirror (x=5, y=5) & Lower mirror (x=5, y=1) → BS2 (x=7, y=3) → Detectors
   * **Michelson**: Source (x=1, y=3) → BS (x=4, y=3) → Mirror1 (x=7, y=3) & Mirror2 (x=4, y=6) → back to BS → Detector at output (x=4, y=1)
   
   Examples of WRONG designs:
   * **WRONG ORDERING**: BS before photon source (photons must exist first!), Detector before interference point
   * **WRONG PLACEMENT**: Crystal at x=5 but beam_path shows photons starting at x=2 (mismatch!)
   * **WRONG SPACING**: HOM with detector at x=3 when BS is at x=5 (detector should be AFTER BS, e.g., x=6+)
   * **WRONG GEOMETRY**: Michelson with detector back at source instead of at BS output port
   
   **CHECK**: 
   - Does beam_path sequence match the physical causality of the experiment?
   - Are components placed at coordinates that align with where light actually travels?
   - Do component positions enable the stated physics?

2. **COMPONENT CONNECTIVITY**:
   - Every component MUST appear in at least one beam_path
   - Beam path coordinates should pass through/near (±0.4 units) each component's (x, y)
   - No "floating" components that light never reaches
   - Components should be spaced appropriately (typically 1-3 units apart for realistic optical table)
   
   **CHECK**: Are all components actually on the light path at their stated coordinates?

3. **EXPERIMENT-SPECIFIC REQUIREMENTS**:
   - Does the spatial layout enable the SPECIFIC physics requested?
   - **HOM**: Two photons must reach BS from different inputs, detectors at BOTH outputs
   - **Bell state**: Entangled pairs must be separated and routed to DIFFERENT detectors
   - **Interferometer**: Two paths must travel different routes then RECOMBINE, detector AFTER recombination
   - **Quantum eraser**: Separate paths for which-path encoding AND erasure, multiple detection stages
   
   **CHECK**: Does component placement + beam routing physically enable this experiment?

4. **SPATIAL CONSISTENCY**:
   - Do the (x, y) coordinates make physical sense?
   - Components should be positioned where the beam_path coordinates actually pass
   - No impossible jumps (e.g., beam goes to x=5 but next component is at x=2)
   - Reasonable spacing (not all components at same location, not impossibly far apart)
   
   **CHECK**: Is there geometric consistency between components and beam paths?

5. **REALISTIC PARAMETERS**:
   - Wavelengths match experiment (SPDC: 405nm pump → 810nm pairs, HeNe: 632.8nm, etc.)
   - Component specs are physically reasonable
   - Beam splitter ratios appropriate (50:50 for interference, other ratios for specific needs)
   
   **CHECK**: Are all parameters physically realistic?

6. **COMPLETENESS**:
   - All essential components present?
   - Source(s), optical elements, detector(s) all included?
   
   **CHECK**: Anything critical missing?

RESPOND WITH JSON ONLY:
{{
    "verdict": "accept" or "refine",
    "reasoning": "Brief explanation of your decision",
    "issues": ["List of specific issues if verdict is refine, empty array if accept"]
}}

**KEY PRINCIPLE**: Correct beam path ordering AND correct component placement are BOTH required.
A design with correct ordering but wrong coordinates needs refinement (components aren't where light goes).
A design with correct coordinates but wrong ordering needs refinement (physics is violated).

Only use "accept" if the design will actually work as proposed.
Use "refine" if any critical issues need fixing.

Return ONLY the JSON, no other text."""

        try:
            validation_response = self.llm.predict(validation_prompt)
            
            # Parse JSON response
            try:
                # Extract JSON if wrapped in markdown code blocks
                if '```json' in validation_response:
                    json_str = validation_response.split('```json')[1].split('```')[0].strip()
                elif '```' in validation_response:
                    json_str = validation_response.split('```')[1].split('```')[0].strip()
                else:
                    json_str = validation_response.strip()
                
                verdict_data = json.loads(json_str)
                verdict = verdict_data.get('verdict', '').lower()
                reasoning = verdict_data.get('reasoning', '')
                issues = verdict_data.get('issues', [])
                
                if verdict == 'accept':
                    return True, reasoning
                elif verdict == 'refine':
                    feedback = reasoning
                    if issues:
                        feedback += "\n\nSpecific issues:\n" + "\n".join(f"- {issue}" for issue in issues)
                    return False, feedback
                else:
                    print(f"⚠️  Unknown verdict: {verdict}, defaulting to refinement")
                    return False, validation_response
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse validation JSON: {e}")
                print(f"Response was: {validation_response[:200]}...")
                # Fallback to text parsing
                response_upper = validation_response.upper()
                if "VERDICT: ACCEPT" in response_upper or validation_response.strip().upper().startswith("VALID"):
                    return True, validation_response
                else:
                    return False, validation_response
        
        except Exception as e:
            print(f"⚠️  Validation error: {e}, assuming design is valid")
            return True, "Validation skipped due to error"
    
    def _build_refinement_prompt(self, query: str, previous_design: str, feedback: str) -> str:
        """Build prompt to refine the design based on validation feedback."""
        
        return f"""You are a quantum optics expert. You previously designed an experiment but it had some issues.

ORIGINAL REQUEST:
{query}

YOUR PREVIOUS DESIGN:
{previous_design}

REVIEWER FEEDBACK (issues to fix):
{feedback}

Please provide an IMPROVED design that addresses ALL the feedback points.
Return ONLY the corrected JSON design (same format as before), no extra text.

{self._build_comprehensive_prompt(query).split('Provide a detailed JSON design')[1]}"""
    
    def _emergency_fallback(self, query: str) -> OpticalSetup:
        """Simple fallback if LLM fails completely."""
        
        query_lower = query.lower()
        
        if 'bell' in query_lower or 'entangle' in query_lower:
            return OpticalSetup(
                title="Bell State via Beam Splitter",
                description="Single photon through 50:50 beam splitter creates spatial entanglement",
                components=[
                    {
                        "type": "laser",
                        "name": "Single Photon Source",
                        "x": 1.0,
                        "y": 3.0,
                        "angle": 0,
                        "parameters": {"wavelength": 810, "power": 0.001}
                    },
                    {
                        "type": "beam_splitter",
                        "name": "50:50 BS",
                        "x": 4.0,
                        "y": 3.0,
                        "angle": 45,
                        "parameters": {"transmittance": 0.5}
                    },
                    {
                        "type": "detector",
                        "name": "Detector A",
                        "x": 7.0,
                        "y": 2.0,
                        "angle": 0,
                        "parameters": {"type": "SPAD"}
                    },
                    {
                        "type": "detector",
                        "name": "Detector B",
                        "x": 7.0,
                        "y": 4.0,
                        "angle": 0,
                        "parameters": {"type": "SPAD"}
                    }
                ],
                beam_path=[(1.0, 3.0), (4.0, 3.0), (7.0, 2.0), (7.0, 4.0)],
                physics_explanation="A single photon in Fock state |1,0⟩ enters a 50:50 beam splitter, creating the superposition (|1,0⟩ + |0,1⟩)/√2. This is a Bell state showing perfect spatial entanglement between the two output modes.",
                expected_outcome="Perfect anti-correlation: detectors never click simultaneously, demonstrating quantum superposition",
                component_justifications={}
            )
        else:
            return OpticalSetup(
                title="Simple Laser Setup",
                description="Basic coherent light source and detection",
                components=[
                    {
                        "type": "laser",
                        "name": "Laser",
                        "x": 2.0,
                        "y": 3.0,
                        "angle": 0,
                        "parameters": {"wavelength": 810, "power": 1.0}
                    },
                    {
                        "type": "detector",
                        "name": "Detector",
                        "x": 6.0,
                        "y": 3.0,
                        "angle": 0,
                        "parameters": {"type": "photodiode"}
                    }
                ],
                beam_path=[(2.0, 3.0), (6.0, 3.0)],
                physics_explanation="Coherent light from laser propagates to detector",
                expected_outcome="Continuous photon detection",
                component_justifications={}
            )
    
    def _convert_stored_to_optical_setup(self, stored_data: Dict) -> OpticalSetup:
        """
        Convert a stored experiment from memory back to OpticalSetup format.
        
        Args:
            stored_data: Experiment data retrieved from memory
            
        Returns:
            OpticalSetup object
        """
        try:
            # Extract components - handle both old and new formats
            components = stored_data.get('components', [])
            if not components:
                # Try getting from experiment.steps
                components = stored_data.get('experiment', {}).get('steps', [])
            
            setup = OpticalSetup(
                title=stored_data.get('title', 'Retrieved Experiment'),
                description=stored_data.get('description', ''),
                components=components,
                beam_path=stored_data.get('beam_path', []),
                physics_explanation=stored_data.get('physics_explanation', ''),
                expected_outcome=stored_data.get('expected_outcome', ''),
                component_justifications=stored_data.get('component_justifications', {}),
                raw_llm_response="[Retrieved from memory - not generated]",
                parsed_design_json=stored_data,
                web_search_used=False,
                web_search_context=""
            )
            
            # Attach metadata about retrieval
            setup.from_memory = True
            setup.memory_metadata = {
                'similarity_score': stored_data.get('_similarity_score', 0),
                'source_query': stored_data.get('_source_query', ''),
                'human_approved': stored_data.get('human_approved', False),
                'verdict': stored_data.get('verdict', 'unknown'),
                'confidence': stored_data.get('confidence', 0)
            }
            
            print(f"✅ Converted stored experiment to OpticalSetup")
            print(f"   Retrieved: {setup.title}")
            print(f"   Similarity: {setup.memory_metadata['similarity_score']:.2f}")
            print(f"   Components: {len(setup.components)}")
            
            return setup
            
        except Exception as e:
            print(f"❌ Failed to convert stored experiment: {e}")
            import traceback
            traceback.print_exc()
            # Return a simple fallback
            return self._emergency_fallback("Retrieved experiment conversion failed")


def _normalize_beam_path(raw):
    """Normalize beam_path to be a list of paths.

    Accepts:
    - None or [] -> []
    - single path: [[x,y], [x,y], ...] -> detect jumps and split into multiple paths
    - multiple paths: [ [[x,y],...], [[x,y],...] ] -> unchanged
    
    Smart splitting: If we see a large spatial jump (>2 units), split into separate paths.
    This handles cases where LLM concatenates multiple arms of an interferometer.
    """
    if not raw:
        return []
    
    # Check if it's already a list of paths (nested lists)
    if isinstance(raw, list) and raw and isinstance(raw[0], list):
        # Check if first element is a coordinate pair [x,y] or a path [[x,y],...]
        if isinstance(raw[0][0], (int, float)):
            # It's a single path: [[x,y], [x,y], ...]
            # Need to detect and split on large jumps
            path = raw
            paths = []
            current_path = [path[0]]
            
            for i in range(1, len(path)):
                prev_x, prev_y = path[i-1]
                curr_x, curr_y = path[i]
                
                # Calculate distance between consecutive points
                distance = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
                
                # If distance is large (>3 units), likely a jump to new path
                # Typical optical table spacing is 1-2 units between adjacent components
                if distance > 3.0:
                    # End current path and start new one
                    paths.append(current_path)
                    current_path = [path[i]]
                else:
                    current_path.append(path[i])
            
            # Add final path
            if current_path:
                paths.append(current_path)
            
            return paths if len(paths) > 1 else [path]  # Return split paths or original wrapped
        else:
            # Already a list of paths: [[[x,y],...], [[x,y],...]]
            return raw
    
    return []


# Example usage / testing
if __name__ == "__main__":
    class MockLLM:
        def predict(self, prompt):
            return """```json
{
  "title": "Bell State Generator",
  "description": "Creates Bell state",
  "components": [
    {
      "type": "laser",
      "name": "Source",
      "x": 1.0,
      "y": 3.0,
      "angle": 0,
      "parameters": {"wavelength": 810, "power": 0.001}
    },
    {
      "type": "beam_splitter",
      "name": "50:50 BS",
      "x": 4.0,
      "y": 3.0,
      "angle": 45,
      "parameters": {"transmittance": 0.5}
    },
    {
      "type": "detector",
      "name": "Det A",
      "x": 7.0,
      "y": 2.0,
      "angle": 0,
      "parameters": {"type": "SPAD"}
    }
  ],
  "beam_path": [[[1.0, 3.0], [4.0, 3.0], [7.0, 2.0]]],
  "physics_explanation": "Creates Bell state via beam splitter",
  "expected_outcome": "Entanglement"
}
```"""
    
    designer = LLMDesigner(MockLLM())
    result = designer.design_experiment("Design a Bell state")
    
    print(f"\nTitle: {result.title}")
    print(f"Components: {len(result.components)}")
    for comp in result.components:
        print(f"  - {comp['name']} at ({comp['x']}, {comp['y']})")
    print(f"\nExplanation: {result.physics_explanation}")
