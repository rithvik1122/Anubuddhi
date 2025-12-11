"""
Simplified Full-Width Split-Screen Chat Interface for Quantum Experiment Design
Left 50%: Simple chat interface
Right 50%: Optical table + all details
"""

import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import time

# Must be first streamlit command
st.set_page_config(
    page_title="Aṇubuddhi - Quantum Designer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import our modules
from src.agentic_quantum.designer.llm_designer import LLMBasedDesigner
from src.agentic_quantum.renderer.optical_table_renderer import create_optical_table_figure

# SIMPLE CSS - Full width, clean chat
st.markdown("""
<style>
    /* Remove ALL padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Minimal header */
    .header {
        background: #1a1a1a;
        color: #d4a574;
        padding: 0.5rem 1rem;
        font-size: 1.2rem;
        border-bottom: 1px solid #333;
    }
    
    /* Chat container - full height */
    .chat-box {
        height: 80vh;
        overflow-y: auto;
        padding: 1rem;
        background: #0a0a0a;
    }
    
    /* Simple bubbles */
    .msg-user {
        background: #1e3a5f;
        color: #fff;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        margin-left: 5%;
    }
    
    .msg-ai {
        background: #2a2a2a;
        color: #ddd;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        margin-right: 5%;
    }
    
    /* Right pane */
    .right-pane {
        background: #0f0f0f;
        height: 100vh;
        padding: 1rem;
        border-left: 1px solid #333;
        overflow-y: auto;
    }
    
    /* Hide streamlit stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'current_design' not in st.session_state:
    st.session_state.current_design = None
if 'designer' not in st.session_state:
    st.session_state.designer = LLMBasedDesigner()

def design_experiment(query, previous_design=None):
    """Simple wrapper for design"""
    try:
        result = st.session_state.designer.design_experiment(
            user_query=query,
            previous_design=previous_design,
            conversation_history=st.session_state.conversation
        )
        return result
    except Exception as e:
        return {'error': str(e)}

def main():
    # Header
    st.markdown('<div class="header">Aṇubuddhi - Quantum Experiment Designer</div>', unsafe_allow_html=True)
    
    # SPLIT 50-50
    col_chat, col_design = st.columns([1, 1])
    
    # ===== LEFT: CHAT =====
    with col_chat:
        st.markdown("### 💬 Chat")
        
        # Display chat
        chat_html = '<div class="chat-box">'
        if st.session_state.conversation:
            for msg in st.session_state.conversation:
                if msg['role'] == 'user':
                    chat_html += f'<div class="msg-user">👤 You: {msg["content"]}</div>'
                else:
                    chat_html += f'<div class="msg-ai">🤖 AI: {msg["content"]}</div>'
        else:
            chat_html += '<div style="color:#666;padding:2rem;text-align:center;">Start by describing your experiment...</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Input
        with st.form("chat_form"):
            user_msg = st.text_input(
                "Message",
                placeholder="Design a Bell state generator...",
                label_visibility="collapsed"
            )
            col1, col2 = st.columns([3, 1])
            with col1:
                send = st.form_submit_button("Send", use_container_width=True)
            with col2:
                clear = st.form_submit_button("New", use_container_width=True)
        
        # Handle clear
        if clear:
            st.session_state.conversation = []
            st.session_state.current_design = None
            st.rerun()
        
        # Handle send
        if send and user_msg:
            # Add user message
            st.session_state.conversation.append({
                'role': 'user',
                'content': user_msg
            })
            
            # Show progress
            with st.spinner("Designing..."):
                result = design_experiment(
                    user_msg,
                    previous_design=st.session_state.current_design
                )
            
            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                # Add AI response
                st.session_state.conversation.append({
                    'role': 'assistant',
                    'content': f"Created: {result.get('title', 'Experiment')}"
                })
                st.session_state.current_design = result
                st.rerun()
    
    # ===== RIGHT: DESIGN + DETAILS =====
    with col_design:
        if st.session_state.current_design:
            result = st.session_state.current_design
            experiment = result.get('experiment', {})
            
            st.markdown(f"### 🔬 {result.get('title', 'Design')}")
            
            # Optical table - BIGGER
            try:
                fig = create_optical_table_figure(experiment, figsize=(14, 10))
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            except Exception as e:
                st.error(f"Render error: {e}")
            
            st.markdown("---")
            
            # Details tabs
            tab1, tab2, tab3 = st.tabs(["📋 Overview", "⚙️ Components", "🔧 Raw Data"])
            
            with tab1:
                st.write("**Description:**")
                st.write(result.get('description', 'N/A'))
                st.write("**Physics:**")
                st.write(result.get('physics_explanation', 'N/A'))
            
            with tab2:
                comps = result.get('component_justifications', {})
                if comps:
                    for i, (name, reason) in enumerate(comps.items(), 1):
                        st.write(f"**{i}. {name}**")
                        st.write(reason)
                        st.write("")
                else:
                    st.info("No component details")
            
            with tab3:
                st.json(result.get('parsed_design', {}))
        
        else:
            st.markdown("### 🔬 Design")
            st.info("Your design will appear here")
            st.write("**Try:**")
            st.write("• Bell state generator")
            st.write("• HOM interferometer")
            st.write("• Quantum teleportation")

if __name__ == "__main__":
    main()
