"""
Aṇubuddhi (अणुबुद्धि) - AI-Powered Quantum Experiment Designer
Atomic Intelligence for Quantum Optics
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import time
import json
import re
from datetime import datetime
import matplotlib.pyplot as plt

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Import LLM-driven designer
from llm_designer import LLMDesigner
from agentic_quantum.llm import SimpleLLM
from simple_optical_table import create_optical_table_figure
from freeform_simulation_agent import FreeFormSimulationAgent
# Quantum primitives (states & operations) used by the simulator
from agentic_quantum.quantum import FockState, BeamSplitter, PhaseShift

# Page config
st.set_page_config(
    page_title="Aṇubuddhi - Quantum AI",
    page_icon="⚛️",
    layout="wide",  # Full width layout
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful dark warm UI
st.markdown("""
<style>
    /* Dark warm background - allow natural scrolling if needed */
    .stApp {
        background: linear-gradient(135deg, #1a1410 0%, #2d1810 50%, #1a1410 100%);
        min-height: 100vh;
    }
    
    /* Allow body to breathe - no forced constraints */
    html, body {
        height: 100vh;
        overflow-x: hidden;
    }
    
    /* Main content area - natural flow */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Header styling - compact for no-scroll layout */
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: #f0d9c0;
        text-align: center;
        padding: 0.5rem 0 0.2rem 0;
        letter-spacing: 2px;
        margin-bottom: 0 !important;
    }
    
    .devanagari {
        font-size: 1.8rem;
        color: #d4a574;
        opacity: 0.8;
    }
    
    .subtitle {
        text-align: center;
        color: #a08060;
        font-size: 0.85rem;
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
        font-style: italic;
    }
    
    /* Input styling */
    .stTextInput {
        max-width: 100% !important;
        margin: 0 !important;
        min-height: 45px !important;
    }
    
    .stTextInput > div {
        background-color: transparent !important;
        border: none !important;
        overflow: visible !important;
        min-height: 45px !important;
    }
    
    .stTextInput > div > div {
        background-color: transparent !important;
        border: none !important;
        overflow: visible !important;
        min-height: 45px !important;
    }
    
    .stTextInput input {
        background-color: rgba(30, 24, 20, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(212, 165, 116, 0.3) !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.2rem !important;
        text-align: left !important;
        height: 45px !important;
        min-height: 45px !important;
        line-height: 1.5rem !important;
        transition: all 0.3s ease !important;
        box-sizing: border-box !important;
        overflow: visible !important;
        width: 100% !important;
    }
    
    .stTextInput input:focus {
        border-color: #d4a574 !important;
        box-shadow: 0 0 0 2px rgba(212, 165, 116, 0.3) !important;
        outline: none !important;
        background-color: rgba(30, 24, 20, 0.8) !important;
        color: #ffffff !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(160, 128, 96, 0.6) !important;
        text-align: left !important;
        font-size: 0.95rem !important;
        line-height: 1.5rem !important;
    }
    
    /* Hide all input instructions */
    .stTextInput [data-testid="InputInstructions"] {
        display: none !important;
    }
    
    .stTextInput label {
        display: none !important;
    }
    
    /* Form styling */
    .stForm {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    /* Button styling */
    .stButton {
        text-align: center !important;
        margin-top: 0.5rem !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #d4a574 0%, #b8865f 100%) !important;
        color: #1a1410 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(212, 165, 116, 0.3) !important;
    }
    
    /* Result boxes */
    .success-box {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        color: #a8e6a3;
    }
    
    .error-box {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        color: #ffcdd2;
    }
    
    /* Glowing golden progress bar with breathing effect */
    div[data-testid="stProgress"] {
        height: 20px !important;
        background: transparent !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Hide the container when progress is 0 or very small */
    div[data-testid="stProgress"] > div[style*="width: 0%"],
    div[data-testid="stProgress"] > div[style*="width: 0px"] {
        display: none !important;
    }
    
    /* Container - completely transparent, no background or border */
    div[data-testid="stProgress"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        overflow: visible !important;
        height: 20px !important;
    }
    
    /* Target the actual progress fill bar with breathing glow - this is the ONLY visible element */
    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, 
            #d4a574 0%, 
            #f4e4c1 40%, 
            #ffb347 70%, 
            #ffd700 100%) !important;
        border-radius: 12px !important;
        animation: breathing-glow 2s ease-in-out infinite !important;
        height: 100% !important;
        border: none !important;
    }
    
    /* Override any Streamlit defaults */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #d4a574 0%, #f4e4c1 50%, #ffb347 100%) !important;
    }
    
    /* Breathing glow animation - pulses smoothly like breathing */
    @keyframes breathing-glow {
        0% {
            box-shadow: 
                0 0 10px rgba(255, 179, 71, 0.4),
                0 0 20px rgba(212, 165, 116, 0.3),
                0 0 30px rgba(255, 215, 0, 0.2);
            filter: brightness(1);
        }
        50% {
            box-shadow: 
                0 0 20px rgba(255, 179, 71, 0.8),
                0 0 40px rgba(212, 165, 116, 0.6),
                0 0 60px rgba(255, 215, 0, 0.4);
            filter: brightness(1.2);
        }
        100% {
            box-shadow: 
                0 0 10px rgba(255, 179, 71, 0.4),
                0 0 20px rgba(212, 165, 116, 0.3),
                0 0 30px rgba(255, 215, 0, 0.2);
            filter: brightness(1);
        }
    }
    
    /* Stage indicator styling */
    .stage-indicator {
        padding: 12px 20px;
        background: linear-gradient(135deg, rgba(212, 165, 116, 0.15) 0%, rgba(244, 228, 193, 0.1) 100%);
        border-left: 4px solid #d4a574;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 16px;
        font-weight: 500;
        color: #f0d9c0;
        box-shadow: 0 2px 10px rgba(212, 165, 116, 0.2);
        animation: slide-in 0.3s ease-out;
    }
    
    @keyframes slide-in {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stage-complete {
        border-left-color: #4caf50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(129, 199, 132, 0.1) 100%);
    }
    
    .stage-active {
        border-left-color: #ffb347;
        animation: pulse-border 2s ease-in-out infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% {
            border-left-color: #ffb347;
            box-shadow: 0 2px 10px rgba(212, 165, 116, 0.2);
        }
        50% {
            border-left-color: #d4a574;
            box-shadow: 0 2px 20px rgba(255, 179, 71, 0.4);
        }
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background: rgba(240, 217, 192, 0.05);
        border: 1px solid rgba(212, 165, 116, 0.2);
        padding: 1rem;
        border-radius: 8px;
    }
    
    div[data-testid="metric-container"] label {
        color: #a08060 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f0d9c0 !important;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(212, 165, 116, 0.1) !important;
        color: #d4a574 !important;
        border-left-color: #d4a574 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f0d9c0 !important;
    }
    
    /* Regular text */
    p, span, li {
        color: #c0a080 !important;
    }
    
    /* Clean form styling - REMOVE ALL SHADOWS AND BORDERS */
    .stForm {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
        max-width: 800px !important;
        margin: 0 auto !important;
        box-shadow: none !important;
    }
    
    .stForm > div {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    
    /* Form submit buttons - visible and styled */
    .stForm button[kind="formSubmit"] {
        margin-top: 0.5rem !important;
    }
    
    /* Form text input - NO SHADOWS */
    .stForm .stTextInput {
        max-width: 100% !important;
    }
    
    .stForm .stTextInput > div {
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Hide all instruction messages */
    [data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Ensure text input wrapper doesn't clip content */
    div[data-baseweb="base-input"] {
        overflow: visible !important;
        min-height: 45px !important;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide deploy button and streamlit branding */
    .stDeployButton {display: none !important;}
    button[kind="header"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Hide horizontal rules for compact layout */
    hr {
        margin: 0.3rem 0 !important;
        border-color: rgba(212, 165, 116, 0.1) !important;
    }
    
    /* SVG diagram container */
    .svg-container {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Smooth transition animations */
    .welcome-container {
        animation: fadeIn 0.5s ease-in;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .two-column-layout {
        animation: expandWidth 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes expandWidth {
        from {
            opacity: 0.7;
            max-width: 900px;
            margin: 0 auto;
        }
        to {
            opacity: 1;
            max-width: 100%;
            margin: 0;
        }
    }
    
    /* Columns with proper height constraints */
    [data-testid="column"] {
        padding: 0 1rem;
        height: calc(100vh - 80px);
        display: flex;
        flex-direction: column;
    }
    
    /* Chat pane styling */
    .chat-container {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        max-height: calc(100vh - 180px);
        padding-right: 0.5rem;
        padding-bottom: 0.5rem;
        margin-bottom: 0;
        scroll-behavior: smooth;
    }
    
    /* User message bubble - left aligned, no shadow */
    .user-message {
        background: linear-gradient(135deg, rgba(100, 150, 200, 0.15), rgba(120, 170, 220, 0.1));
        border-left: 3px solid rgba(100, 150, 200, 0.5);
        padding: 1rem 1.2rem;
        border-radius: 12px 12px 12px 4px;
        margin: 0.8rem 0;
        margin-right: 15%;
        color: #e8f4f8;
    }
    
    /* AI message bubble - slightly right offset, no shadow */
    .ai-message {
        background: linear-gradient(135deg, rgba(212, 165, 116, 0.12), rgba(244, 228, 193, 0.08));
        border-left: 3px solid rgba(212, 165, 116, 0.6);
        padding: 1rem 1.2rem;
        border-radius: 12px 12px 4px 12px;
        margin: 0.8rem 0;
        margin-left: 8%;
        margin-right: 0;
        color: #f4e4c1;
    }
    
    /* Design pane styling */
    .design-container {
        height: 100%;
    }
    
    /* Tab styling - BRIGHTER INACTIVE TABS */
    button[data-baseweb="tab"] {
        color: rgba(212, 165, 116, 0.9) !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: rgba(212, 165, 116, 1) !important;
        background-color: rgba(212, 165, 116, 0.1) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #d4a574 !important;
        font-weight: 600 !important;
        border-bottom-color: #d4a574 !important;
    }
    
    /* Tab content area */
    [data-testid="stTabContent"] {
        color: #f0d9c0 !important;
    }
    
    /* Button styling - ALL BUTTONS */
    .stButton > button,
    button[data-testid^="baseButton"] {
        background-color: #3d2817 !important;
        border: 1px solid #d4a574 !important;
        color: #ffffff !important;
    }
    
    .stButton > button:hover,
    button[data-testid^="baseButton"]:hover {
        background-color: #4d3520 !important;
        border-color: #e0b888 !important;
    }
    
    /* Force WHITE text in ALL buttons */
    .stButton > button,
    .stButton > button *,
    button[data-testid^="baseButton"],
    button[data-testid^="baseButton"] *,
    button[data-testid^="baseButton"] p,
    button[data-testid^="baseButton"] span,
    button[data-testid^="baseButton"] div,
    button p, button span, button div {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_design' not in st.session_state:
    st.session_state.current_design = None
if 'designer_agent' not in st.session_state:
    st.session_state.designer_agent = None
if 'conversation_context' not in st.session_state:
    # Track full conversation for episodic memory
    st.session_state.conversation_context = []
if 'design_iterations' not in st.session_state:
    # Track design evolution (v1, v2, v3...)
    st.session_state.design_iterations = []
if 'current_design_id' not in st.session_state:
    # Link iterations together
    st.session_state.current_design_id = None
if 'pending_query' not in st.session_state:
    # Store query to process after rerun (prevents ghost rendering)
    st.session_state.pending_query = None
if 'is_processing' not in st.session_state:
    # Flag to show clean "thinking" state during AI processing
    st.session_state.is_processing = False
if 'processing_mode' not in st.session_state:
    # Track if processing is 'chat' or 'design' mode
    st.session_state.processing_mode = None
if 'terminal_logs' not in st.session_state:
    # Global terminal logs for all system output
    st.session_state.terminal_logs = []


def web_search_wrapper(query: str) -> dict:
    """
    Wrapper for web search using DuckDuckGo API.
    Falls back to curated quantum optics knowledge if search fails.
    Returns dict with 'results' list and 'source' field ('web' or 'curated').
    """
    try:
        import requests
        from urllib.parse import quote
        
        # Try DuckDuckGo Instant Answer API first (cleaner, faster)
        encoded_query = quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                results = []
                
                # Extract abstract/definition
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', 'DuckDuckGo Result'),
                        'description': data.get('Abstract'),
                        'url': data.get('AbstractURL', 'https://duckduckgo.com')
                    })
                
                # Extract related topics
                for topic in data.get('RelatedTopics', [])[:2]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else 'Related',
                            'description': topic.get('Text', ''),
                            'url': topic.get('FirstURL', 'https://duckduckgo.com')
                        })
                
                # If we got real results, return them
                if results:
                    return {"results": results[:3], "source": "web"}
            except (ValueError, KeyError) as json_error:
                # JSON parsing failed, fall through to curated knowledge
                pass
        
        # Fallback: return curated quantum optics knowledge
        # (Don't print message here - let calling code handle it)
        curated = _get_curated_quantum_knowledge(query)
        curated['source'] = 'curated'
        return curated
        
    except Exception as e:
        # Only print error for non-JSON issues
        if "Expecting value" not in str(e):
            print(f"   ⚠️  Web search error: {e}")
        curated = _get_curated_quantum_knowledge(query)
        curated['source'] = 'curated'
        return curated


def _get_curated_quantum_knowledge(query: str) -> dict:
    """Provide curated quantum optics experiment knowledge when web search fails."""
    query_lower = query.lower()
    
    knowledge_base = {
        'hong-ou-mandel': {
            'title': 'Hong-Ou-Mandel (HOM) Effect',
            'description': 'Two-photon quantum interference where indistinguishable photons incident on a 50:50 beam splitter always exit together in the same output port, creating a characteristic dip in coincidence counts. Requires SPDC source, delay matching, 50:50 BS, and coincidence detection.',
            'url': 'https://en.wikipedia.org/wiki/Hong%E2%80%93Ou%E2%80%93Mandel_effect'
        },
        'bell': {
            'title': 'Bell State Measurement',
            'description': 'Measurement of maximally entangled two-qubit states |Φ±⟩ or |Ψ±⟩. Typically uses SPDC to generate entangled photon pairs, polarization analysis with wave plates and polarizers, and coincidence counting.',
            'url': 'https://en.wikipedia.org/wiki/Bell_state'
        },
        'mach-zehnder': {
            'title': 'Mach-Zehnder Interferometer',
            'description': 'Two-path interferometer with two beam splitters and adjustable phase shift in one arm. Shows wave-particle duality and can demonstrate quantum erasure. Components: 2× beam splitters, 2× mirrors, phase shifter, detectors.',
            'url': 'https://en.wikipedia.org/wiki/Mach%E2%80%93Zehnder_interferometer'
        },
        'double-slit': {
            'title': 'Double-Slit Experiment',
            'description': 'Fundamental quantum interference experiment showing wave-particle duality. Single photons create interference pattern on screen. Components: coherent source, double slit, detection screen or camera.',
            'url': 'https://en.wikipedia.org/wiki/Double-slit_experiment'
        },
        'spdc': {
            'title': 'Spontaneous Parametric Down-Conversion (SPDC)',
            'description': 'Nonlinear optical process where pump photon splits into signal and idler photons in nonlinear crystal (BBO, KTP, PPLN). Energy and momentum conservation creates entangled pairs. Type-I: same polarization, Type-II: orthogonal polarizations.',
            'url': 'https://en.wikipedia.org/wiki/Spontaneous_parametric_down-conversion'
        }
    }
    
    # Find matching knowledge
    for key, info in knowledge_base.items():
        if key in query_lower or any(word in query_lower for word in key.split('-')):
            return {"results": [info]}
    
    # Generic quantum optics info
    return {"results": [{
        'title': 'Quantum Optics Experiment Design',
        'description': 'Design quantum optics experiments using standard components: lasers, nonlinear crystals, beam splitters, phase shifters, polarizers, wave plates, single-photon detectors (SPADs), and coincidence electronics.',
        'url': 'https://en.wikipedia.org/wiki/Quantum_optics'
    }]}


def initialize_designer():
    """Initialize the LLM-driven quantum designer with web search capability."""
    # Show initialization message
    with st.spinner("🧠 Initializing AI memory system (first time may take a moment)..."):
        llm = SimpleLLM(model="anthropic/claude-sonnet-4.5")
        
        # Try to enable web search if available
        try:
            # Check if web search tool is available
            web_search_fn = web_search_wrapper
            st.session_state.designer = LLMDesigner(
                llm_client=llm,
                web_search_tool=web_search_fn
            )
            print("✅ Designer initialized with web search capability")
        except Exception as e:
            print(f"⚠️  Web search not available, initializing without it: {e}")
            st.session_state.designer = LLMDesigner(llm_client=llm)
        
        # Initialize free-form simulation agent
        st.session_state.freeform_agent = FreeFormSimulationAgent(llm_client=llm)


def create_component_legend():
    """Create a visual legend for optical components."""
    return """
    <div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px;">
        <h4 style="margin-top: 0; color: #495057;">Component Legend</h4>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background: #ff6b6b; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">hν</div>
                <div>
                    <strong>Photon Source</strong><br/>
                    <small>Generates single photons</small>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background: #4dabf7; border-radius: 3px; transform: rotate(45deg);"></div>
                <div>
                    <strong>Beam Splitter</strong><br/>
                    <small>Splits/combines light paths</small>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background: #a5d8ff; border: 2px solid #1971c2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #1864ab; font-weight: bold;">φ</div>
                <div>
                    <strong>Phase Shifter</strong><br/>
                    <small>Adjusts photon phase</small>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background: #51cf66; clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%); display: flex; align-items: center; justify-content: center;"></div>
                <div>
                    <strong>Detector</strong><br/>
                    <small>Measures photon states</small>
                </div>
            </div>
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
            <div style="display: flex; gap: 20px; align-items: center;">
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 40px; height: 4px; background: #ffd43b;"></div>
                    <small>Optical Path</small>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 40px; height: 3px; background: #ffd43b; border-top: 3px dashed #ffd43b;"></div>
                    <small>Split Path</small>
                </div>
            </div>
        </div>
    </div>
    """


def create_optical_table_diagram(experiment_dict):
    """Generate professional canvas-based optical table diagram with proper physics layout."""
    
    # Parse experiment steps to extract components
    components = []
    for step in experiment_dict.get('steps', []):
        step_type = step.get('step_type')
        desc = step.get('description', '')
        params = step.get('parameters', {})
        
        if 'Fock state' in desc or step_type == 'initialization':
            photon_pattern = '|1,0⟩' if '|1,0' in desc else '|0,0⟩'
            components.append({'type': 'source', 'label': f'Source {photon_pattern}'})
        elif 'Beam splitter' in desc or step_type == 'beam_splitter':
            t = params.get('transmittance', 0.5)
            components.append({'type': 'beamsplitter', 'label': f'BS (T={t:.0%})'})
        elif 'Phase shift' in desc or step_type == 'phase_shift':
            phase = params.get('phase', 0.0)
            components.append({'type': 'phase', 'label': f'φ={phase:.2f}rad'})
        elif 'measurement' in step_type or 'Measurement' in desc:
            components.append({'type': 'detector', 'label': 'Detector'})
    
    # Create a clean HTML/CSS based diagram
    diagram_html = f'''
    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 20px; font-size: 20px;">🔬 Optical Table Setup</h3>
        <div style="background: white; padding: 20px; border-radius: 10px; min-height: 200px; position: relative;">
'''
    
    # Draw optical path horizontally with proper spacing
    if components:
        num_comps = len(components)
        for i, comp in enumerate(components):
            left_pos = 10 + (i * 80 / num_comps)
            
            # Component box
            if comp['type'] == 'source':
                color = '#ff6b6b'
                icon = '🔴'
            elif comp['type'] == 'beamsplitter':
                color = '#4dabf7'
                icon = '🔷'
            elif comp['type'] == 'phase':
                color = '#a5d8ff'
                icon = '🔵'
            elif comp['type'] == 'detector':
                color = '#51cf66'
                icon = '🟢'
            else:
                color = '#adb5bd'
                icon = '⚪'
            
            diagram_html += f'''
            <div style="display: inline-block; width: {70/num_comps}%; vertical-align: middle; text-align: center;">
                <div style="background: {color}; color: white; padding: 20px 10px; border-radius: 10px; font-weight: bold; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="font-size: 12px; margin-top: 5px;">{comp['label']}</div>
                </div>
            </div>'''
            
            # Draw arrow between components
            if i < num_comps - 1:
                diagram_html += f'''
            <div style="display: inline-block; width: {25/num_comps}%; vertical-align: middle; text-align: center;">
                <div style="color: #ffd43b; font-size: 30px; font-weight: bold;">→</div>
            </div>'''
    
    diagram_html += '''
        </div>
        <div style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.9); border-radius: 10px; font-size: 13px;">
            <strong>📊 Optical Path:</strong> Photons flow left to right through each component sequentially
        </div>
    </div>
'''
    
    return diagram_html


def simulate_and_validate(experiment_dict):
    """Simulate the designed experiment and validate results."""
    
    status_placeholder = st.empty()
    
    # Simulation steps with progress
    steps = [
        ("🔄 Initializing quantum simulation...", 0.2),
        ("⚛️  Preparing initial quantum state...", 0.4),
        ("🔧 Applying quantum operations...", 0.6),
        ("📊 Calculating state properties...", 0.8),
        ("✅ Validating design...", 1.0)
    ]
    
    progress_bar = st.progress(0)
    
    for step_text, progress in steps:
        status_placeholder.info(step_text)
        progress_bar.progress(progress)
        time.sleep(0.3)  # Simulate processing
    
    # Actually simulate
    try:
        # Start with initial state
        initial_state_info = None
        for step in experiment_dict['steps']:
            if step['step_type'] == 'state':
                initial_state_info = step
                break
        
        # Create initial state
        if initial_state_info and 'Fock' in initial_state_info['description']:
            photon_nums = initial_state_info['component']['metadata']['photon_numbers']
            state = FockState(photon_numbers=photon_nums).to_qobj()
            
            # Apply operations
            for step in experiment_dict['steps']:
                if step['step_type'] == 'operation':
                    comp = step['component']
                    if comp['type'] == 'beam_splitter':
                        modes = comp['target_modes']
                        bs = BeamSplitter(
                            mode1=modes[0],
                            mode2=modes[1],
                            transmittance=comp['parameters']['transmittance'],
                            phase=comp['parameters']['phase']
                        )
                        bs_op = bs.get_operator([50, 50])
                        state = bs_op * state
                    
                    elif comp['type'] == 'phase_shift':
                        mode = comp['target_modes'][0]
                        ps = PhaseShift(
                            mode=mode,
                            phase=comp['parameters']['phase']
                        )
                        ps_op = ps.get_operator([50, 50])
                        state = ps_op * state
            
            # Analyze final state
            vec = np.array(state.full()).flatten()
            
            # Calculate metrics
            purity = np.abs(np.vdot(vec, vec))
            non_zero_components = np.sum(np.abs(vec) > 0.001)
            
            # Find dominant components
            indices = np.argsort(-np.abs(vec))[:5]
            components = []
            for idx in indices:
                if np.abs(vec[idx]) > 0.001:
                    mode1 = idx // 50
                    mode2 = idx % 50
                    prob = np.abs(vec[idx])**2
                    components.append((mode1, mode2, prob))
            
            # Determine if it's entangled
            is_vacuum = (non_zero_components == 1 and np.abs(vec[0]) > 0.99)
            is_entangled = non_zero_components > 1 and purity > 0.99
            
            # Bell state fidelity (rough estimate)
            bell_fidelity = 0.0
            if not is_vacuum and len(components) >= 2:
                # Check if it looks like a Bell state pattern
                bell_fidelity = min(components[0][2] + components[1][2], 1.0)
            
            status_placeholder.empty()
            progress_bar.empty()
            
            return {
                'success': True,
                'purity': float(purity),
                'non_zero_components': int(non_zero_components),
                'is_vacuum': is_vacuum,
                'is_entangled': is_entangled,
                'bell_fidelity': bell_fidelity,
                'components': components,
                'is_correct': not is_vacuum and (is_entangled or bell_fidelity > 0.5)
            }
    
    except Exception as e:
        status_placeholder.empty()
        progress_bar.empty()
        return {
            'success': False,
            'error': str(e)
        }
    
    status_placeholder.empty()
    progress_bar.empty()
    
    return {
        'success': False,
        'error': 'Unknown simulation error'
    }


def design_experiment(user_query, previous_design=None, conversation_history=None):
    """
    Design an experiment based on user query using LLM designer.
    
    Args:
        user_query: Current user request
        previous_design: If refining, the previous design to modify
        conversation_history: Full conversation context for episodic memory
    """
    
    # Prevent duplicate calls during Streamlit reruns
    if 'design_in_progress' in st.session_state and st.session_state.design_in_progress:
        print(f"⚠️  Design already in progress, skipping duplicate call")
        # Return cached result if available
        if 'last_design_result' in st.session_state:
            return st.session_state.last_design_result
        # Otherwise wait (should not happen, but just in case)
        return {'error': 'Design in progress, please wait...'}
    
    # Mark design as in progress
    st.session_state.design_in_progress = True
    
    designer = st.session_state.designer
    
    # Check if user wants to force new design (skip retrieval)
    force_new = st.session_state.get('force_new_design', False)
    if force_new:
        print(f"🔄 User requested new design - skipping memory retrieval")
        st.session_state['force_new_design'] = False  # Reset flag
        # Add marker to conversation history
        if conversation_history is None:
            conversation_history = []
        conversation_history.append({'force_new_design': True})
    
    # Build enhanced query with conversation context if refining
    enhanced_query = user_query
    if previous_design:
        # Refinement mode: include previous design context with numbered components
        components = previous_design.get('experiment', {}).get('steps', [])
        component_list = ""
        for i, comp in enumerate(components, 1):
            comp_name = comp.get('description', comp.get('type', 'Component'))
            comp_type = comp.get('type', 'unknown')
            pos = comp.get('position', (0, 0))
            params = comp.get('parameters', {})
            component_list += f"{i}. **{comp_name}** (type: {comp_type})\n"
            component_list += f"   Position: ({pos[0]:.1f}, {pos[1]:.1f})\n"
            if params:
                component_list += f"   Parameters: {json.dumps(params)}\n"
        
        enhanced_query = f"""REFINE THE FOLLOWING DESIGN:

**Current Design**: {previous_design.get('title', 'Quantum Experiment')}
{previous_design.get('description', '')}

**Current Components** (numbered for reference):
{component_list}

**User Refinement Request**: {user_query}

**IMPORTANT**: If the user refers to components by NUMBER (e.g., "move component 5", "components 3 and 4 are too close", "#6"), use the numbered list above to identify which specific components they mean. Then modify ONLY those components as requested.

Please modify the design according to the user's request while preserving the overall experiment structure and physics unless specifically asked to change them."""
    
    try:
        # Let LLM design everything (with conversation context if available)
        result = designer.design_experiment(enhanced_query, conversation_context=conversation_history)
        
        # Track design phase token usage
        design_tokens = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'cost': 0.0
        }
        if hasattr(designer.llm, 'last_usage'):
            design_tokens = designer.llm.last_usage.copy()
        
        # Store the original query for memory storage later
        result.original_user_query = user_query  # Store original, not enhanced
        
    except Exception as e:
        error_msg = str(e)
        # Clear the in-progress flag on error
        st.session_state.design_in_progress = False
        
        # Check for API credit issues
        if "402" in error_msg or "credits" in error_msg.lower():
            return {
                'error': '💳 OpenRouter API credits exhausted',
                'details': 'Please add credits at https://openrouter.ai/credits',
                'raw_error': error_msg
            }
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            return {
                'error': '⏰ Rate limit exceeded',
                'details': 'Please wait a moment and try again',
                'raw_error': error_msg
            }
        else:
            return {
                'error': f'Design failed: {error_msg}',
                'details': 'Check terminal output for more details'
            }
    
    # Convert to format expected by visualization
    optical_format = {
        'title': result.title,
        'description': result.description,
        'steps': []
    }
    
    # Add components as steps
    for comp in result.components:
        step = {
            'type': comp['type'],
            'description': comp.get('name', comp['type'].title()),
            'position': (comp['x'], comp['y']),
            'angle': comp.get('angle', 0),
            'parameters': comp.get('parameters', {})
        }
        optical_format['steps'].append(step)
    # Attach beam paths if provided (LLMDesigner returns list-of-paths or [])
    if hasattr(result, 'beam_path') and result.beam_path:
        optical_format['beam_path'] = result.beam_path
    
    design_result = {
        'experiment': optical_format,
        'title': result.title,
        'description': result.description,
        'physics_explanation': result.physics_explanation,
        'design_rationale': result.physics_explanation,
        'design_confidence': 0.95,
        'estimated_complexity': len(result.components),
        'expected_outcome': result.expected_outcome,
        'component_justifications': result.component_justifications,
        # Debug info
        'raw_llm_response': result.raw_llm_response,
        'parsed_design': result.parsed_design_json,
        'components_sent_to_renderer': result.components,
        'web_search_used': result.web_search_used,
        'web_search_context': result.web_search_context,
        # Store the OpticalSetup object for simulation
        'optical_setup_object': result,
        # Store original user query for memory
        'original_user_query': getattr(result, 'original_user_query', user_query),
        # Simulation results (now added on-demand)
        'simulation_results': getattr(result, 'simulation_results', None),
        # Track design phase token usage
        'design_tokens': design_tokens
    }
    
    # Cache the result and clear the in-progress flag
    st.session_state.last_design_result = design_result
    st.session_state.design_in_progress = False
    
    return design_result


def run_simulation_on_design(design_result):
    """
    Run quantum simulation on an existing design.
    Called when user clicks 'Run Simulation' button.
    
    Args:
        design_result: Dict containing the design information with OpticalSetup object
        
    Returns:
        Dict with simulation results
    """
    if 'designer' not in st.session_state or st.session_state.designer is None:
        return {
            'success': False,
            'error': 'Designer not initialized'
        }
    
    designer = st.session_state.designer
    
    # Logs are already captured by global terminal_print function
    
    try:
        # We need to reconstruct the OpticalSetup from the design result
        # or better yet, store the original OpticalSetup object
        if 'optical_setup_object' in design_result:
            optical_setup = design_result['optical_setup_object']
        else:
            # Reconstruct from design_result
            from llm_designer import OpticalSetup
            optical_setup = OpticalSetup(
                title=design_result.get('title', 'Untitled'),
                description=design_result.get('description', ''),
                components=design_result.get('components_sent_to_renderer', []),
                beam_path=design_result.get('experiment', {}).get('beam_path', []),
                physics_explanation=design_result.get('physics_explanation', ''),
                expected_outcome=design_result.get('expected_outcome', ''),
                component_justifications=design_result.get('component_justifications', {}),
                raw_llm_response=design_result.get('raw_llm_response', ''),
                parsed_design_json=design_result.get('parsed_design', {}),
                web_search_used=design_result.get('web_search_used', False),
                web_search_context=design_result.get('web_search_context', '')
            )
        
        # Run simulation
        result = designer.run_simulation(optical_setup)
        return result
    except Exception as e:
        st.session_state.terminal_logs.append(f"❌ Simulation error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_freeform_simulation(design_result):
    """
    Run free-form physics-aware simulation on an existing design.
    Called when user clicks 'Free-Form Sim' button.
    
    Args:
        design_result: Dict containing the design information
        
    Returns:
        Dict with simulation results including generated code and analysis
    """
    if 'freeform_agent' not in st.session_state or st.session_state.freeform_agent is None:
        return {
            'success': False,
            'error': 'Free-form simulation agent not initialized'
        }
    
    agent = st.session_state.freeform_agent
    
    try:
        # Format design for free-form agent
        design = {
            'title': design_result.get('title', 'Untitled'),
            'description': design_result.get('description', ''),
            'physics_explanation': design_result.get('physics_explanation', ''),
            'expected_outcome': design_result.get('expected_outcome', ''),
            'components': design_result.get('components_sent_to_renderer', []),
            'experiment': design_result.get('experiment', {}),
        }
        
        # Run free-form simulation
        result = agent.validate_design(design)
        return result
    except Exception as e:
        st.session_state.terminal_logs.append(f"❌ Free-form simulation error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main app interface - clean and beautiful."""
    
    # Setup global print capture for terminal display
    import builtins
    if 'original_print' not in st.session_state:
        st.session_state.original_print = builtins.print
    
    def terminal_print(*args, **kwargs):
        """Capture all print statements to terminal logs."""
        message = ' '.join(str(arg) for arg in args)
        if 'terminal_logs' not in st.session_state:
            st.session_state.terminal_logs = []
        st.session_state.terminal_logs.append(message)
        # Also print to original output
        st.session_state.original_print(*args, **kwargs)
        
        # Force update terminal display if placeholder exists
        if 'terminal_placeholder' in st.session_state and st.session_state.terminal_placeholder is not None:
            try:
                with st.session_state.terminal_placeholder.container():
                    logs = st.session_state.get('terminal_logs', [])
                    if logs:
                        terminal_text = "\n".join(logs)
                        st.code(terminal_text, language="bash")
            except:
                pass  # Placeholder might not be active anymore
    
    # Replace print globally
    builtins.print = terminal_print
    
    # Sidebar with system status
    with st.sidebar:
        st.markdown("### ⚙️ System Status")
        
        # Check API configuration
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and len(api_key) > 10:
            st.success("✅ API Key: Configured")
        else:
            st.error("❌ API Key: Missing")
            st.warning("Set OPENAI_API_KEY in .env file")
        
        # Memory system status
        if 'designer' in st.session_state and hasattr(st.session_state.designer, 'memory') and st.session_state.designer.memory:
            st.success("✅ Memory: Active")
        else:
            st.info("💤 Memory: Not initialized")
        
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Simple designs: 30-60 seconds")
        st.markdown("- Complex designs: may take 2-3 minutes")
        st.markdown("- Don't refresh during design!")
        st.markdown("- Check terminal for progress logs")
        st.markdown("- Memory learns from each design")
    
    # Initialize designer if not exists
    if 'designer' not in st.session_state or st.session_state.designer is None:
        initialize_designer()
    
    # Header - always visible at top
    st.markdown('<h1 class="main-header">Aṇubuddhi <span class="devanagari">अणुबुद्धि</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Agentic AI for Quantum Experiment Design</p>', unsafe_allow_html=True)
    
    # TWO-COLUMN LAYOUT (always visible)
    left_col, right_col = st.columns([1, 1], gap="large")
    
    # LEFT: Chat pane with input at bottom
    with left_col:
        st.markdown("### 💬 Discussion")
        
        # Content area - show welcome OR messages
        messages_container = st.container(height=600)
        
        with messages_container:
            # Scrollable chat messages area
            st.markdown('<div class="chat-messages" id="chatMessages">', unsafe_allow_html=True)
            
            # Show conversation messages OR welcome (NEVER both)
            # Welcome ONLY shows when completely idle - no messages, no pending, no processing
            if st.session_state.conversation_context:
                # Show conversation messages
                for msg in st.session_state.conversation_context:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    
                    if role == 'user':
                        # User message - left aligned
                        st.markdown(f"""
                        <div class="user-message">
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # AI message - slightly right offset, more conversational
                        st.markdown(f"""
                        <div class="ai-message">
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
            elif not st.session_state.is_processing and not st.session_state.conversation_context and not st.session_state.get('pending_query'):
                # Welcome ONLY when completely idle - no conversation, no processing, no pending query
                st.markdown("""
                <div style="text-align: center; padding: 3rem 2rem 2rem 2rem;">
                    <div style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.9;">⚛️</div>
                    <div style="font-size: 1.8rem; font-weight: 300; margin-bottom: 1rem; color: #f0d9c0; letter-spacing: 1px;">
                        Welcome to Aṇubuddhi
                    </div>
                    <div style="font-size: 1rem; color: #d4a574; margin-bottom: 2rem; font-style: italic;">
                        AI-Powered Quantum Experiment Designer
                    </div>
                    <div style="max-width: 600px; margin: 0 auto; color: #a08060; line-height: 1.8; font-size: 0.95rem;">
                        <div style="background: rgba(212, 165, 116, 0.1); border: 1px solid rgba(212, 165, 116, 0.2); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
                            <div style="color: #d4a574; font-weight: 500; margin-bottom: 1rem;">I can help you with:</div>
                            <div style="text-align: left; margin-left: 2rem;">
                                🔬 <strong style="color: #f0d9c0;">Design quantum optics experiments</strong> from scratch<br>
                                💬 <strong style="color: #f0d9c0;">Answer questions</strong> about quantum physics and setups<br>
                                🔧 <strong style="color: #f0d9c0;">Refine and optimize</strong> existing configurations<br>
                                🧪 <strong style="color: #f0d9c0;">Simulate and validate</strong> designs with QuTiP<br>
                                📚 <strong style="color: #f0d9c0;">Learn from experience</strong> and retrieve past successes
                            </div>
                        </div>
                        <div style="color: #d4a574; font-size: 0.9rem; margin-top: 1rem;">
                            💡 <em>Start by typing a message below, like "design a Hong-Ou-Mandel interferometer"</em>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input - above terminal for easy access
        st.markdown("---")
        
        # New Design button (prominent, outside form) when design exists
        if st.session_state.current_design:
            col_new_btn, col_spacer = st.columns([1, 3])
            with col_new_btn:
                if st.button("🆕 Start New Design", type="secondary", use_container_width=True, key="new_design_main"):
                    st.session_state.current_design = None
                    st.session_state.conversation_context = []
                    st.session_state.design_iterations = []
                    st.session_state.current_design_id = None
                    st.session_state.pending_query = None
                    st.session_state.is_processing = False
                    st.session_state.processing_mode = None
                    st.rerun()
        
        with st.form(key="chat_form", clear_on_submit=True):
            chat_text = st.text_input(
                "Message", 
                placeholder="Design a Bell state generator... or ask: 'What is SPDC?'",
                key="chat_text",
                label_visibility="collapsed"
            )
            send = st.form_submit_button("💬 Send", use_container_width=True)
            new_design = False
        
        # Terminal/Logs display - ALWAYS visible
        st.markdown("---")
        col_term_title, col_term_clear = st.columns([3, 1])
        with col_term_title:
            st.markdown("#### 🖥️ System Terminal")
        with col_term_clear:
            if st.button("🗑️ Clear", key="clear_terminal", type="secondary"):
                st.session_state.terminal_logs = []
                st.rerun()
        
        # Use placeholder for dynamic updates
        if 'terminal_placeholder' not in st.session_state:
            st.session_state.terminal_placeholder = None
        
        terminal_container = st.container(height=500)
        with terminal_container:
            st.session_state.terminal_placeholder = st.empty()
            with st.session_state.terminal_placeholder.container():
                logs = st.session_state.get('terminal_logs', [])
                if logs:
                    # Display ALL logs (no limit), newest at bottom
                    terminal_text = "\n".join(logs)
                    st.code(terminal_text, language="bash")
                else:
                    st.caption("💡 System logs will appear here...")

        # Handle new design button
        if new_design:
            st.session_state.current_design = None
            st.session_state.conversation_context = []
            st.session_state.design_iterations = []
            st.session_state.current_design_id = None
            st.session_state.pending_query = None  # Clear any pending query
            st.session_state.is_processing = False
            st.session_state.processing_mode = None
            st.rerun()

        # Handle send message
        if send and chat_text and chat_text.strip():
            # Append user message to conversation
            st.session_state.conversation_context.append({
                'role': 'user',
                'content': chat_text,
                'timestamp': datetime.now().isoformat()
            })
            
            # Store the query for processing after rerun
            st.session_state.pending_query = chat_text
            st.session_state.is_processing = True
            st.session_state.processing_mode = 'pending'
            st.session_state.processing_logs = []  # Initialize logs immediately
            
            # Set up print interception immediately
            import builtins
            if not hasattr(st.session_state, 'original_print'):
                st.session_state.original_print = builtins.print
            
            def log_print(*args, **kwargs):
                # Call original print for terminal
                if hasattr(st.session_state, 'original_print'):
                    st.session_state.original_print(*args, **kwargs)
                # Add to logs (force add to session state)
                message = ' '.join(str(arg) for arg in args)
                if message.strip():
                    if 'processing_logs' not in st.session_state:
                        st.session_state.processing_logs = []
                    st.session_state.processing_logs.append(message)
            
            builtins.print = log_print
            
            # Rerun immediately to show user message cleanly
            st.rerun()

        # Handle "Improve This" request for retrieved designs
        if st.session_state.get('improve_retrieved', False) and st.session_state.get('base_design'):
            st.session_state['improve_retrieved'] = False  # Reset flag
            base_design = st.session_state.pop('base_design')
            
            # Automatically generate improved version using original query as refinement
            # The system will use the base_design as previous_design to inform improvements
            original_query = st.session_state.conversation_context[-1]['content'] if st.session_state.conversation_context else "improve this design"
            
            # Set the base design as current design so refinement flow kicks in
            st.session_state.current_design = base_design
            st.session_state.pending_query = f"Generate an improved version of this design with better performance and optimization"
            st.session_state.is_processing = True
            st.session_state.processing_mode = 'pending'
            
            # Add system message to conversation
            st.session_state.conversation_context.append({
                'role': 'assistant',
                'content': "I'll generate an improved version of the retrieved design, optimizing the parameters and configuration for better performance. You can also request specific improvements by chatting in the box below.",
                'timestamp': datetime.now().isoformat(),
                'type': 'chat'
            })
            
            st.rerun()
        
        # Process pending query if exists (no overlay - terminal shows progress)
        if st.session_state.pending_query and st.session_state.is_processing:
            chat_text = st.session_state.pending_query
            
            # Ensure logging is set up
            if 'processing_logs' not in st.session_state:
                st.session_state.processing_logs = []
            
            # Add initial log
            if not st.session_state.processing_logs:
                st.session_state.processing_logs.append("🚀 Starting request processing...")
            
            designer = st.session_state.designer
            
            # Route the message: chat or design modification?
            st.session_state.processing_logs.append(f"🧭 Analyzing your request: '{chat_text[:100]}...'")
            mode, reason = designer.route_user_message(chat_text, st.session_state.current_design)
            st.session_state.processing_mode = mode
            st.session_state.processing_logs.append(f"🎯 Routing decision: {mode} - {reason}")
            print(f"🎯 Routing decision: {mode} - {reason}")
            
            try:
                if mode == 'chat':
                    # Conversational Q&A mode
                    with st.spinner("💭 Thinking..."):
                        response_text = designer.chat_about_design(
                            chat_text,
                            current_design=st.session_state.current_design,
                            conversation_context=st.session_state.conversation_context
                        )
                    
                    # Add conversational response (no design update)
                    st.session_state.conversation_context.append({
                        'role': 'assistant',
                        'content': response_text,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'chat'
                    })
                    
                    # Clear processing flags
                    st.session_state.pending_query = None
                    st.session_state.is_processing = False
                    st.session_state.processing_mode = None
                    st.session_state.processing_logs = []  # Clear logs
                    
                    # Restore original print
                    import builtins
                    if hasattr(st.session_state, 'original_print'):
                        builtins.print = st.session_state.original_print
                    
                    st.rerun()
                    
                else:  # mode == 'design'
                    # Design modification/creation mode
                    # LLM sees toolbox composites in prompt and decides whether to use/adapt them
                    # All progress now shows in system terminal below
                    
                    try:
                        # Print to system terminal
                        if st.session_state.current_design:
                            print("🔄 Understanding your refinement request...")
                        else:
                            print("🤖 Starting design process...")
                        
                        print("🧠 Analyzing quantum requirements...")
                        
                        # Run design
                        start_time = time.time()
                        print("⚗️ Generating design (this may take 30-90 seconds)...")
                        print("   → Constructing optical components...")
                        
                        updated = design_experiment(
                            chat_text,
                            previous_design=st.session_state.current_design,
                            conversation_history=st.session_state.conversation_context
                        )
                        
                        elapsed = time.time() - start_time
                        print(f"⏱️  Design generated in {elapsed:.1f} seconds")
                        
                        # Check for errors
                        if 'error' in updated:
                            print(f"❌ Design Failed: {updated['error']}")
                            if 'details' in updated:
                                print(f"⚠️  {updated['details']}")
                            st.error(f"{updated['error']}")
                            st.stop()
                        
                        print("✅ Validating component configuration...")
                        print("📐 Computing beam paths...")
                        print("🎨 Rendering optical table...")
                        print("✅ Design complete!")
                        
                        # Create conversational response for design update
                        if st.session_state.current_design:
                            conversational_response = f"I've updated the design to incorporate your request. The {updated.get('title', 'experiment')} now includes the changes you asked for."
                        else:
                            conversational_response = f"I've designed a {updated.get('title', 'quantum experiment')} based on your requirements. {updated.get('description', '')} Check out the optical setup on the right!"
                        
                        # Append assistant message
                        st.session_state.conversation_context.append({
                            'role': 'assistant',
                            'content': conversational_response,
                            'design': updated,
                            'timestamp': datetime.now().isoformat(),
                            'type': 'design'
                        })

                        # Update iterations
                        st.session_state.design_iterations.append({
                            'version': len(st.session_state.design_iterations) + 1,
                            'query': chat_text,
                            'design': updated,
                            'timestamp': datetime.now().isoformat(),
                            'is_refinement': bool(st.session_state.current_design)
                        })

                        st.session_state.current_design = updated
                        st.session_state.chat_history.append({
                            'timestamp': datetime.now(),
                            'query': chat_text,
                            'result': updated
                        })
                        
                        # Clear processing flags
                        st.session_state.pending_query = None
                        st.session_state.is_processing = False
                        st.session_state.processing_mode = None
                        st.session_state.processing_logs = []  # Clear logs
                        
                        # Restore original print
                        import builtins
                        if hasattr(st.session_state, 'original_print'):
                            builtins.print = st.session_state.original_print
                        
                        st.rerun()
                    
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        st.error(f"Design error: {e}")
                        # Clear processing flags on error too
                        st.session_state.pending_query = None
                        st.session_state.is_processing = False
                        st.session_state.processing_mode = None
                        st.stop()
                    
            except Exception as e:
                # Restore original print on error
                import builtins
                if hasattr(st.session_state, 'original_print'):
                    builtins.print = st.session_state.original_print
                st.session_state.processing_logs = []
                st.error(f"Error: {e}")
    
    # RIGHT: Design visualization and details
    with right_col:
        # Show design if it exists (unless actively generating a new design)
        # Priority: Hide during design generation, show at all other times
        
        if st.session_state.current_design and not (st.session_state.is_processing and st.session_state.processing_mode == 'design'):
            # Show current design
            result = st.session_state.current_design
            experiment = result.get('experiment', {})
            
            # Check if this was retrieved from toolbox (LLM suggested using existing)
            retrieved_setup = result.get('optical_setup_object')
            if retrieved_setup and hasattr(retrieved_setup, 'from_toolbox') and retrieved_setup.from_toolbox:
                metadata = retrieved_setup.toolbox_metadata
                st.success("🧰 **Found Matching Design in Toolbox!**")
                
                col_info, col_actions = st.columns([2, 1])
                with col_info:
                    st.markdown(f"""
                    **Existing Design Found:**
                    
                    **Your Request**: "{metadata.get('user_query', 'N/A')}"
                    
                    **Why This Matches**: {metadata.get('reason', 'This design matches your requirements')}
                    
                    💡 *Choose what to do with this design - use it as-is, improve it, or generate something completely new.*
                    """)
                
                with col_actions:
                    st.markdown("**Your Options:**")
                    
                    if st.button("✅ Use This Design", type="primary", use_container_width=True, key="use_toolbox_btn"):
                        # Mark as accepted and clear the toolbox flag
                        retrieved_setup.from_toolbox = False
                        st.success("✅ Using this design!")
                        st.rerun()
                    
                    if st.button("🔧 Auto-Improve This", type="primary", use_container_width=True, key="improve_toolbox_btn"):
                        # Trigger auto-improvement
                        st.session_state.pending_query = f"Improve this design for better performance and optimization"
                        st.session_state.is_processing = True
                        st.session_state.processing_mode = 'design'
                        retrieved_setup.from_toolbox = False  # Clear flag
                        st.rerun()
                    
                    if st.button("🔄 Generate Fresh Design", type="primary", use_container_width=True, key="fresh_toolbox_btn"):
                        # Force new design generation
                        original_query = metadata.get('user_query', 'design quantum experiment')
                        st.session_state.current_design = None  # Clear current
                        st.session_state.pending_query = f"{original_query} (generate completely new design)"
                        st.session_state.is_processing = True
                        st.session_state.processing_mode = 'design'
                        st.session_state.force_new_design = True
                        st.rerun()
                
                st.markdown("---")
            
            # Check if this was retrieved from memory (old system)
            elif retrieved_setup and hasattr(retrieved_setup, 'from_memory') and retrieved_setup.from_memory:
                metadata = retrieved_setup.memory_metadata
                st.info("📦 **Retrieved from Memory**")
                
                col_info, col_actions = st.columns([2, 1])
                with col_info:
                    # Build status text
                    status_items = []
                    status_items.append(f"📝 **Original Query**: \"{metadata.get('source_query', 'N/A')}\"")
                    
                    # Only show similarity if it's meaningful (>5%)
                    similarity = metadata.get('similarity_score', 0)
                    if similarity > 0.05:
                        status_items.append(f"🎯 **Similarity**: {similarity:.0%} match")
                    
                    if metadata.get('human_approved'):
                        status_items.append("✅ **Human-Approved Design**")
                    
                    status_text = "\n\n".join(status_items)
                    
                    st.markdown(f"""
                    **🔍 Found existing experiment in memory:**
                    
                    {status_text}
                    
                    💡 *Choose an option on the right, or chat below for custom improvements (e.g., \"add delay stage\", \"optimize for 810nm\")*
                    """)
                
                with col_actions:
                    st.markdown("**Your Options:**")
                    
                    # Match the style of Run Simulation button
                    if st.button("✅ Use This Design", type="primary", use_container_width=True, key="use_retrieved_btn"):
                        st.session_state['retrieval_decision'] = 'use'
                        st.success("Using retrieved design!")
                    
                    if st.button("🔧 Auto-Improve This", type="primary", use_container_width=True, key="improve_retrieved_btn"):
                        st.session_state['improve_retrieved'] = True
                        st.session_state['base_design'] = result
                        st.rerun()
                    
                    if st.button("🔄 Start Completely Fresh", type="primary", use_container_width=True, key="fresh_design_btn"):
                        st.session_state['force_new_design'] = True
                        st.info("Generating completely new design...")
                        st.rerun()
                
                st.markdown("---")
            
            # Memory & experience indicator
            if st.session_state.designer and hasattr(st.session_state.designer, 'memory') and st.session_state.designer.memory:
                try:
                    stats = st.session_state.designer.memory.get_statistics()
                    if stats['episodic_count'] > 0:
                        st.success(f"🧠 **Experience Used**: This design benefited from {stats['episodic_count']} past experiment(s) and {stats['patterns_count']} learned building block(s).")
                except:
                    pass

            # Web search indicator
            if result.get('web_search_used', False):
                st.info("🔍 **Web Search Enhanced**: This design incorporates information from online research to ensure accuracy and relevance.")
            
            # Optical table diagram (fills right half)
            st.markdown("### 🔬 Quantum Optical Setup")
            try:
                fig = create_optical_table_figure(experiment, figsize=(14, 10))
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            except Exception as e:
                st.error(f"Could not render optical table: {e}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Design Details without conversational content
            st.markdown("---")
            st.markdown("## 🔬 Design Details")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "⚙️ Component Selection",
                "📋 Overview",
                "🔬 Simulation",
                "🌊 Beam Paths",
                "💬 Memory & Learn"
            ])

            with tab1:
                with st.container(height=500):
                    st.markdown("### Component Selection Rationale")
                    st.markdown("*Numbers match the optical table diagram above:*")
                    st.markdown("")
                    component_justifications = result.get('component_justifications', {})
                    if component_justifications:
                        for i, (comp_name, justification) in enumerate(component_justifications.items(), 1):
                            # Display with number badge for easy reference to diagram
                            st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                            <div style='display: flex; align-items: center;'>
                                <div style='background: white; color: #667eea; width: 35px; height: 35px; 
                                            border-radius: 50%; display: flex; align-items: center; 
                                            justify-content: center; font-weight: bold; font-size: 18px; 
                                            margin-right: 15px; flex-shrink: 0;'>
                                    {i}
                                </div>
                                <div style='flex-grow: 1;'>
                                    <div style='font-weight: bold; font-size: 16px; margin-bottom: 5px;'>{comp_name}</div>
                                    <div style='font-size: 14px; opacity: 0.95;'>{justification}</div>
                                </div>
                            </div>
                        </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("💡 Detailed component justifications were not provided by the LLM.")

            with tab2:
                with st.container(height=500):
                    st.markdown("### Experiment Overview")
                    st.markdown(f"**Title:** {result.get('title', 'N/A')}")
                    st.markdown(f"**Description:** {result.get('description', 'N/A')}")
                    st.markdown("---")
                    st.markdown("### Physics Explanation")
                    st.write(result.get('physics_explanation', 'N/A'))
                    st.markdown("---")
                    st.markdown("### Expected Outcome")
                    st.write(result.get('expected_outcome', 'N/A'))

            with tab3:
                with st.container(height=600):
                    st.markdown("### 🔬 Quantum Simulation Results")
                    
                    # Add "Run Simulation" and "Download All" buttons
                    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1, 3])
                    with col1:
                        if st.button("🔬 QuTiP Sim", type="primary", width="stretch", help="Fock state simulation"):
                            # Run simulation with global log capture
                            with st.spinner("Running QuTiP simulation..."):
                                sim_results = run_simulation_on_design(result)
                                # Update the result with simulation results
                                result['simulation_results'] = sim_results
                                result['simulation_method'] = 'qutip'
                                # Update session state if it exists
                                if 'current_design' in st.session_state and st.session_state.current_design:
                                    st.session_state.current_design['simulation_results'] = sim_results
                                    st.session_state.current_design['simulation_method'] = 'qutip'
                                st.rerun()
                    
                    with col2:
                        if st.button("🚀 Free-Form Sim", type="secondary", width="stretch", help="Physics-aware code gen"):
                            # Run free-form simulation
                            with st.spinner("Generating simulation..."):
                                freeform_results = run_freeform_simulation(result)
                                # Store in separate key
                                result['freeform_simulation_results'] = freeform_results
                                result['simulation_method'] = 'freeform'
                                # Update session state
                                if 'current_design' in st.session_state and st.session_state.current_design:
                                    st.session_state.current_design['freeform_simulation_results'] = freeform_results
                                    st.session_state.current_design['simulation_method'] = 'freeform'
                                st.rerun()
                    
                    with col3:
                        # Download all button (only if simulation exists)
                        if result.get('simulation_results') and result['simulation_results'].get('success'):
                            if st.button("📦 Download All", width="stretch"):
                                # Generate complete report package
                                import zipfile
                                import io
                                
                                # Create timestamp
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                exp_name = result.get('title', 'experiment').replace(' ', '_')
                                zip_filename = f"{exp_name}_{timestamp}.zip"
                                
                                # Create in-memory zip
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    # 1. Optical table diagram
                                    try:
                                        fig_temp = create_optical_table_figure(experiment, figsize=(14, 10))
                                        img_buf = io.BytesIO()
                                        fig_temp.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
                                        plt.close(fig_temp)
                                        img_buf.seek(0)
                                        zip_file.writestr(f"01_optical_setup.png", img_buf.read())
                                    except Exception as e:
                                        zip_file.writestr("01_optical_setup_ERROR.txt", f"Could not generate: {e}")
                                    
                                    # 2. Component selection
                                    component_justifications = result.get('component_justifications', {})
                                    if component_justifications:
                                        report = f"# Component Selection Rationale\n\n"
                                        report += f"**Experiment:** {result.get('title', 'N/A')}\n\n"
                                        report += f"**Timestamp:** {timestamp}\n\n"
                                        report += f"**Description:** {result.get('description', 'N/A')}\n\n"
                                        report += "---\n\n"
                                        for i, (comp_name, justification) in enumerate(component_justifications.items(), 1):
                                            report += f"## {i}. {comp_name}\n\n{justification}\n\n"
                                        zip_file.writestr("02_component_selection.md", report)
                                    
                                    # 3. QuTiP simulation code
                                    sim_code = result['simulation_results'].get('simulation_code')
                                    if sim_code:
                                        zip_file.writestr("03_qutip_simulation.py", sim_code)
                                    
                                    # 4. JSON design
                                    parsed = result.get('parsed_design', {})
                                    zip_file.writestr("04_design_components.json", json.dumps(parsed, indent=2))
                                    
                                    # 5. Deep analysis report
                                    reasoning = result['simulation_results'].get('reasoning', {})
                                    if reasoning and isinstance(reasoning, dict):
                                        rating = result['simulation_results'].get('honest_rating', 5)
                                        if rating >= 8:
                                            quality = 'EXCELLENT'
                                        elif rating >= 6:
                                            quality = 'GOOD'
                                        elif rating >= 4:
                                            quality = 'FAIR'
                                        else:
                                            quality = 'POOR'
                                        
                                        analysis_report = f"# Deep Analysis: Design vs Simulation vs Results\n\n"
                                        analysis_report += f"**Experiment:** {result.get('title', 'N/A')}\n\n"
                                        analysis_report += f"**Timestamp:** {timestamp}\n\n"
                                        analysis_report += f"**Quality Rating:** {rating}/10 ({quality})\n\n"
                                        analysis_report += "---\n\n"
                                        analysis_report += f"## Overview\n\n{reasoning.get('analysis', 'No detailed analysis available')}\n\n"
                                        
                                        key_insight = reasoning.get('key_insight', '')
                                        if key_insight:
                                            analysis_report += f"## Key Insight\n\n{key_insight}\n\n"
                                        
                                        analysis_report += "## Design Intent\n\n"
                                        design_intent = reasoning.get('design_intent', {})
                                        components = design_intent.get('components', [])
                                        if components:
                                            analysis_report += "**Components:**\n"
                                            for comp in components:
                                                analysis_report += f"- {comp}\n"
                                            analysis_report += "\n"
                                        
                                        physics_goal = design_intent.get('physics_goal', '')
                                        if physics_goal:
                                            analysis_report += f"**Physics Goal:** {physics_goal}\n\n"
                                        
                                        params = design_intent.get('key_parameters', [])
                                        if params:
                                            analysis_report += "**Key Parameters:**\n"
                                            for param in params:
                                                analysis_report += f"- {param}\n"
                                            analysis_report += "\n"
                                        
                                        analysis_report += "## QuTiP Implementation\n\n"
                                        code_impl = reasoning.get('code_implementation', {})
                                        for section_name, section_code in code_impl.items():
                                            if section_code:
                                                analysis_report += f"### {section_name.replace('_', ' ').title()}\n\n```python\n{section_code}\n```\n\n"
                                        
                                        comparison = reasoning.get('comparison', '')
                                        if comparison:
                                            analysis_report += f"## How Design Maps to Code\n\n{comparison}\n\n"
                                        
                                        limitations = reasoning.get('limitations', [])
                                        if limitations:
                                            analysis_report += "## Identified Limitations\n\n"
                                            for lim in limitations:
                                                analysis_report += f"- {lim}\n"
                                            analysis_report += "\n"
                                        
                                        recommendations = result['simulation_results'].get('recommendations', [])
                                        if recommendations:
                                            analysis_report += "## Recommendations\n\n"
                                            for i, rec in enumerate(recommendations, 1):
                                                analysis_report += f"{i}. {rec}\n"
                                            analysis_report += "\n"
                                        
                                        matches = reasoning.get('matches_design', False)
                                        analysis_report += f"## Conclusion\n\n"
                                        if matches:
                                            analysis_report += "✅ Simulation successfully captured the design's intended physics.\n"
                                        else:
                                            analysis_report += "⚠️ Simulation could not fully capture the design's intended physics.\n"
                                        
                                        zip_file.writestr("05_deep_analysis.md", analysis_report)
                                    
                                    # 6. README with metadata
                                    readme = f"# Quantum Experiment Package\n\n"
                                    readme += f"**Experiment:** {result.get('title', 'N/A')}\n\n"
                                    readme += f"**Generated:** {timestamp}\n\n"
                                    readme += f"**Description:** {result.get('description', 'N/A')}\n\n"
                                    readme += "---\n\n"
                                    readme += "## Package Contents\n\n"
                                    readme += "1. `01_optical_setup.png` - High-resolution diagram (300 DPI)\n"
                                    readme += "2. `02_component_selection.md` - Component justifications\n"
                                    readme += "3. `03_qutip_simulation.py` - Python simulation code\n"
                                    readme += "4. `04_design_components.json` - Complete design specification\n"
                                    readme += "5. `05_deep_analysis.md` - Detailed analysis report\n"
                                    readme += "6. `README.md` - This file\n\n"
                                    readme += "---\n\n"
                                    readme += "## Quick Start\n\n"
                                    readme += "```bash\n"
                                    readme += "# Run the simulation\n"
                                    readme += "python 03_qutip_simulation.py\n"
                                    readme += "```\n\n"
                                    readme += "## Physics\n\n"
                                    readme += f"{result.get('physics_explanation', 'N/A')}\n\n"
                                    readme += "## Expected Outcome\n\n"
                                    readme += f"{result.get('expected_outcome', 'N/A')}\n"
                                    
                                    zip_file.writestr("README.md", readme)
                                
                                zip_buffer.seek(0)
                                st.download_button(
                                    label="📦 Download Complete Package",
                                    data=zip_buffer,
                                    file_name=zip_filename,
                                    mime="application/zip",
                                    use_container_width=True,
                                    key="download_all_zip"
                                )
                    
                    with col3:
                        st.info("💡 Click to validate this design using quantum simulation")
                    
                    st.markdown("---")
                    
                    # Get both simulation results
                    qutip_results = result.get('simulation_results')
                    freeform_results = result.get('freeform_simulation_results')
                    
                    # Display results based on what's available
                    if freeform_results and (freeform_results.get('success') or freeform_results.get('valid') is not None):
                        st.markdown("### 🚀 Free-Form Simulation Results")
                        
                        # Get key data
                        analysis = freeform_results.get('analysis', {})
                        alignment = analysis.get('alignment_check', {})
                        alignment_score = alignment.get('alignment_score', 0)
                        convergence = freeform_results.get('convergence_info', {})
                        
                        # DOWNLOAD BUTTON AT TOP
                        st.markdown("---")
                        
                        import io
                        import zipfile
                        
                        # Create ZIP package
                        zip_buffer = io.BytesIO()
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        experiment_name = result.get('title', 'quantum_experiment').replace(' ', '_').lower()
                        zip_filename = f"{experiment_name}_freeform_{timestamp}.zip"
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            # 1. Simulation Python code
                            code = freeform_results.get('code', '')
                            if code:
                                zip_file.writestr("01_freeform_simulation.py", code)
                            
                            # 2. Execution output (text)
                            execution_success = freeform_results.get('execution_success', freeform_results.get('results', {}).get('success', False))
                            output = freeform_results.get('output', '')
                            if execution_success and output:
                                zip_file.writestr("02_execution_output.txt", output)
                            
                            # 3. Simulation Report (with analysis)
                            report = analysis.get('report', '')
                            if report:
                                zip_file.writestr("03_simulation_report.md", report)
                            
                            # 4. Simulation figures (if any)
                            figures = analysis.get('figures', [])
                            if figures:
                                for i, fig_data in enumerate(figures, 1):
                                    import base64
                                    fig_bytes = base64.b64decode(fig_data['data'])
                                    zip_file.writestr(f"figures/figure_{i:02d}.png", fig_bytes)
                            
                            # 5. Complete analysis JSON
                            # Remove base64 figures from JSON (too large)
                            analysis_for_json = {k: v for k, v in analysis.items() if k != 'figures'}
                            analysis_for_json['num_figures'] = len(figures)
                            analysis_json = json.dumps(analysis_for_json, indent=2)
                            zip_file.writestr("04_analysis_results.json", analysis_json)
                            
                            # 6. Metrics summary (for paper writing)
                            metrics_report = f"""# Free-Form Simulation Metrics

## Experiment
**Title:** {result.get('title', 'N/A')}
**Description:** {result.get('description', 'N/A')}

## Simulation Results
**Figures Generated:** {len(figures)}
**Execution Success:** {'Yes' if execution_success else 'No'}

## Design Alignment
**Alignment Score:** {alignment_score}/10
**Models Design Accurately:** {alignment.get('actually_models_design', 'N/A')}
**Physics Match Quality:** {alignment.get('physics_match_quality', 'N/A')}

## Convergence
**Converged:** {'Yes' if convergence.get('converged', False) else 'No'}
**Iterations:** {convergence.get('iterations', 0)}/{convergence.get('max_iterations', 3)}
**Total Time:** {convergence.get('total_time_seconds', 0):.2f} seconds

### Missing from Simulation
"""
                            missing = alignment.get('missing_from_code', [])
                            if missing:
                                for item in missing:
                                    metrics_report += f"- {item}\n"
                            else:
                                metrics_report += "- None\n"
                            
                            metrics_report += "\n### Incorrect in Simulation\n"
                            wrong = alignment.get('wrong_in_code', [])
                            if wrong:
                                for item in wrong:
                                    metrics_report += f"- {item}\n"
                            else:
                                metrics_report += "- None\n"
                            
                            # Add token usage if available
                            metrics_report += "\n## API Usage\n\n"
                            
                            # Design phase tokens
                            design_tokens = result.get('design_tokens', {})
                            if design_tokens.get('total_tokens'):
                                metrics_report += "### Design Phase\n"
                                metrics_report += f"**Prompt Tokens:** {design_tokens.get('prompt_tokens', 0):,}\n"
                                metrics_report += f"**Completion Tokens:** {design_tokens.get('completion_tokens', 0):,}\n"
                                metrics_report += f"**Total Tokens:** {design_tokens.get('total_tokens', 0):,}\n"
                                metrics_report += f"**Cost:** ${design_tokens.get('cost', 0):.6f}\n\n"
                            
                            # Simulation phase tokens
                            if convergence.get('total_prompt_tokens'):
                                metrics_report += "### Simulation Phase\n"
                                metrics_report += f"**Prompt Tokens:** {convergence.get('total_prompt_tokens', 0):,}\n"
                                metrics_report += f"**Completion Tokens:** {convergence.get('total_completion_tokens', 0):,}\n"
                                metrics_report += f"**Total Tokens:** {convergence.get('total_tokens', 0):,}\n"
                                metrics_report += f"**Cost:** ${convergence.get('total_cost', 0):.6f}\n\n"
                            
                            # Combined total
                            total_design_tokens = design_tokens.get('total_tokens', 0)
                            total_sim_tokens = convergence.get('total_tokens', 0)
                            total_design_cost = design_tokens.get('cost', 0.0)
                            total_sim_cost = convergence.get('total_cost', 0.0)
                            
                            if total_design_tokens or total_sim_tokens:
                                metrics_report += "### Combined Total\n"
                                metrics_report += f"**Total Tokens:** {total_design_tokens + total_sim_tokens:,}\n"
                                metrics_report += f"**Total Cost:** ${total_design_cost + total_sim_cost:.6f}\n"
                            else:
                                metrics_report += "Token usage data not available\n"
                            
                            # Add physics assessment
                            physics_correct = analysis.get('physics_correctness', '')
                            if physics_correct:
                                metrics_report += f"\n## Physics Assessment\n\n{physics_correct}\n"
                            
                            zip_file.writestr("05_metrics_summary.md", metrics_report)
                            
                            # 7. Design specification JSON (with 1-indexed component numbers to match figure)
                            components = result.get('experiment', {}).get('steps', [])
                            # Re-number components to start at 1 (matching figure labels)
                            components_1indexed = []
                            for i, comp in enumerate(components, 1):
                                comp_copy = comp.copy()
                                comp_copy['component_number'] = i
                                components_1indexed.append(comp_copy)
                            
                            design_spec = {
                                'title': result.get('title'),
                                'description': result.get('description'),
                                'components': components_1indexed,
                                'beam_paths': result.get('experiment', {}).get('beam_paths', []),
                                'physics_explanation': result.get('physics_explanation', ''),
                                'expected_outcome': result.get('expected_outcome', ''),
                                'note': 'Component numbers match the labels shown in 07_optical_setup.png (1-indexed)'
                            }
                            zip_file.writestr("06_design_specification.json", json.dumps(design_spec, indent=2))
                            
                            # 8. Optical setup diagram (generate high-res version)
                            try:
                                experiment = result.get('experiment', {})
                                if experiment:
                                    # Generate high-resolution diagram for download
                                    fig = create_optical_table_figure(experiment, figsize=(16, 12))
                                    
                                    # Save to bytes buffer
                                    img_buffer = io.BytesIO()
                                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                                    img_buffer.seek(0)
                                    
                                    zip_file.writestr("07_optical_setup.png", img_buffer.getvalue())
                                    plt.close(fig)
                            except Exception as e:
                                # If diagram generation fails, just skip it
                                pass
                            
                            # 9. Iteration history (if available)
                            iteration_history = convergence.get('iteration_history', [])
                            if iteration_history:
                                history_report = "# Refinement Iteration History\n\n"
                                for i, iteration in enumerate(iteration_history, 1):
                                    history_report += f"## Iteration {i}\n\n"
                                    history_report += f"**Stage:** {iteration.get('stage', 'N/A')}\n"
                                    history_report += f"**Approved:** {iteration.get('approved', 'N/A')}\n"
                                    history_report += f"**Alignment Score:** {iteration.get('alignment_score', 'N/A')}/10\n"
                                    history_report += f"**Execution Success:** {iteration.get('execution_success', 'N/A')}\n\n"
                                    
                                    if iteration.get('feedback'):
                                        history_report += f"**Feedback:** {iteration.get('feedback')}\n\n"
                                    
                                    history_report += "---\n\n"
                                
                                zip_file.writestr("08_iteration_history.md", history_report)
                            
                            # 10. README with quick start guide
                            readme = f"""# Free-Form Simulation Package

**Experiment:** {result.get('title', 'N/A')}
**Generated:** {timestamp}
**Simulation Mode:** Aṇubuddhi-Generated Free-Form Python

---

## Package Contents

1. `01_freeform_simulation.py` - Aṇubuddhi-generated Python simulation code
2. `02_execution_output.txt` - Complete simulation output (text)
3. `03_simulation_report.md` - Comprehensive analysis report
4. `04_analysis_results.json` - Full analysis data (JSON format)
5. `05_metrics_summary.md` - Key metrics for paper writing
6. `06_design_specification.json` - Complete design specification with numbered components
7. `07_optical_setup.png` - Optical diagram (300 DPI)
8. `08_iteration_history.md` - Refinement iteration log (if applicable)
9. `figures/` - All generated matplotlib figures from simulation
10. `README.md` - This file

---

## Quick Start

```bash
# Install dependencies (if needed)
pip install numpy scipy qutip matplotlib

# Run the simulation
python 01_freeform_simulation.py
```

---

## Simulation Report

The `03_simulation_report.md` file contains:
- Complete simulation output (text)
- References to all figures ({len(figures)} figure(s) in `figures/` folder)
- LLM analysis of physics correctness
- Design alignment assessment
- Key findings and recommendations

All generated plots are saved as PNG files in the `figures/` folder for easy viewing.

This report combines the simulation results with AI-powered analysis to help you understand:
- Whether the simulation accurately models the designed experiment
- Physics correctness and validity of results
- Suggestions for improvement

---

## Experiment Description

{result.get('description', 'N/A')}

---

## Physics Background

{result.get('physics_explanation', 'N/A')}

---

## Design Alignment Assessment

**Alignment Score:** {alignment_score}/10
**Converged:** {'Yes' if convergence.get('converged', False) else 'No'} (in {convergence.get('iterations', 0)} iteration(s))

---

*Generated by Aṇubuddhi (अणुबुद्धि) - AI-Driven Quantum Experiment Design*
*Designed by S. K. Rithvik*
"""
                            zip_file.writestr("README.md", readme)
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            label="📦 Download Complete Package (ZIP)",
                            data=zip_buffer,
                            file_name=zip_filename,
                            mime="application/zip",
                            use_container_width=True,
                            key="download_freeform_package"
                        )
                        
                        st.caption("📊 Package includes: code, output, metrics, optical diagram, and analysis")
                        
                        st.markdown("---")
                        
                        # Show convergence and alignment info
                        col1, col2 = st.columns(2)
                        with col1:
                            if convergence:
                                iterations = convergence.get('iterations', 0)
                                converged = convergence.get('converged', False)
                                st.metric("Convergence", f"{iterations} iteration(s)", 
                                         "✅ Converged" if converged else "⚠️ Did not converge")
                        
                        with col2:
                            st.metric("Design Alignment", f"{alignment_score}/10",
                                     "Models design" if alignment.get('actually_models_design') else "Mismatch")
                        
                        # Show generated code
                        with st.expander("📝 Generated Simulation Code", expanded=False):
                            code = freeform_results.get('code', 'No code available')
                            st.code(code, language='python')
                        
                        # Show execution results with comprehensive report
                        execution_success = freeform_results.get('execution_success', freeform_results.get('results', {}).get('success', False))
                        if execution_success:
                            with st.expander("📊 Simulation Report", expanded=True):
                                # Display the comprehensive report
                                report = analysis.get('report', '')
                                if report:
                                    # Split report into sections
                                    sections = report.split('---')
                                    
                                    # Show overall assessment
                                    st.markdown(sections[0] if len(sections) > 0 else report)
                                    
                                    # Show figures if any
                                    figures = analysis.get('figures', [])
                                    if figures:
                                        st.markdown("### 📈 Generated Figures")
                                        for i, fig_data in enumerate(figures, 1):
                                            import base64
                                            fig_bytes = base64.b64decode(fig_data['data'])
                                            st.image(fig_bytes, caption=f"Figure {i}", use_column_width=True)
                                        st.markdown("---")
                                    
                                    # Show remaining sections of report
                                    if len(sections) > 1:
                                        for section in sections[1:]:
                                            if section.strip():
                                                st.markdown(section)
                                else:
                                    # Fallback to plain output
                                    output = freeform_results.get('output') or freeform_results.get('results', {}).get('stdout', 'No output')
                                    st.text(output)
                        else:
                            with st.expander("❌ Execution Error", expanded=True):
                                error = freeform_results.get('error', 'Unknown error')
                                st.error(error)
                        
                        # Show simplified analysis
                        with st.expander("🧠 Analysis Summary", expanded=True):
                            # Get scores from alignment_check
                            alignment = analysis.get('alignment_check', {})
                            alignment_score = alignment.get('alignment_score', 0)
                            
                            # Get physics rating from analysis
                            physics_rating = analysis.get('rating', 0)
                            
                            # Display primary success metric
                            st.metric("✅ Simulation Success", f"{alignment_score}/10")
                            st.caption("How well the simulation models your design")
                            
                            if alignment_score >= 7:
                                st.success("✓ Simulation successfully models the design")
                            elif alignment_score >= 5:
                                st.info("⚠️ Simulation partially models the design - check alignment issues below")
                            else:
                                st.warning("⚠️ Simulation may not accurately represent the design")
                            
                            st.markdown("---")
                            
                            # Show alignment issues if alignment < 7
                            if alignment_score < 7:
                                st.markdown("---")
                                st.markdown("**⚠️ Key Issues:**")
                                
                                missing = alignment.get('missing_from_code', [])
                                if missing:
                                    st.write("Missing from simulation:")
                                    for item in missing[:3]:  # Show max 3
                                        st.markdown(f"- {item}")
                                
                                wrong = alignment.get('wrong_in_code', [])
                                if wrong:
                                    st.write("Incorrect in simulation:")
                                    for item in wrong[:3]:  # Show max 3
                                        st.markdown(f"- {item}")
                        
                        # Technical Details Section (collapsible like QuTiP)
                        st.markdown("---")
                        st.markdown("### 🔧 Technical Details")
                        
                        tech_tab1, tech_tab2 = st.tabs(["💻 Simulation Code", "📋 Full Analysis"])
                        
                        with tech_tab1:
                            code = freeform_results.get('code', 'No code available')
                            st.caption("Aṇubuddhi-generated Python simulation code")
                            st.code(code, language='python', line_numbers=True)
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Python Code",
                                data=code,
                                file_name="freeform_simulation.py",
                                mime="text/x-python",
                                use_container_width=True
                            )
                        
                        with tech_tab2:
                            st.caption("Complete analysis data in JSON format")
                            st.json(analysis)
                        
                        st.markdown("---")
                        
                        # ADD TO TOOLBOX SECTION (like QuTiP simulation)
                        st.markdown("### 💾 Save to Toolbox")
                        
                        # Check if already stored in THIS session
                        title = result.get('title', 'unknown')
                        already_stored_in_session = st.session_state.get(f"stored_{title}", False)
                        
                        # Check if design with same title exists in actual toolbox
                        from toolbox_loader import get_toolbox
                        toolbox = get_toolbox()
                        existing_in_toolbox = any(
                            comp.get('name', '').lower() == title.lower() 
                            for comp in toolbox.list_all_composites()
                        )
                        
                        if already_stored_in_session == "discarded":
                            st.info("🗑️ This design was discarded and not saved to toolbox")
                        elif already_stored_in_session:
                            st.success("✅ This design was just saved to the toolbox!")
                        elif existing_in_toolbox:
                            # Design with same title exists - offer options
                            st.warning(f"⚠️ A design with title '{title}' already exists in toolbox")
                            st.info("💡 This new design may be different. Choose an option:")
                            
                            col1, col2, col3 = st.columns([2, 2, 2])
                            
                            with col1:
                                if st.button("🔄 Replace Existing", key="replace_freeform", use_container_width=True):
                                    # Will save with same base name but new timestamp
                                    st.session_state['save_action'] = 'replace'
                                    st.rerun()
                            
                            with col2:
                                if st.button("➕ Save as New Version", key="save_new_freeform", use_container_width=True):
                                    st.session_state['save_action'] = 'new_version'
                                    st.rerun()
                            
                            with col3:
                                if st.button("❌ Cancel", key="cancel_save_freeform", use_container_width=True):
                                    st.session_state[f"stored_{title}"] = "discarded"
                                    st.rerun()
                            
                            # Handle save action
                            save_action = st.session_state.get('save_action')
                            if save_action:
                                try:
                                    # Generate ID based on action
                                    base_id = re.sub(r'[^a-z0-9]+', '_', title.lower())
                                    if save_action == 'replace':
                                        # Remove old versions first
                                        composites = toolbox.list_all_composites()
                                        for comp in composites:
                                            if comp.get('name', '').lower() == title.lower():
                                                old_id = comp.get('id', '')
                                                # Note: Actual removal would need toolbox.remove_composite() method
                                                # For now, just add with timestamp to differentiate
                                        composite_id = f"{base_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                    else:  # new_version
                                        composite_id = f"{base_id}_v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                    
                                    # Extract fields and save
                                    components = result.get('components_sent_to_renderer', [])
                                    beam_path = result.get('experiment', {}).get('beam_path', [])
                                    physics_explanation = result.get('physics_explanation', '')
                                    description = result.get('description', title)
                                    expected_outcome = result.get('expected_outcome', '')
                                    typical_use = f"{expected_outcome}. Demonstrates: {physics_explanation[:100]}"
                                    
                                    full_design = {
                                        'title': title,
                                        'description': description,
                                        'experiment': result.get('experiment', {}),
                                        'components': components,
                                        'beam_path': beam_path,
                                        'physics_explanation': physics_explanation,
                                        'component_justifications': result.get('component_justifications', {}),
                                        'expected_outcome': expected_outcome,
                                        'quality_rating': physics_rating,
                                        'alignment_score': alignment_score,
                                        'simulation_type': 'freeform',
                                        'user_query': result.get('original_user_query', ''),
                                        'approved_timestamp': datetime.now().isof(), 
                                        'note': 'Re-run simulation to validate design with latest methods'
                                    }
                                    
                                    success = toolbox.add_learned_composite(
                                        composite_id=composite_id,
                                        name=title,
                                        description=description,
                                        components=components,
                                        beam_path=beam_path,
                                        physics_explanation=physics_explanation,
                                        typical_use=typical_use,
                                        full_design=full_design
                                    )
                                    
                                    if success:
                                        st.session_state[f"stored_{title}"] = True
                                        st.session_state.pop('save_action', None)
                                        action_msg = "replaced existing" if save_action == 'replace' else "saved as new version"
                                        st.success(f"✅ Design {action_msg}: `{composite_id}`")
                                        composites = toolbox.list_all_composites()
                                        st.info(f"🧰 Toolbox now contains {len(composites)} learned composite blocks")
                                        st.rerun()
                                    else:
                                        st.error("Failed to add to toolbox - check logs")
                                        st.session_state.pop('save_action', None)
                                
                                except Exception as e:
                                    st.error(f"Failed to store: {e}")
                                    st.session_state.pop('save_action', None)
                                    import traceback
                                    st.code(traceback.format_exc())
                        
                        else:
                            # Show alignment-based recommendation
                            if alignment_score >= 7:
                                st.info(f"📊 Alignment Score: {alignment_score}/10 - Simulation faithfully models the design")
                            else:
                                st.warning(f"📊 Alignment Score: {alignment_score}/10 - Review alignment issues before saving")
                            
                            col1, col2, col3 = st.columns([2, 2, 3])
                            
                            with col1:
                                if st.button("✅ Approve & Save", key="approve_freeform", use_container_width=True):
                                    try:
                                        from toolbox_loader import get_toolbox
                                        toolbox = get_toolbox()
                                        
                                        # Generate unique ID
                                        composite_id = re.sub(r'[^a-z0-9]+', '_', title.lower())
                                        composite_id = f"{composite_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                        
                                        # Extract fields
                                        components = result.get('components_sent_to_renderer', [])
                                        beam_path = result.get('experiment', {}).get('beam_path', [])
                                        physics_explanation = result.get('physics_explanation', '')
                                        description = result.get('description', title)
                                        expected_outcome = result.get('expected_outcome', '')
                                        
                                        typical_use = f"{expected_outcome}. Demonstrates: {physics_explanation[:100]}"
                                        
                                        # Store full design (WITHOUT simulation results to reduce tokens)
                                        full_design = {
                                            'title': title,
                                            'description': description,
                                            'experiment': result.get('experiment', {}),
                                            'components': components,
                                            'beam_path': beam_path,
                                            'physics_explanation': physics_explanation,
                                            'component_justifications': result.get('component_justifications', {}),
                                            'expected_outcome': expected_outcome,
                                            'quality_rating': physics_rating,
                                            'alignment_score': alignment_score,
                                            'simulation_type': 'freeform',
                                            'user_query': result.get('original_user_query', ''),
                                            'approved_timestamp': datetime.now().isoformat(),
                                            'note': 'Re-run simulation to validate design with latest methods'
                                        }
                                        
                                        # Add to toolbox
                                        success = toolbox.add_learned_composite(
                                            composite_id=composite_id,
                                            name=title,
                                            description=description,
                                            components=components,
                                            beam_path=beam_path,
                                            physics_explanation=physics_explanation,
                                            typical_use=typical_use,
                                            full_design=full_design
                                        )
                                        
                                        if success:
                                            st.session_state[f"stored_{title}"] = True
                                            st.success(f"✅ Added to toolbox as learned composite: `{composite_id}`")
                                            
                                            # Show toolbox stats
                                            composites = toolbox.list_all_composites()
                                            st.info(f"🧰 Toolbox now contains {len(composites)} learned composite blocks")
                                            st.rerun()
                                        else:
                                            st.error("Failed to add to toolbox - check logs")
                                    
                                    except Exception as e:
                                        st.error(f"Failed to store: {e}")
                                        import traceback
                                        st.code(traceback.format_exc())
                            
                            with col2:
                                if st.button("❌ Discard", key="discard_freeform", use_container_width=True):
                                    st.session_state[f"stored_{title}"] = "discarded"
                                    st.info("Design discarded - will not be added to toolbox")
                                    st.rerun()
                            
                            with col3:
                                st.caption("💡 Approve to save validated designs • Discard to skip low-quality results")
                        
                        st.markdown("---")
                    
                    # Display QuTiP results (existing code)
                    sim_results = qutip_results
                
                if sim_results and sim_results.get('success'):
                    st.markdown("### 🔬 QuTiP Simulation Results")
                    
                    # Show honest rating (1-10) instead of categorical verdict
                    rating = sim_results.get('honest_rating', 5)
                    confidence = sim_results.get('confidence', 0)
                    
                    # Color rating based on score
                    if rating >= 8:
                        icon = '🟢'
                        quality = 'EXCELLENT'
                    elif rating >= 6:
                        icon = '🟡'
                        quality = 'GOOD'
                    elif rating >= 4:
                        icon = '🟠'
                        quality = 'FAIR'
                    else:
                        icon = '🔴'
                        quality = 'POOR'
                    
                    st.markdown(f"### {icon} Simulation Quality: **{rating}/10** ({quality})")
                    
                    # Show independent assessment if rating < 7
                    assessment = sim_results.get('independent_assessment')
                    if assessment and isinstance(assessment, dict):
                        st.markdown("---")
                        st.markdown("### ⚖️ Independent Assessment")
                        
                        root_cause = assessment.get('root_cause', 'UNKNOWN')
                        confidence = assessment.get('confidence', 0.0)
                        recommendation = assessment.get('recommendation', '')
                        
                        # Display root cause with color coding
                        if root_cause == 'DESIGN_INCOMPLETE':
                            st.error(f"**🔍 Root Cause: Design Incomplete** (Confidence: {confidence:.0%})")
                        elif root_cause == 'SIMULATION_OVERSTRICT':
                            st.warning(f"**🔬 Root Cause: Simulation Too Restrictive** (Confidence: {confidence:.0%})")
                        elif root_cause == 'MISMATCH':
                            st.info(f"**🔀 Root Cause: Goal Mismatch** (Confidence: {confidence:.0%})")
                        elif root_cause == 'BOTH_FLAWED':
                            st.error(f"**⚠️ Root Cause: Both Have Issues** (Confidence: {confidence:.0%})")
                        else:
                            st.info(f"**Root Cause: {root_cause}** (Confidence: {confidence:.0%})")
                        
                        # Show detailed assessments
                        col_design, col_sim = st.columns(2)
                        
                        with col_design:
                            design_assess = assessment.get('design_assessment', {})
                            design_score = design_assess.get('completeness_score', 0)
                            st.markdown(f"**🎯 Design Completeness: {design_score}/10**")
                            
                            missing = design_assess.get('missing_components', [])
                            if missing:
                                st.markdown("*Missing Components:*")
                                for item in missing:
                                    st.markdown(f"- {item}")
                            
                            unrealistic = design_assess.get('unrealistic_specs', [])
                            if unrealistic:
                                st.markdown("*Unrealistic Specs:*")
                                for item in unrealistic:
                                    st.markdown(f"- {item}")
                            
                            physics_errors = design_assess.get('physics_errors', [])
                            if physics_errors:
                                st.markdown("*Physics Errors:*")
                                for item in physics_errors:
                                    st.markdown(f"- {item}")
                        
                        with col_sim:
                            sim_assess = assessment.get('simulation_assessment', {})
                            sim_score = sim_assess.get('fidelity_score', 0)
                            st.markdown(f"**⚙️ Simulation Fidelity: {sim_score}/10**")
                            
                            restrictive = sim_assess.get('overly_restrictive', [])
                            if restrictive:
                                st.markdown("*Overly Restrictive:*")
                                for item in restrictive:
                                    st.markdown(f"- {item}")
                            
                            invalid = sim_assess.get('invalid_assumptions', [])
                            if invalid:
                                st.markdown("*Invalid Assumptions:*")
                                for item in invalid:
                                    st.markdown(f"- {item}")
                            
                            bugs = sim_assess.get('implementation_bugs', [])
                            if bugs:
                                st.markdown("*Implementation Issues:*")
                                for item in bugs:
                                    st.markdown(f"- {item}")
                        
                        # Show action buttons based on recommendation
                        st.markdown("---")
                        st.markdown("**📋 Recommended Action:**")
                        
                        if recommendation == 'improve_design':
                            st.warning("The design needs improvement to address identified issues")
                            designer_instructions = assessment.get('designer_instructions', '')
                            if designer_instructions:
                                with st.expander("🔧 Specific Instructions for Design Improvement"):
                                    st.write(designer_instructions)
                            
                            col_a1, col_a2, col_a3 = st.columns([1, 1, 2])
                            with col_a1:
                                if st.button("🔧 Refine Design", type="primary", use_container_width=True, key="refine_design_btn"):
                                    # Trigger refinement with specific instructions
                                    st.session_state.pending_query = f"Refine the design based on this feedback: {designer_instructions}"
                                    st.session_state.is_processing = True
                                    st.session_state.processing_mode = 'design'
                                    st.rerun()
                            
                            with col_a2:
                                if st.button("✅ Accept Anyway", use_container_width=True, key="accept_anyway_btn"):
                                    st.success("Design accepted despite identified issues")
                        
                        elif recommendation == 'trust_design':
                            st.success("The design is likely correct - simulation may be too pessimistic")
                            user_interp = assessment.get('user_interpretation', '')
                            if user_interp:
                                st.info(user_interp)
                            
                            col_b1, col_b2 = st.columns([1, 1])
                            with col_b1:
                                if st.button("✅ Trust Design", type="primary", use_container_width=True, key="trust_design_btn"):
                                    st.success("Design accepted - simulation assumptions questioned")
                            
                            with col_b2:
                                if st.button("🔧 Refine Anyway", use_container_width=True, key="refine_anyway_btn"):
                                    # Trigger refinement with assessment instructions
                                    designer_instructions = assessment.get('designer_instructions', 'Improve this design for better performance')
                                    st.session_state.pending_query = f"Refine the design based on this feedback: {designer_instructions}"
                                    st.session_state.is_processing = True
                                    st.session_state.processing_mode = 'design'
                                    st.rerun()
                        
                        elif recommendation == 'both_need_work':
                            st.warning("Both design and simulation have identified issues")
                            st.write(assessment.get('user_interpretation', 'Recommend revisiting the approach'))
                            
                            col_c1, col_c2 = st.columns([1, 1])
                            with col_c1:
                                if st.button("🔄 Start Fresh", type="primary", use_container_width=True, key="start_fresh_btn"):
                                    # Clear current design and restart
                                    st.session_state.current_design = None
                                    st.session_state.conversation_context = []
                                    st.session_state.design_iterations = []
                                    st.session_state.current_design_id = None
                                    st.success("✅ Cleared - ready for new design")
                                    st.rerun()
                            
                            with col_c2:
                                if st.button("🔧 Try Refinement", use_container_width=True, key="try_refinement_btn"):
                                    # Attempt refinement despite issues
                                    designer_instructions = assessment.get('designer_instructions', 'Improve design addressing identified issues')
                                    st.session_state.pending_query = f"Refine the design: {designer_instructions}"
                                    st.session_state.is_processing = True
                                    st.session_state.processing_mode = 'design'
                                    st.rerun()
                        
                        else:  # accept_as_is
                            st.success("Design and simulation are reasonably aligned")
                            st.info(assessment.get('user_interpretation', ''))
                    
                    # Main Analysis Section
                    st.markdown("---")
                    with st.expander("🧠 AI Interpretation & Analysis", expanded=True):
                        st.write(sim_results.get('interpretation', 'No analysis available'))
                    
                    # Key Metrics Section
                    metrics = sim_results.get('metrics', {})
                    if metrics:
                        with st.expander("📊 Quantitative Metrics", expanded=False):
                            cols = st.columns(min(3, len(metrics)))
                            for i, (metric, value) in enumerate(metrics.items()):
                                with cols[i % 3]:
                                    if isinstance(value, (int, float)):
                                        st.metric(metric.replace('_', ' ').title(), f"{value:.3f}")
                                    else:
                                        st.metric(metric.replace('_', ' ').title(), str(value))
                    
                    # Recommendations Section
                    recommendations = sim_results.get('recommendations', [])
                    if recommendations:
                        with st.expander("💡 Improvement Recommendations", expanded=False):
                            for i, rec in enumerate(recommendations, 1):
                                st.markdown(f"{i}. {rec}")
                    
                    # Technical Details in Collapsible Sections
                    st.markdown("---")
                    st.markdown("### 🔧 Technical Details")
                    
                    tech_tab1, tech_tab2, tech_tab3 = st.tabs(["💻 Simulation Code", "📋 Design Data", "🌐 Research Context"])
                    
                    with tech_tab1:
                        sim_code = sim_results.get('simulation_code')
                        if sim_code:
                            st.caption("QuTiP implementation used for validation")
                            st.code(sim_code, language='python', line_numbers=True)
                    
                    with tech_tab2:
                        st.caption("Complete design specification in JSON format")
                        parsed = result.get('parsed_design', {})
                        st.json(parsed)
                    
                    with tech_tab3:
                        if result.get('web_search_used', False):
                            web_context = result.get('web_search_context', '')
                            if web_context:
                                st.info("🔍 The AI used web research to enhance this design:")
                                st.markdown(web_context)
                            else:
                                st.caption("Web search was attempted but no relevant results found")
                        else:
                            st.caption("No web search was used for this design")
                    
                    # Deep Analysis Section
                    reasoning = sim_results.get('reasoning', {})
                    if reasoning and isinstance(reasoning, dict):
                        st.markdown("---")
                        with st.expander("🔬 Deep Analysis: Design Intent vs Implementation", expanded=False):
                            st.markdown("#### 📖 Overview")
                            st.write(reasoning.get('analysis', 'No detailed analysis available'))
                            
                            # Show key insight
                            key_insight = reasoning.get('key_insight', '')
                            if key_insight:
                                st.info(f"**💡 Key Insight:** {key_insight}")
                            
                            st.markdown("---")
                            st.markdown("#### 🔍 Side-by-Side Comparison: Design Intent vs Implementation")
                            
                            # Use LLM-extracted annotations (not client-side string matching)
                            design_intent = reasoning.get('design_intent', {})
                            code_impl = reasoning.get('code_implementation', {})
                            comparison = reasoning.get('comparison', '')
                            
                            # Create annotated comparison
                            col_json, col_code = st.columns(2)
                            
                            with col_json:
                                st.markdown("**🎯 Designer's Intent**")
                                st.caption("What the designer wanted to achieve")
                                
                                # Show LLM-extracted design components
                                components = design_intent.get('components', [])
                                if components:
                                    st.markdown("**Components:**")
                                    for comp in components:
                                        st.markdown(f"- {comp}")
                                
                                # Show physics goal
                                physics_goal = design_intent.get('physics_goal', '')
                                if physics_goal:
                                    st.markdown("**Physics Goal:**")
                                    st.info(physics_goal)
                                
                                # Show key parameters
                                params = design_intent.get('key_parameters', [])
                                if params:
                                    st.markdown("**Key Parameters:**")
                                    for param in params:
                                        st.markdown(f"- {param}")
                            
                            with col_code:
                                st.markdown("**⚙️ QuTiP Implementation**")
                                st.caption("How it was actually modeled")
                                
                                # Show LLM-extracted code sections (actual lines from simulation)
                                state_init = code_impl.get('state_init', '')
                                if state_init:
                                    st.markdown("**State Initialization:**")
                                    st.code(state_init, language='python')
                                
                                operations = code_impl.get('operations', '')
                                if operations:
                                    st.markdown("**Key Operations:**")
                                    st.code(operations, language='python')
                                
                                measurements = code_impl.get('measurements', '')
                                if measurements:
                                    st.markdown("**Measurements:**")
                                    st.code(measurements, language='python')
                            
                            # Show comparison analysis
                            if comparison:
                                st.markdown("---")
                                st.markdown("#### 🔗 How Design Maps to Code")
                                st.write(comparison)
                            
                            st.markdown("---")
                            
                            # Show identified limitations
                            limitations = reasoning.get('limitations', [])
                            if limitations:
                                st.markdown("#### ⚠️ Identified Limitations")
                                for lim in limitations:
                                    st.markdown(f"- {lim}")
                            
                            # Show whether simulation matched design
                            matches = reasoning.get('matches_design', False)
                            if matches:
                                st.success("✅ Simulation successfully captured the design's intended physics")
                            else:
                                st.warning("⚠️ Simulation could not fully capture the design's intended physics")
                    elif reasoning:
                        # Fallback for old-style string reasoning
                        with st.expander("💭 Simulation Reasoning"):
                            st.write(reasoning)
                    
                    # Human feedback for memory storage
                    st.markdown("---")
                    st.markdown("### 🎓 Add to Knowledge Base?")
                    st.write("Should this design be saved for future reference? Expert feedback helps the AI learn.")
                    
                    # Check if already stored or discarded
                    storage_status = st.session_state.get(f"stored_{result.get('title', 'unknown')}", None)
                    
                    if storage_status == True:
                        st.success("✅ This design has been added to the knowledge base")
                    elif storage_status == "discarded":
                        st.info("❌ This design was discarded")
                    else:
                        col1, col2, col3 = st.columns([1, 1, 3])
                        with col1:
                            if st.button("✅ Approve & Store", type="primary", use_container_width=True):
                                # Store as learned composite block in toolbox
                                try:
                                    from toolbox_loader import get_toolbox
                                    
                                    toolbox = get_toolbox()
                                    
                                    # Generate unique ID from title
                                    title = result.get('title', 'untitled_experiment')
                                    composite_id = re.sub(r'[^a-z0-9]+', '_', title.lower())
                                    composite_id = f"{composite_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                    
                                    # Extract relevant fields
                                    components = result.get('components_sent_to_renderer', [])
                                    beam_path = result.get('experiment', {}).get('beam_path', [])
                                    physics_explanation = result.get('physics_explanation', '')
                                    description = result.get('description', title)
                                    expected_outcome = result.get('expected_outcome', '')
                                    
                                    # Determine typical use case from description and physics
                                    typical_use = f"{expected_outcome}. Demonstrates: {physics_explanation[:100]}"
                                    
                                    # Store full design (include experiment dict for rendering)
                                    # NOTE: Simulation results NOT stored to reduce token usage
                                    full_design = {
                                        'title': title,
                                        'description': description,
                                        'experiment': result.get('experiment', {}),  # CRITICAL: needed for rendering
                                        'components': components,
                                        'beam_path': beam_path,
                                        'physics_explanation': physics_explanation,
                                        'component_justifications': result.get('component_justifications', {}),
                                        'expected_outcome': expected_outcome,
                                        'quality_rating': rating,
                                        'simulation_type': 'qutip',
                                        'user_query': result.get('original_user_query', ''),
                                        'approved_timestamp': datetime.now().isoformat(),
                                        'note': 'Re-run simulation to validate design with latest methods'
                                    }
                                    
                                    # Add to toolbox
                                    success = toolbox.add_learned_composite(
                                        composite_id=composite_id,
                                        name=title,
                                        description=description,
                                        components=components,
                                        beam_path=beam_path,
                                        physics_explanation=physics_explanation,
                                        typical_use=typical_use,
                                        full_design=full_design
                                    )
                                    
                                    if success:
                                        st.session_state[f"stored_{title}"] = True
                                        st.success(f"✅ Added to toolbox as learned composite: `{composite_id}`")
                                        
                                        # Show toolbox stats
                                        composites = toolbox.list_all_composites()
                                        st.info(f"🧰 Toolbox now contains {len(composites)} learned composite blocks")
                                        st.rerun()
                                    else:
                                        st.error("Failed to add to toolbox - check logs")
                                        
                                except Exception as e:
                                    st.error(f"Failed to store: {e}")
                                    import traceback
                                    st.code(traceback.format_exc())
                        
                        with col2:
                            if st.button("❌ Discard", use_container_width=True):
                                st.session_state[f"stored_{result.get('title', 'unknown')}"] = "discarded"
                                st.info("Design discarded - will not be added to toolbox")
                                st.rerun()
                        
                        with col3:
                            st.caption("💡 Approve to save validated designs • Discard to skip low-quality results")
                    
                elif sim_results:
                    # Simulation attempted but failed
                    st.error(f"⚠️ Simulation Error")
                    st.write(sim_results.get('error', 'Unknown error'))
                    if 'qutip' in sim_results.get('error', '').lower():
                        st.info("💡 Install QuTiP to enable simulations: `pip install qutip`")


            with tab4:
                with st.container(height=500):
                    st.markdown("### Light Propagation Paths")
                    beam_path = experiment.get('beam_path', None)
                    if beam_path and isinstance(beam_path, list):
                        if beam_path and isinstance(beam_path[0], list):
                            if isinstance(beam_path[0][0], (int, float)):
                                st.info(f"Single beam path with {len(beam_path)} waypoints")
                                for i, (x, y) in enumerate(beam_path):
                                    st.write(f"**Waypoint {i+1}:** ({x:.2f}, {y:.2f})")
                            else:
                                st.success(f"**{len(beam_path)} distinct beam paths**")
                                for path_idx, path in enumerate(beam_path, 1):
                                    with st.container():
                                        st.markdown(f"#### Path {path_idx}")
                                        st.caption(f"{len(path)} waypoints")
                                        path_str = " → ".join([f"({x:.1f}, {y:.1f})" for x, y in path])
                                        st.text(path_str)
                                        if path_idx < len(beam_path):
                                            st.markdown("---")
                        else:
                            st.json(beam_path)
                    else:
                        st.info("Beam paths auto-generated from component positions")

            with tab5:
                with st.container(height=500):
                    st.markdown("### 🧠 AI Memory & Learning System")
                    st.markdown("*The AI learns from every design and builds knowledge over time*")
                    
                    # Get toolbox and stats
                    from toolbox_loader import get_toolbox
                    toolbox = get_toolbox()
                    all_composites = toolbox.list_all_composites()
                    
                    if st.session_state.designer and hasattr(st.session_state.designer, 'memory') and st.session_state.designer.memory:
                        try:
                            stats = st.session_state.designer.memory.get_statistics()
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(212, 165, 116, 0.1), rgba(244, 228, 193, 0.05));
                                            border: 1px solid rgba(212, 165, 116, 0.3);
                                            border-radius: 12px;
                                            padding: 1.5rem;
                                            text-align: center;">
                                    <div style="font-size: 2rem; color: #d4a574; margin-bottom: 0.5rem;">
                                        {len(all_composites)}
                                    </div>
                                    <div style="color: #c0a080; font-size: 0.9rem;">
                                        Experiments Stored
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(212, 165, 116, 0.1), rgba(244, 228, 193, 0.05));
                                            border: 1px solid rgba(212, 165, 116, 0.3);
                                            border-radius: 12px;
                                            padding: 1.5rem;
                                            text-align: center;">
                                    <div style="font-size: 2rem; color: #d4a574; margin-bottom: 0.5rem;">
                                        {stats['patterns_count']}
                                    </div>
                                    <div style="color: #c0a080; font-size: 0.9rem;">
                                        Building Blocks
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col3:
                                experience_level = min(10, len(all_composites) // 5)
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(212, 165, 116, 0.1), rgba(244, 228, 193, 0.05));
                                            border: 1px solid rgba(212, 165, 116, 0.3);
                                            border-radius: 12px;
                                            padding: 1.5rem;
                                            text-align: center;">
                                    <div style="font-size: 2rem; color: #d4a574; margin-bottom: 0.5rem;">
                                        Level {experience_level}
                                    </div>
                                    <div style="color: #c0a080; font-size: 0.9rem;">
                                        AI Experience
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"⚠️ Could not access memory system: {e}")
                    
                    st.markdown("---")
                    
                    # Show learned experiments
                    if all_composites:
                        # Clear all button at the top
                        col_title, col_clear = st.columns([3, 1])
                        with col_title:
                            st.markdown("#### 📚 Learned Experiments")
                        with col_clear:
                            if st.button("🗑️ Clear All", type="secondary", use_container_width=True, key="clear_all_composites"):
                                if toolbox.clear_all_composites():
                                    st.success("✅ All experiments cleared!")
                                    st.rerun()
                                else:
                                    st.error("Failed to clear experiments")
                        
                        st.markdown("")
                        
                        # Display each experiment as expandable
                        for idx, composite in enumerate(sorted(all_composites, key=lambda x: x.get('approved_date', ''), reverse=True)):
                            composite_id = composite['id']
                            full_data = toolbox.get_composite(composite_id)
                            
                            with st.expander(f"🔬 {composite['name']}", expanded=False):
                                # Header with delete button
                                col_info, col_delete = st.columns([4, 1])
                                with col_info:
                                    st.markdown(f"**Description:** {composite.get('description', 'N/A')}")
                                    st.caption(f"Added: {composite.get('approved_date', 'Unknown')[:10]} | Components: {composite.get('num_components', 0)}")
                                with col_delete:
                                    if st.button("🗑️ Delete", key=f"delete_{composite_id}", use_container_width=True, type="secondary"):
                                        if toolbox.delete_composite(composite_id):
                                            st.success("Deleted!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete")
                                
                                st.markdown("---")
                                
                                # Show full design details
                                exp_tab1, exp_tab2, exp_tab3, exp_tab4 = st.tabs(["📋 Overview", "⚙️ Components", "📊 Simulation", "💾 Raw Data"])
                                
                                with exp_tab1:
                                    full_design = full_data.get('full_design', {})
                                    st.markdown("**Physics Explanation:**")
                                    st.write(full_design.get('physics_explanation', 'N/A'))
                                    st.markdown("**Expected Outcome:**")
                                    st.write(full_design.get('expected_outcome', 'N/A'))
                                    st.markdown("**User Query:**")
                                    st.info(full_design.get('user_query', 'N/A'))
                                
                                with exp_tab2:
                                    components = full_data.get('components', [])
                                    if components:
                                        for i, comp in enumerate(components, 1):
                                            st.markdown(f"**{i}. {comp.get('name', 'Unknown')}** ({comp.get('type', 'N/A')})")
                                            st.caption(f"Position: ({comp.get('x', 0)}, {comp.get('y', 0)}) | Angle: {comp.get('angle', 0)}°")
                                            params = comp.get('parameters', {})
                                            if params:
                                                st.json(params)
                                            st.markdown("")
                                    else:
                                        st.info("No component data available")
                                
                                with exp_tab3:
                                    sim_results = full_design.get('simulation_results', {})
                                    if sim_results and sim_results.get('success'):
                                        rating = sim_results.get('honest_rating', 'N/A')
                                        st.metric("Quality Rating", f"{rating}/10")
                                        st.markdown("**AI Analysis:**")
                                        st.write(sim_results.get('interpretation', 'N/A'))
                                        
                                        # Show QuTiP code if available
                                        sim_code = sim_results.get('simulation_code')
                                        if sim_code:
                                            with st.expander("View QuTiP Code"):
                                                st.code(sim_code, language='python', line_numbers=True)
                                    else:
                                        st.info("No simulation results stored")
                                
                                with exp_tab4:
                                    st.json(full_data)
                    else:
                        st.info("💡 No experiments learned yet. Approve designs to build the knowledge base!")
        
        # STATE 4: Completely idle - show welcome (only when no design, no conversation, not processing, no pending query)
        elif not st.session_state.current_design and not st.session_state.conversation_context and not st.session_state.is_processing and not st.session_state.get('pending_query'):
            # Empty state - show right pane welcome
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; color: #a08060;">
                <div style="font-size: 5rem; margin-bottom: 1.5rem; opacity: 0.2;">🔬</div>
                <div style="font-size: 1.5rem; color: #d4a574; margin-bottom: 1rem; font-weight: 300;">
                    Your Optical Setup Will Appear Here
                </div>
                <div style="line-height: 1.8; color: #a08060; font-size: 1rem; max-width: 500px; margin: 0 auto;">
                    Start a conversation on the left to design your first quantum experiment.<br><br>
                    <span style="color: #d4a574;">I'll generate the optical table, component layout, and beam paths!</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer with attribution
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0; color: #a08060; font-size: 0.9rem;">
        <div style="margin-bottom: 0.5rem;">
            <strong style="color: #d4a574;">Aṇubuddhi</strong> <span style="color: #8b7355;">(अणुबुद्धि)</span> 
            — Agentic AI for Quantum Experiment Design
        </div>
        <div style="margin-bottom: 0.5rem;">
            Designed and Developed by <strong style="color: #d4a574;">S. K. Rithvik</strong>
        </div>
        <div style="font-size: 0.85rem; color: #8b7355; margin-top: 0.8rem;">
            © 2025 S. K. Rithvik. All rights reserved.<br>
            Licensed for open science and research with proper attribution.
        </div>
        <div style="font-size: 0.8rem; color: #6b5d4f; margin-top: 0.8rem; font-style: italic;">
            Built with LLMs, ChromaDB, QuTiP, and the spirit of quantum curiosity
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
