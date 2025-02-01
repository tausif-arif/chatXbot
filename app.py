import os
import time
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Set page config FIRST
st.set_page_config(
    page_title="J.A.R.V.I.S. MK XLIX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for JARVIS UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Electrolize&family=Orbitron:wght@500&display=swap');
    
    :root {
        --jarvis-blue: #00f7ff;
        --hud-background: rgba(10, 10, 46, 0.95);
    }
    
    .main {
        background: linear-gradient(160deg, #0a0a2e 40%, #001144 100%);
        color: var(--jarvis-blue);
    }
    
    .stChatInput input {
        background: rgba(0, 0, 34, 0.8) !important;
        color: var(--jarvis-blue) !important;
        border: 1px solid var(--jarvis-blue) !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    .jarvis-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8em;
        text-align: center;
        text-shadow: 0 0 15px var(--jarvis-blue);
        animation: pulse 2s infinite;
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .jarvis-header::after {
        content: "MARK XLIX";
        position: absolute;
        bottom: -20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.4em;
        opacity: 0.8;
    }
    
    @keyframes scanline {
        0% { background-position: 0 0; }
        100% { background-position: 0 100vh; }
    }
    
    .hud-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: linear-gradient(rgba(0, 247, 255, 0.1) 1px, transparent 1px);
        background-size: 100% 2px;
        animation: scanline 15s linear infinite;
        z-index: 999;
    }
    
    .assistant-message {
        position: relative;
        background: rgba(0, 8, 34, 0.9);
        border-left: 3px solid var(--jarvis-blue);
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 247, 255, 0.2);
    }
    
    .typing-indicator {
        display: inline-block;
        padding: 10px;
        font-family: 'Orbitron', sans-serif;
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin-right: 3px;
        background: var(--jarvis-blue);
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    @keyframes typing {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
</style>
<div class="hud-overlay"></div>
""", unsafe_allow_html=True)

# Dummy avatar URLs
USER_AVATAR = "https://avatar.iran.liara.run/public/job/astronomer/male"  # Blue User Avatar
ASSISTANT_AVATAR = "https://upload.wikimedia.org/wikipedia/en/e/e0/J.A.R.V.I.S._%28MCU%29.png"  # Red J.A.R.V.I.S. Avatar

# Initialize session state
def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "model" not in st.session_state:
        st.session_state.model = "mixtral-8x7b-32768"
    if "processing" not in st.session_state:
        st.session_state.processing = False

# Typing animation
def typing_animation():
    return st.markdown("""
    <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot" style="animation-delay: 0.2s"></span>
        <span class="typing-dot" style="animation-delay: 0.4s"></span>
    </div>
    """, unsafe_allow_html=True)

# Sidebar configuration
def sidebar():
    with st.sidebar:
        st.title("▲ TACTICAL HUD")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Power Core", "400%", "+2.4%")
            st.metric("Neural Load", "34%", "3ms latency")
            
        with col2:
            st.metric("Nanite Integrity", "98%", "-2%")
            st.metric("Shield Capacity", "100%", "Nominal")
        
        st.markdown("---")
        st.markdown("**THREAT ANALYSIS**")
        st.code("No hostiles detected\nAirspace clear\nGround stability: 98%", language="text")
        
        st.session_state.model = st.selectbox(
            "NEURAL ARCHITECTURE",
            ["llama-3.3-70b-versatile","mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it","deepseek-r1-distill-llama-70b"],
            index=0
        )

# Main application
def main():
    st.markdown('<div class="jarvis-header">J.A.R.V.I.S.</div>', unsafe_allow_html=True)
    initialize_session_state()
    sidebar()
    
    groq_chat = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=st.session_state.model
    )
    
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=groq_chat, memory=memory)
    
    # Display chat history
    for message in st.session_state.history:
        role = message["role"]
        content = message["content"]
        
        avatar_url = USER_AVATAR if role == "user" else ASSISTANT_AVATAR
        
        with st.chat_message(role, avatar=avatar_url):
            st.markdown(f"<div class='assistant-message'>{content}</div>", unsafe_allow_html=True)

    # User input
    user_input = st.chat_input("Awaiting your command, Sir...")
    if user_input and not st.session_state.processing:
        st.session_state.processing = True

        # Add user message
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(user_input)

        # Show typing animation
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            typing = st.empty()
            typing.markdown(typing_animation(), unsafe_allow_html=True)
            
            # Simulate processing delay
            start_time = time.time()
            response = conversation.predict(input=user_input)
            processing_time = time.time() - start_time
            
            # Clear typing indicator
            typing.empty()
            
            # Display response
            st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
            st.caption(f"Response generated in {processing_time:.2f}s")

        st.session_state.history.append({"role": "assistant", "content": response})
        st.session_state.processing = False

if __name__ == "__main__":
    load_dotenv()
    main()