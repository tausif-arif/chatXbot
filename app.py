import os
import time
import streamlit as st
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
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

# Enhanced Custom CSS for JARVIS UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Electrolize&family=Orbitron:wght@500&display=swap');
    
    :root {
        --jarvis-gold: #FFD700;
        --jarvis-blue: #00f7ff;
        --hud-background: rgba(10, 10, 46, 0.95);
    }
    
    .main {
        background: linear-gradient(160deg, #0a0a2e 40%, #001144 100%);
        color: var(--jarvis-gold);
        position: relative;
        overflow: hidden;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            repeating-linear-gradient(
                90deg,
                rgba(255, 215, 0, 0.03) 0px,
                transparent 2px,
                transparent 150px
            ),
            repeating-linear-gradient(
                180deg,
                rgba(255, 215, 0, 0.03) 0px,
                transparent 2px,
                transparent 150px
            );
        pointer-events: none;
    }
    
    .stChatInput input {
        background: rgba(0, 0, 34, 0.8) !important;
        color: var(--jarvis-gold) !important;
        border: 1px solid var(--jarvis-gold) !important;
        font-family: 'Orbitron', sans-serif;
        backdrop-filter: blur(5px);
    }
    
    .jarvis-header-container {
        position: relative;
        width: 100%;
        height: 120px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .jarvis-logo {
        position: relative;
        width: 80px;
        height: 80px;
        border: 2px solid var(--jarvis-gold);
        border-radius: 50%;
        animation: logoSpin 10s linear infinite;
        margin-right: 20px;
    }
    
    .jarvis-logo::before,
    .jarvis-logo::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        border: 2px solid var(--jarvis-gold);
        border-radius: 50%;
        animation: pulseRing 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
    }
    
    .jarvis-logo::before {
        width: 90%;
        height: 90%;
    }
    
    .jarvis-logo::after {
        width: 75%;
        height: 75%;
        animation-delay: 0.5s;
    }
    
    .jarvis-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8em;
        text-align: center;
        color: var(--jarvis-gold);
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.7);
        animation: textGlow 2s infinite;
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
        letter-spacing: 2px;
    }
    
    .assistant-message {
        position: relative;
        background: rgba(0, 8, 34, 0.9);
        border-left: 3px solid var(--jarvis-gold);
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        backdrop-filter: blur(5px);
    }
    
    .assistant-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 215, 0, 0.1),
            transparent
        );
        animation: shimmer 2s infinite;
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
        background: var(--jarvis-gold);
        border-radius: 50%;
        animation: typing 1.4s infinite;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    /* Enhanced Animations */
    @keyframes logoSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes pulseRing {
        0% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.8; }
        50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.4; }
        100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.8; }
    }
    
    @keyframes textGlow {
        0% { text-shadow: 0 0 10px rgba(255, 215, 0, 0.7); }
        50% { text-shadow: 0 0 20px rgba(255, 215, 0, 0.9); }
        100% { text-shadow: 0 0 10px rgba(255, 215, 0, 0.7); }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes typing {
        0%, 100% { transform: translateY(0); opacity: 0.5; }
        50% { transform: translateY(-5px); opacity: 1; }
    }
    
    /* Sidebar Styling */
    .stSidebar {
        background: rgba(0, 0, 34, 0.95);
        border-right: 1px solid var(--jarvis-gold);
    }
    
    .stSidebar [data-testid="stMetricValue"] {
        color: var(--jarvis-gold) !important;
    }
    
    .stSidebar [data-testid="stMetricDelta"] {
        color: var(--jarvis-blue) !important;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 34, 0.95);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--jarvis-gold);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ffd900;
    }
</style>

<!-- Enhanced JARVIS Header with Logo -->
<div class="jarvis-header-container">
    <div class="jarvis-logo"></div>
    <div class="jarvis-header">J.A.R.V.I.S.</div>
</div>
""", unsafe_allow_html=True)

# Dummy avatar URLs
USER_AVATAR = "https://avatar.iran.liara.run/public/job/astronomer/male"
ASSISTANT_AVATAR = "https://upload.wikimedia.org/wikipedia/en/e/e0/J.A.R.V.I.S._%28MCU%29.png"

# Initialize session state
def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "model" not in st.session_state:
        st.session_state.model = "mixtral-8x7b-32768"
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

# Typing animation
def typing_animation():
    return """
    <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot" style="animation-delay: 0.2s"></span>
        <span class="typing-dot" style="animation-delay: 0.4s"></span>
    </div>
    """

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

# Create conversation chain with custom prompt
def create_conversation_chain(groq_chat):
    # Custom prompt template for JARVIS personality
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="""You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), a sophisticated AI assistant created by Tausif(Software engineer). 
        You should respond in a concise, helpful manner with a touch of wit, similar to the MCU's JARVIS.
        Keep responses brief but informative, and maintain a slightly formal but warm tone.
        Never introduce yourself unless asked - just respond naturally to queries.
        
        Previous conversation:
        {history}
        
        User: {input}
        Assistant:"""
    )
    
    memory = ConversationBufferMemory(ai_prefix="Assistant")
    
    conversation = ConversationChain(
        llm=groq_chat,
        prompt=prompt,
        memory=memory,
        verbose=False
    )
    
    return conversation

# Main application
def main():
    # st.markdown('<div class="jarvis-header">J.A.R.V.I.S.</div>', unsafe_allow_html=True)
    initialize_session_state()
    sidebar()
    
    groq_chat = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=st.session_state.model
    )
    
    # Create or get conversation chain
    if st.session_state.conversation is None:
        st.session_state.conversation = create_conversation_chain(groq_chat)
    
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

        # Create a message container for the assistant
        assistant_message = st.chat_message("assistant", avatar=ASSISTANT_AVATAR)
        
        # Show typing animation in the container
        typing_container = assistant_message.empty()
        typing_container.markdown(typing_animation(), unsafe_allow_html=True)
        
        # Get response
        start_time = time.time()
        response = st.session_state.conversation.predict(input=user_input)
        processing_time = time.time() - start_time
        
        # Update the container with the response
        typing_container.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
        assistant_message.caption(f"Response generated in {processing_time:.2f}s")

        st.session_state.history.append({"role": "assistant", "content": response})
        st.session_state.processing = False

if __name__ == "__main__":
    load_dotenv()
    main()