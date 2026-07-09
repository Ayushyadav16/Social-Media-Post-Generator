import streamlit as st
import os
from dotenv import load_dotenv

# Import our agent and utilities
from agent import YoutubeAgent, MODEL_NAME
from utils import validate_url

# Load environment variables from .env
load_dotenv()

# Streamlit Page Setup
st.set_page_config(
    page_title="Agentic YouTube Content Repurposer",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Agentic AI Content Repurposer")
st.markdown(
    f"This minimalist project demonstrates **Agentic AI** concepts (Planning, Tool Use, and Reflection) "
    f"by reading a YouTube video transcript and generating optimized social posts. "
    f"Uses model: `{MODEL_NAME}`"
)

# Initialize Session States
if "generated" not in st.session_state:
    st.session_state.generated = False
if "results" not in st.session_state:
    st.session_state.results = {}

# Sidebar for Google API Key
with st.sidebar:
    st.header("🔑 Credentials")
    env_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Pre-fill placeholder if loaded from .env
    placeholder = "Key loaded from environment (.env)" if env_key else "Enter Google Gemini API Key"
    user_key = st.text_input("Gemini API Key", type="password", placeholder=placeholder)
    
    # Prioritize user input over env variable
    api_key = user_key if user_key else env_key
    
    st.markdown("---")
    st.markdown(
        "💡 **Interview Tip:** When demonstrating this, emphasize how the `YoutubeAgent` "
        "class operates autonomously using planning and reasoning rather than running static pipelines."
    )

# Input Section
st.subheader("🎥 Step 1: Input Video Details")
url_input = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Generate Action
if st.button("Run AI Agent ⚡", type="primary", use_container_width=True):
    if not url_input:
        st.error("Please enter a YouTube video URL.")
    elif not api_key:
        st.warning("Please provide your Google API key (either in the sidebar or via the `.env` file).")
    elif not validate_url(url_input):
        st.error("Invalid YouTube URL. Please enter a valid watch, shorts, or sharing link.")
    else:
        # Reset generation state
        st.session_state.generated = False
        st.session_state.results = {}
        
        # Instantiate our agent
        agent = YoutubeAgent(api_key=api_key)
        
        # Real-time visual display of the agentic loop
        st.subheader("🧠 2. Agent Reasoning & Execution Trace")
        
        with st.status("Agent starting...", expanded=True) as status_box:
            try:
                # Iterate through the agent's generator yielding steps
                for step in agent.run(url_input):
                    if step["status"] == "info":
                        st.markdown(f"**Thought:** *{step['log']}*")
                    elif step["status"] == "success":
                        st.markdown(f"🔹 **Action:** {step['log']}")
                    elif step["status"] == "done":
                        st.session_state.results = step["results"]
                        st.session_state.generated = True
                        status_box.update(label="Agent execution complete!", state="complete", expanded=False)
                        st.success("🎉 Marketing assets generated successfully!")
            except Exception as e:
                status_box.update(label="Agent execution failed!", state="error")
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)  # Show the full traceback directly on the screen for debugging

# Output rendering (Displays if results exist in Session State)
if st.session_state.generated and st.session_state.results:
    st.markdown("---")
    st.subheader("📁 Step 3: Generated Marketing Assets")
    
    res = st.session_state.results
    meta = res["metadata"]
    
    st.markdown(f"**Processing results for:** *{meta['title']}*")
    
    # 1. Summary Output
    with st.expander("📘 Short Summary", expanded=True):
        st.write(res["summary"])
        
    # 2. LinkedIn Post Output
    with st.expander("💼 LinkedIn Post"):
        st.caption("Click the copy button in the top-right of the code box.")
        st.code(res["linkedin"], language="text")
        
    # 3. Twitter/X Thread Output
    with st.expander("🐦 Twitter/X Thread"):
        st.caption("Click the copy button in the top-right of the code box.")
        st.code(res["twitter"], language="text")
        
    # 4. Instagram Caption Output
    with st.expander("📸 Instagram Caption"):
        st.caption("Click the copy button in the top-right of the code box.")
        st.code(res["instagram"], language="text")
        
    # 5. Raw Transcript Preview
    with st.expander("📝 Transcript Preview"):
        st.text_area("Cleaned Transcript Text", value=res["transcript"], height=250, disabled=True)
