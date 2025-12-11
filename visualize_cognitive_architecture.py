"""
Visualization script for Aṇubuddhi cognitive architecture
Generates publication-quality diagrams showing the three-layer pipeline and agent interactions
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.patheffects import withStroke
import numpy as np

# Set publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['figure.dpi'] = 300

def create_three_layer_architecture():
    """
    Visualize the three-layer cognitive pipeline:
    Layer 1: Conversational Intelligence
    Layer 2: Knowledge-Augmented Design
    Layer 3: Dual-Mode Validation
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Color scheme - warm professional colors
    color_conversation = '#6B9BD1'  # Soft blue
    color_design = '#E8A87C'  # Warm orange
    color_validation = '#7BC96F'  # Fresh green
    color_support = '#B19CD9'  # Lavender
    color_user = '#F4A6A3'  # Coral
    
    # Title
    ax.text(7, 9.5, 'Aṇubuddhi Cognitive Architecture', 
            ha='center', va='top', fontsize=18, fontweight='bold')
    ax.text(7, 9.0, 'Three-Layer Hierarchical Processing Pipeline',
            ha='center', va='top', fontsize=12, style='italic', color='#555')
    
    # === USER INTERFACE (Top) ===
    user_box = FancyBboxPatch((5.5, 8.0), 3, 0.6,
                              boxstyle="round,pad=0.1",
                              edgecolor=color_user, facecolor=color_user,
                              linewidth=2, alpha=0.7)
    ax.add_patch(user_box)
    ax.text(7, 8.3, 'User Interface (Streamlit)', 
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.text(7, 8.0, 'Natural Language Input / Visual Feedback',
            ha='center', va='center', fontsize=8, color='white', style='italic')
    
    # === LAYER 1: CONVERSATIONAL INTELLIGENCE ===
    layer1_y = 6.8
    
    # Main box
    layer1_box = FancyBboxPatch((0.5, layer1_y - 0.3), 13, 1.0,
                                boxstyle="round,pad=0.15",
                                edgecolor=color_conversation, facecolor=color_conversation,
                                linewidth=2.5, alpha=0.15)
    ax.add_patch(layer1_box)
    
    # Layer label
    ax.text(0.8, layer1_y + 0.5, 'Layer 1', ha='left', va='center',
            fontsize=14, fontweight='bold', color=color_conversation)
    ax.text(0.8, layer1_y + 0.2, 'Conversational\nIntelligence', ha='left', va='center',
            fontsize=10, color=color_conversation)
    
    # Intent Router
    router_box = FancyBboxPatch((3.5, layer1_y - 0.1), 2.5, 0.7,
                                boxstyle="round,pad=0.1",
                                edgecolor=color_conversation, facecolor='white',
                                linewidth=2, alpha=0.9)
    ax.add_patch(router_box)
    ax.text(4.75, layer1_y + 0.4, 'Intent Router', ha='center', va='center',
            fontsize=10, fontweight='bold', color=color_conversation)
    ax.text(4.75, layer1_y + 0.1, 'LLM + Fallback', ha='center', va='center',
            fontsize=8, color='#555')
    
    # Decision branches
    # Chat branch
    chat_box = FancyBboxPatch((7.0, layer1_y - 0.1), 2.0, 0.7,
                              boxstyle="round,pad=0.1",
                              edgecolor=color_conversation, facecolor='white',
                              linewidth=1.5, alpha=0.9)
    ax.add_patch(chat_box)
    ax.text(8.0, layer1_y + 0.4, 'Chat Mode', ha='center', va='center',
            fontsize=9, fontweight='bold', color=color_conversation)
    ax.text(8.0, layer1_y + 0.1, '(Q&A, Explain)', ha='center', va='center',
            fontsize=7, color='#555')
    
    # Design branch
    design_branch = FancyBboxPatch((10.0, layer1_y - 0.1), 2.0, 0.7,
                                   boxstyle="round,pad=0.1",
                                   edgecolor=color_conversation, facecolor='white',
                                   linewidth=1.5, alpha=0.9)
    ax.add_patch(design_branch)
    ax.text(11.0, layer1_y + 0.4, 'Design Mode', ha='center', va='center',
            fontsize=9, fontweight='bold', color=color_conversation)
    ax.text(11.0, layer1_y + 0.1, '(Create, Modify)', ha='center', va='center',
            fontsize=7, color='#555')
    
    # Arrows from router
    arrow1 = FancyArrowPatch((6.0, layer1_y + 0.25), (7.0, layer1_y + 0.25),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color=color_conversation)
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((6.0, layer1_y + 0.25), (10.0, layer1_y + 0.25),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color=color_conversation)
    ax.add_patch(arrow2)
    
    # Arrow from user to router
    user_to_router = FancyArrowPatch((7, 8.0), (4.75, layer1_y + 0.65),
                                     arrowstyle='->', mutation_scale=25, linewidth=2.5,
                                     color='#888', alpha=0.7)
    ax.add_patch(user_to_router)
    
    # === LAYER 2: KNOWLEDGE-AUGMENTED DESIGN ===
    layer2_y = 4.5
    
    # Main box
    layer2_box = FancyBboxPatch((0.5, layer2_y - 0.8), 13, 1.8,
                                boxstyle="round,pad=0.15",
                                edgecolor=color_design, facecolor=color_design,
                                linewidth=2.5, alpha=0.15)
    ax.add_patch(layer2_box)
    
    # Layer label
    ax.text(0.8, layer2_y + 0.7, 'Layer 2', ha='left', va='center',
            fontsize=14, fontweight='bold', color=color_design)
    ax.text(0.8, layer2_y + 0.35, 'Knowledge-\nAugmented\nDesign', ha='left', va='center',
            fontsize=10, color=color_design)
    
    # Design Generator
    generator_box = FancyBboxPatch((3.5, layer2_y + 0.1), 3.0, 0.8,
                                   boxstyle="round,pad=0.1",
                                   edgecolor=color_design, facecolor='white',
                                   linewidth=2, alpha=0.9)
    ax.add_patch(generator_box)
    ax.text(5.0, layer2_y + 0.7, 'LLM Designer Agent', ha='center', va='center',
            fontsize=10, fontweight='bold', color=color_design)
    ax.text(5.0, layer2_y + 0.4, 'Component Selection', ha='center', va='center',
            fontsize=8, color='#555')
    ax.text(5.0, layer2_y + 0.2, 'Spatial Layout Planning', ha='center', va='center',
            fontsize=8, color='#555')
    
    # Memory System (left support)
    memory_box = FancyBboxPatch((3.5, layer2_y - 0.6), 3.0, 0.5,
                                boxstyle="round,pad=0.08",
                                edgecolor=color_support, facecolor=color_support,
                                linewidth=1.5, alpha=0.3)
    ax.add_patch(memory_box)
    ax.text(5.0, layer2_y - 0.25, 'Memory System (RAG)', ha='center', va='center',
            fontsize=9, fontweight='bold', color=color_support)
    ax.text(5.0, layer2_y - 0.45, 'ONNX MiniLM-L6-V2 + ChromaDB', ha='center', va='center',
            fontsize=7, color=color_support)
    
    # Toolbox (right support)
    toolbox_box = FancyBboxPatch((7.5, layer2_y - 0.6), 3.0, 0.5,
                                 boxstyle="round,pad=0.08",
                                 edgecolor=color_support, facecolor=color_support,
                                 linewidth=1.5, alpha=0.3)
    ax.add_patch(toolbox_box)
    ax.text(9.0, layer2_y - 0.25, 'Toolbox System', ha='center', va='center',
            fontsize=9, fontweight='bold', color=color_support)
    ax.text(9.0, layer2_y - 0.45, 'Primitives + Composites', ha='center', va='center',
            fontsize=7, color=color_support)
    
    # Arrows from supports to generator
    mem_arrow = FancyArrowPatch((5.0, layer2_y - 0.05), (5.0, layer2_y + 0.1),
                               arrowstyle='->', mutation_scale=15, linewidth=1.5,
                               color=color_support, linestyle='--', alpha=0.6)
    ax.add_patch(mem_arrow)
    
    tool_arrow = FancyArrowPatch((9.0, layer2_y - 0.05), (6.2, layer2_y + 0.1),
                                arrowstyle='->', mutation_scale=15, linewidth=1.5,
                                color=color_support, linestyle='--', alpha=0.6)
    ax.add_patch(tool_arrow)
    
    # Arrow from Layer 1 to Layer 2
    layer12_arrow = FancyArrowPatch((11.0, layer1_y - 0.1), (5.0, layer2_y + 0.9),
                                   arrowstyle='->', mutation_scale=25, linewidth=2.5,
                                   color='#888', alpha=0.7)
    ax.add_patch(layer12_arrow)
    ax.text(8.2, 5.8, 'Design Request', ha='center', va='center',
            fontsize=8, style='italic', color='#666')
    
    # === LAYER 3: DUAL-MODE VALIDATION ===
    layer3_y = 1.8
    
    # Main box
    layer3_box = FancyBboxPatch((0.5, layer3_y - 0.8), 13, 1.8,
                                boxstyle="round,pad=0.15",
                                edgecolor=color_validation, facecolor=color_validation,
                                linewidth=2.5, alpha=0.15)
    ax.add_patch(layer3_box)
    
    # Layer label
    ax.text(0.8, layer3_y + 0.7, 'Layer 3', ha='left', va='center',
            fontsize=14, fontweight='bold', color=color_validation)
    ax.text(0.8, layer3_y + 0.35, 'Dual-Mode\nValidation', ha='left', va='center',
            fontsize=10, color=color_validation)
    
    # Tool-based path (left)
    tool_sim_box = FancyBboxPatch((3.5, layer3_y + 0.1), 2.8, 0.8,
                                  boxstyle="round,pad=0.1",
                                  edgecolor=color_validation, facecolor='white',
                                  linewidth=2, alpha=0.9)
    ax.add_patch(tool_sim_box)
    ax.text(4.9, layer3_y + 0.65, 'Tool-Based', ha='center', va='center',
            fontsize=10, fontweight='bold', color=color_validation)
    ax.text(4.9, layer3_y + 0.4, 'SimulationAgent', ha='center', va='center',
            fontsize=8, color='#555')
    ax.text(4.9, layer3_y + 0.2, 'PhotonicToolbox', ha='center', va='center',
            fontsize=7, color='#555', style='italic')
    
    # Free-form path (right)
    free_sim_box = FancyBboxPatch((7.7, layer3_y + 0.1), 2.8, 0.8,
                                  boxstyle="round,pad=0.1",
                                  edgecolor=color_validation, facecolor='white',
                                  linewidth=2, alpha=0.9)
    ax.add_patch(free_sim_box)
    ax.text(9.1, layer3_y + 0.65, 'Free-Form', ha='center', va='center',
            fontsize=10, fontweight='bold', color=color_validation)
    ax.text(9.1, layer3_y + 0.4, 'FreeFormSimAgent', ha='center', va='center',
            fontsize=8, color='#555')
    ax.text(9.1, layer3_y + 0.2, 'Code Generation', ha='center', va='center',
            fontsize=7, color='#555', style='italic')
    
    # Refinement loops
    ax.annotate('', xy=(4.0, layer3_y + 0.1), xytext=(4.0, layer3_y - 0.3),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=color_validation, 
                               linestyle=':', alpha=0.6))
    ax.annotate('', xy=(4.2, layer3_y - 0.3), xytext=(4.2, layer3_y + 0.1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=color_validation,
                               linestyle=':', alpha=0.6))
    ax.text(3.6, layer3_y - 0.45, 'Max 3\nIterations', ha='center', va='center',
            fontsize=7, color=color_validation, style='italic')
    
    ax.annotate('', xy=(9.5, layer3_y + 0.1), xytext=(9.5, layer3_y - 0.3),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=color_validation,
                               linestyle=':', alpha=0.6))
    ax.annotate('', xy=(9.7, layer3_y - 0.3), xytext=(9.7, layer3_y + 0.1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=color_validation,
                               linestyle=':', alpha=0.6))
    ax.text(10.2, layer3_y - 0.45, 'Convergent\nRefinement', ha='center', va='center',
            fontsize=7, color=color_validation, style='italic')
    
    # Arrow from Layer 2 to Layer 3
    layer23_arrow = FancyArrowPatch((5.0, layer2_y + 0.1), (7.0, layer3_y + 0.9),
                                   arrowstyle='->', mutation_scale=25, linewidth=2.5,
                                   color='#888', alpha=0.7)
    ax.add_patch(layer23_arrow)
    ax.text(5.8, 3.3, 'Validate Design', ha='center', va='center',
            fontsize=8, style='italic', color='#666')
    
    # Feedback arrow back to Layer 2
    feedback_arrow = FancyArrowPatch((9.1, layer3_y + 0.9), (6.3, layer2_y + 0.1),
                                    arrowstyle='->', mutation_scale=20, linewidth=2,
                                    color='#d9534f', linestyle='--', alpha=0.6)
    ax.add_patch(feedback_arrow)
    ax.text(8.2, 3.3, 'Refinement\nFeedback', ha='center', va='center',
            fontsize=7, style='italic', color='#d9534f')
    
    # === FINAL OUTPUT ===
    output_box = FancyBboxPatch((5.0, 0.2), 4.0, 0.6,
                                boxstyle="round,pad=0.1",
                                edgecolor='#2ecc71', facecolor='#d5f4e6',
                                linewidth=2, alpha=0.8)
    ax.add_patch(output_box)
    ax.text(7.0, 0.5, 'Validated Experimental Design', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#27ae60')
    ax.text(7.0, 0.25, 'Optical Layout + Simulation Results', ha='center', va='center',
            fontsize=8, color='#555', style='italic')
    
    # Arrow from validation to output
    final_arrow = FancyArrowPatch((7.0, layer3_y + 0.1), (7.0, 0.8),
                                 arrowstyle='->', mutation_scale=25, linewidth=2.5,
                                 color='#27ae60', alpha=0.7)
    ax.add_patch(final_arrow)
    
    # Legend showing data flow
    ax.text(12.0, 0.5, 'Data Flow:', ha='left', va='top',
            fontsize=9, fontweight='bold', color='#333')
    ax.plot([12.0, 12.4], [0.3, 0.3], color='#888', linewidth=2.5, alpha=0.7)
    ax.text(12.5, 0.3, 'Forward', ha='left', va='center', fontsize=7, color='#555')
    ax.plot([12.0, 12.4], [0.1, 0.1], color='#d9534f', linewidth=2, 
            linestyle='--', alpha=0.6)
    ax.text(12.5, 0.1, 'Feedback', ha='left', va='center', fontsize=7, color='#555')
    
    plt.tight_layout()
    plt.savefig('paper/fig_cognitive_architecture.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('paper/fig_cognitive_architecture.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: fig_cognitive_architecture.pdf/png")
    plt.close()


def create_agent_communication_flow():
    """
    Detailed view of how agents communicate through structured data exchange
    Shows the OpticalSetup dataclass and message passing protocol
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    color_user = '#F4A6A3'
    color_llm = '#E8A87C'
    color_sim = '#7BC96F'
    color_data = '#FFD700'
    
    # Title
    ax.text(6, 9.5, 'Agent Communication Protocol', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    ax.text(6, 9.0, 'Request-Response Architecture with Structured Data Exchange',
            ha='center', va='top', fontsize=11, style='italic', color='#555')
    
    # === Timeline view of agent interactions ===
    
    # User
    user_circle = Circle((2, 7.5), 0.4, color=color_user, ec='black', linewidth=2)
    ax.add_patch(user_circle)
    ax.text(2, 7.5, 'User', ha='center', va='center', fontsize=9, 
            fontweight='bold', color='white')
    
    # LLM Designer
    llm_circle = Circle((6, 7.5), 0.4, color=color_llm, ec='black', linewidth=2)
    ax.add_patch(llm_circle)
    ax.text(6, 7.5, 'LLM\nDesigner', ha='center', va='center', fontsize=8,
            fontweight='bold', color='white')
    
    # Simulation Agent
    sim_circle = Circle((10, 7.5), 0.4, color=color_sim, ec='black', linewidth=2)
    ax.add_patch(sim_circle)
    ax.text(10, 7.5, 'Simulation\nAgent', ha='center', va='center', fontsize=8,
            fontweight='bold', color='white')
    
    # Vertical timelines
    ax.plot([2, 2], [7.0, 1.0], 'k--', alpha=0.3, linewidth=1)
    ax.plot([6, 6], [7.0, 1.0], 'k--', alpha=0.3, linewidth=1)
    ax.plot([10, 10], [7.0, 1.0], 'k--', alpha=0.3, linewidth=1)
    
    # === Interaction sequence ===
    y = 6.5
    
    # 1. User sends query
    arrow1 = FancyArrowPatch((2.4, y), (5.6, y),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#333')
    ax.add_patch(arrow1)
    ax.text(4.0, y + 0.2, 'Natural Language Query', ha='center', va='bottom',
            fontsize=8, color='#333', bbox=dict(boxstyle='round,pad=0.3',
                                                facecolor='white', alpha=0.8))
    ax.text(4.0, y - 0.2, '"Design HOM interferometer"', ha='center', va='top',
            fontsize=7, style='italic', color='#666')
    
    # 2. LLM generates design
    y -= 1.2
    design_box = FancyBboxPatch((5.5, y - 0.3), 1.0, 0.6,
                                boxstyle="round,pad=0.05",
                                edgecolor=color_llm, facecolor=color_llm,
                                linewidth=1.5, alpha=0.5)
    ax.add_patch(design_box)
    ax.text(6, y, 'Generate\nDesign', ha='center', va='center',
            fontsize=7, color='white', fontweight='bold')
    
    # 3. Send OpticalSetup to Simulation
    y -= 0.8
    arrow2 = FancyArrowPatch((6.4, y), (9.6, y),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#333')
    ax.add_patch(arrow2)
    
    # OpticalSetup dataclass visualization
    data_box = FancyBboxPatch((6.8, y - 0.5), 2.4, 1.0,
                             boxstyle="round,pad=0.08",
                             edgecolor=color_data, facecolor='white',
                             linewidth=2, alpha=0.95)
    ax.add_patch(data_box)
    ax.text(8.0, y + 0.3, 'OpticalSetup', ha='center', va='center',
            fontsize=9, fontweight='bold', color=color_data)
    ax.text(8.0, y, '• components: List[Dict]', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    ax.text(8.0, y - 0.15, '• beam_path: List[List]', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    ax.text(8.0, y - 0.3, '• physics_explanation: str', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    
    # 4. Simulation validates
    y -= 1.3
    sim_box = FancyBboxPatch((9.5, y - 0.3), 1.0, 0.6,
                            boxstyle="round,pad=0.05",
                            edgecolor=color_sim, facecolor=color_sim,
                            linewidth=1.5, alpha=0.5)
    ax.add_patch(sim_box)
    ax.text(10, y, 'Validate\nPhysics', ha='center', va='center',
            fontsize=7, color='white', fontweight='bold')
    
    # 5. Return verdict
    y -= 0.8
    arrow3 = FancyArrowPatch((9.6, y), (6.4, y),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#d9534f', linestyle='--')
    ax.add_patch(arrow3)
    
    # Verdict structure
    verdict_box = FancyBboxPatch((6.8, y - 0.4), 2.4, 0.8,
                                boxstyle="round,pad=0.08",
                                edgecolor='#d9534f', facecolor='white',
                                linewidth=2, alpha=0.95)
    ax.add_patch(verdict_box)
    ax.text(8.0, y + 0.2, 'SimulationResult', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#d9534f')
    ax.text(8.0, y - 0.05, '• success: bool', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    ax.text(8.0, y - 0.2, '• verdict: "accept" | "refine"', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    ax.text(8.0, y - 0.35, '• issues: List[str]', ha='center', va='center',
            fontsize=6, color='#333', family='monospace')
    
    # 6. Refinement (if needed)
    y -= 1.0
    refine_box = FancyBboxPatch((5.5, y - 0.25), 1.0, 0.5,
                               boxstyle="round,pad=0.05",
                               edgecolor=color_llm, facecolor=color_llm,
                               linewidth=1.5, alpha=0.5)
    ax.add_patch(refine_box)
    ax.text(6, y, 'Refine\n(if needed)', ha='center', va='center',
            fontsize=7, color='white', fontweight='bold')
    
    # Loop arrow
    loop_arrow = FancyArrowPatch((6, y - 0.3), (6, y + 1.5),
                                arrowstyle='->', mutation_scale=15, linewidth=1.5,
                                color=color_llm, linestyle=':', alpha=0.6)
    ax.add_patch(loop_arrow)
    ax.text(6.5, y + 0.6, 'Max 3\nCycles', ha='left', va='center',
            fontsize=7, color=color_llm, style='italic')
    
    # 7. Return to user
    y -= 0.8
    arrow4 = FancyArrowPatch((5.6, y), (2.4, y),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#27ae60')
    ax.add_patch(arrow4)
    ax.text(4.0, y + 0.2, 'Validated Design + Visualization', ha='center', va='bottom',
            fontsize=8, color='#27ae60', bbox=dict(boxstyle='round,pad=0.3',
                                                    facecolor='#d5f4e6', alpha=0.8))
    
    # === Key insight box ===
    insight_box = FancyBboxPatch((0.5, 0.2), 11, 0.8,
                                boxstyle="round,pad=0.1",
                                edgecolor='#3498db', facecolor='#ebf5fb',
                                linewidth=2, alpha=0.9)
    ax.add_patch(insight_box)
    ax.text(6, 0.75, '🔑 Key Design Principle: Loose Coupling Through Data Structures', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='#2c3e50')
    ax.text(6, 0.5, 'Agents communicate solely through OpticalSetup and SimulationResult dataclasses,', 
            ha='center', va='center', fontsize=8, color='#34495e')
    ax.text(6, 0.3, 'enabling independent upgrades without breaking the protocol.', 
            ha='center', va='center', fontsize=8, color='#34495e')
    
    plt.tight_layout()
    plt.savefig('paper/fig_agent_communication.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('paper/fig_agent_communication.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: fig_agent_communication.pdf/png")
    plt.close()


def create_self_refinement_loop():
    """
    Visualize the SELF-REFINE paradigm implementation
    Shows how validation-critique-improvement cycle works
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Colors
    color_generate = '#E8A87C'
    color_validate = '#6B9BD1'
    color_refine = '#B19CD9'
    color_success = '#7BC96F'
    
    # Title
    ax.text(6, 7.5, 'Self-Refinement Loop (SELF-REFINE Paradigm)', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    ax.text(6, 7.0, 'Convergent Validation-Critique-Improvement Cycle (Max 3 Iterations)',
            ha='center', va='top', fontsize=11, style='italic', color='#555')
    
    # === Circular flow diagram ===
    
    center_x, center_y = 6, 4
    radius = 2.5
    
    # Stage positions (clockwise from top)
    angles = [90, 350, 250, 150]  # degrees
    positions = {
        'generate': (center_x + radius * np.cos(np.radians(angles[0])),
                    center_y + radius * np.sin(np.radians(angles[0]))),
        'validate': (center_x + radius * np.cos(np.radians(angles[1])),
                    center_y + radius * np.sin(np.radians(angles[1]))),
        'critique': (center_x + radius * np.cos(np.radians(angles[2])),
                    center_y + radius * np.sin(np.radians(angles[2]))),
        'refine': (center_x + radius * np.cos(np.radians(angles[3])),
                  center_y + radius * np.sin(np.radians(angles[3])))
    }
    
    # 1. Generate stage
    gen_box = FancyBboxPatch((positions['generate'][0] - 0.7, positions['generate'][1] - 0.3),
                             1.4, 0.6,
                             boxstyle="round,pad=0.1",
                             edgecolor=color_generate, facecolor=color_generate,
                             linewidth=2.5, alpha=0.8)
    ax.add_patch(gen_box)
    ax.text(positions['generate'][0], positions['generate'][1] + 0.1, 
            '1. Generate', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(positions['generate'][0], positions['generate'][1] - 0.15, 
            'Initial Design', ha='center', va='center',
            fontsize=8, color='white', style='italic')
    
    # 2. Validate stage
    val_box = FancyBboxPatch((positions['validate'][0] - 0.7, positions['validate'][1] - 0.3),
                             1.4, 0.6,
                             boxstyle="round,pad=0.1",
                             edgecolor=color_validate, facecolor=color_validate,
                             linewidth=2.5, alpha=0.8)
    ax.add_patch(val_box)
    ax.text(positions['validate'][0], positions['validate'][1] + 0.1, 
            '2. Validate', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(positions['validate'][0], positions['validate'][1] - 0.15, 
            '6 Physics Checks', ha='center', va='center',
            fontsize=8, color='white', style='italic')
    
    # 3. Critique stage
    crit_box = FancyBboxPatch((positions['critique'][0] - 0.7, positions['critique'][1] - 0.3),
                              1.4, 0.6,
                              boxstyle="round,pad=0.1",
                              edgecolor=color_refine, facecolor=color_refine,
                              linewidth=2.5, alpha=0.8)
    ax.add_patch(crit_box)
    ax.text(positions['critique'][0], positions['critique'][1] + 0.1, 
            '3. Critique', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(positions['critique'][0], positions['critique'][1] - 0.15, 
            'Identify Issues', ha='center', va='center',
            fontsize=8, color='white', style='italic')
    
    # 4. Refine stage
    ref_box = FancyBboxPatch((positions['refine'][0] - 0.7, positions['refine'][1] - 0.3),
                             1.4, 0.6,
                             boxstyle="round,pad=0.1",
                             edgecolor=color_generate, facecolor=color_generate,
                             linewidth=2.5, alpha=0.8)
    ax.add_patch(ref_box)
    ax.text(positions['refine'][0], positions['refine'][1] + 0.1, 
            '4. Refine', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(positions['refine'][0], positions['refine'][1] - 0.15, 
            'Targeted Fix', ha='center', va='center',
            fontsize=8, color='white', style='italic')
    
    # Circular arrows connecting stages
    for i in range(4):
        start = positions[list(positions.keys())[i]]
        end = positions[list(positions.keys())[(i + 1) % 4]]
        
        # Calculate arrow positions (outside the boxes)
        angle_start = angles[i]
        angle_end = angles[(i + 1) % 4]
        
        arrow = FancyArrowPatch(start, end,
                               arrowstyle='->', mutation_scale=25, linewidth=3,
                               color='#34495e', alpha=0.6,
                               connectionstyle="arc3,rad=.3")
        ax.add_patch(arrow)
    
    # Center: Iteration counter
    center_circle = Circle((center_x, center_y), 0.8, 
                          color='white', ec='#34495e', linewidth=2.5)
    ax.add_patch(center_circle)
    ax.text(center_x, center_y + 0.15, 'Iteration', ha='center', va='center',
            fontsize=9, color='#34495e', fontweight='bold')
    ax.text(center_x, center_y - 0.15, 'Counter', ha='center', va='center',
            fontsize=9, color='#34495e', fontweight='bold')
    ax.text(center_x, center_y - 0.45, '(Max 3)', ha='center', va='center',
            fontsize=7, color='#7f8c8d', style='italic')
    
    # Success exit arrow
    success_arrow = FancyArrowPatch((positions['validate'][0] + 0.7, 
                                    positions['validate'][1]),
                                   (9.5, positions['validate'][1]),
                                   arrowstyle='->', mutation_scale=25, linewidth=3,
                                   color=color_success, alpha=0.8)
    ax.add_patch(success_arrow)
    
    success_box = FancyBboxPatch((9.5, positions['validate'][1] - 0.3), 1.8, 0.6,
                                boxstyle="round,pad=0.1",
                                edgecolor=color_success, facecolor=color_success,
                                linewidth=2.5, alpha=0.8)
    ax.add_patch(success_box)
    ax.text(10.4, positions['validate'][1] + 0.1, '✓ Accept', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(10.4, positions['validate'][1] - 0.15, 'Design Valid', ha='center', va='center',
            fontsize=8, color='white', style='italic')
    
    ax.text(8.2, positions['validate'][1] + 0.3, 'If Valid', ha='center', va='bottom',
            fontsize=8, color=color_success, fontweight='bold')
    
    # === Validation criteria detail box ===
    criteria_box = FancyBboxPatch((0.3, 0.3), 5.5, 1.3,
                                 boxstyle="round,pad=0.1",
                                 edgecolor='#3498db', facecolor='#ebf5fb',
                                 linewidth=2, alpha=0.9)
    ax.add_patch(criteria_box)
    ax.text(3.05, 1.45, '6 Validation Checks (85-line Prompt):', 
            ha='center', va='top', fontsize=9, fontweight='bold', color='#2c3e50')
    
    checks = [
        '1. Optical Path Logic (correct component ordering)',
        '2. Component Connectivity (all connected to beam)',
        '3. Experiment-Specific Requirements (HOM, Bell, etc.)',
        '4. Spatial Consistency (geometric feasibility)',
        '5. Realistic Parameters (wavelengths, ratios)',
        '6. Completeness (source → optics → detector)'
    ]
    
    y_pos = 1.2
    for check in checks:
        ax.text(0.5, y_pos, check, ha='left', va='top',
                fontsize=7, color='#34495e')
        y_pos -= 0.15
    
    # === Convergence criteria box ===
    conv_box = FancyBboxPatch((6.2, 0.3), 5.5, 1.3,
                             boxstyle="round,pad=0.1",
                             edgecolor='#27ae60', facecolor='#d5f4e6',
                             linewidth=2, alpha=0.9)
    ax.add_patch(conv_box)
    ax.text(8.95, 1.45, 'Convergence Criteria:', 
            ha='center', va='top', fontsize=9, fontweight='bold', color='#27ae60')
    
    criteria = [
        '✓ Validation verdict: "accept"',
        '✓ All 6 checks pass',
        '✓ OR max 3 iterations reached',
        '',
        'Token usage tracked across all cycles',
        'Best version preserved if refinement degrades'
    ]
    
    y_pos = 1.2
    for crit in criteria:
        ax.text(6.4, y_pos, crit, ha='left', va='top',
                fontsize=7, color='#27ae60' if '✓' in crit else '#34495e',
                fontweight='bold' if '✓' in crit else 'normal')
        y_pos -= 0.15
    
    plt.tight_layout()
    plt.savefig('paper/fig_self_refinement_loop.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('paper/fig_self_refinement_loop.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: fig_self_refinement_loop.pdf/png")
    plt.close()


if __name__ == '__main__':
    print("🎨 Generating cognitive architecture visualizations...")
    print()
    
    print("1. Creating three-layer architecture diagram...")
    create_three_layer_architecture()
    print()
    
    print("2. Creating agent communication flow diagram...")
    create_agent_communication_flow()
    print()
    
    print("3. Creating self-refinement loop diagram...")
    create_self_refinement_loop()
    print()
    
    print("✅ All visualizations complete!")
    print("\nGenerated files:")
    print("  - fig_cognitive_architecture.pdf/png")
    print("  - fig_agent_communication.pdf/png")
    print("  - fig_self_refinement_loop.pdf/png")
    print("\nUse these in the Methods section to illustrate:")
    print("  Fig 1: Overall three-layer cognitive pipeline")
    print("  Fig 2: How agents communicate through structured data")
    print("  Fig 3: SELF-REFINE validation-critique-improvement cycle")
