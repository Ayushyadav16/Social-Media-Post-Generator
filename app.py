import streamlit as st
import os
import time
from dotenv import load_dotenv

# Import utilities and agent config
from agent import YoutubeAgent, MODEL_NAME
from utils import validate_url

# Load environment variables
load_dotenv()

# Streamlit Page Setup
st.set_page_config(
    page_title="Advanced Agentic AI Content Generator",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling for modern look
st.markdown("""
<style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #6C5CE7;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Advanced Agentic AI Content Generator")
st.markdown(
    "Demonstrating advanced **Agentic AI** behaviors: "
    "**Planning**, **Tool Orchestration**, **Self-Reflection (Scoring)**, and **Iterative Self-Improvement**."
)

# Initialize Session State Variables
if "generated" not in st.session_state:
    st.session_state.generated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Config
with st.sidebar:
    st.header("🔑 Credentials")
    env_key = os.getenv("GOOGLE_API_KEY", "")
    placeholder = "Key loaded from environment (.env)" if env_key else "Enter Google Gemini API Key"
    user_key = st.text_input("Gemini API Key", type="password", placeholder=placeholder)
    api_key = user_key if user_key else env_key
    
    st.markdown("---")
    st.header("🧠 Session Memory")
    
    if st.session_state.history:
        st.write("Reload past generations to compare:")
        
        # Display list of past items in a select box
        selected_history = st.selectbox(
            "Select past run",
            options=st.session_state.history,
            format_func=lambda x: f"{x['title'][:25]}... ({x['audience']} - {x['tone']})"
        )
        
        if st.button("Reload Selected Run 🔄"):
            st.session_state.results = selected_history["results"]
            st.session_state.generated = True
            st.success("Past run loaded from session memory!")
    else:
        st.info("No past runs in memory yet. Execute a generation to store it.")

# Main Panel layout split into Inputs & Live Logs
col_inputs, col_logs = st.columns([1.2, 1])

with col_inputs:
    st.subheader("🎥 Step 1: Configuration")
    url_input = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    col_selectors_1, col_selectors_2 = st.columns(2)
    with col_selectors_1:
        audience_input = st.selectbox(
            "Target Audience",
            options=["Developers", "Students", "Recruiters", "Startup Founders", "Marketing Professionals", "Beginners"]
        )
    with col_selectors_2:
        tone_input = st.selectbox(
            "Target Tone",
            options=["Professional", "Friendly", "Humorous", "Storytelling", "Motivational", "Technical"]
        )
        
    run_btn = st.button("Run AI Agent ⚡", type="primary", use_container_width=True)

with col_logs:
    st.subheader("🤖 Live Agent Trace")
    log_area = st.container()

# Execution Event loop
if run_btn:
    if not url_input:
        st.error("Please enter a YouTube video URL.")
    elif not api_key:
        st.warning("Please provide your Google API key in the sidebar or via the `.env` file.")
    elif not validate_url(url_input):
        st.error("Invalid YouTube URL. Please enter a valid YouTube video link.")
    else:
        st.session_state.generated = False
        st.session_state.results = {}
        
        # Initialize Agent
        agent = YoutubeAgent(api_key=api_key)
        
        with log_area:
            with st.status("Agent starting...", expanded=True) as status_box:
                try:
                    # Iterate through the generator
                    for step in agent.run(url_input, audience_input, tone_input):
                        if step["status"] == "info":
                            st.markdown(f"💭 **Thought:** *{step['log']}*")
                        elif step["status"] == "success":
                            st.markdown(f"🔹 **Action ({step['step']}):** {step['log']}")
                        elif step["status"] == "done":
                            st.session_state.results = step["results"]
                            st.session_state.generated = True
                            
                            # Append to Session Memory (History)
                            history_item = {
                                "title": step["results"]["metadata"]["title"],
                                "url": url_input,
                                "audience": audience_input,
                                "tone": tone_input,
                                "results": step["results"]
                            }
                            st.session_state.history.append(history_item)
                            
                            status_box.update(label="Agent execution complete!", state="complete", expanded=False)
                            st.toast("Generation Complete!", icon="🎉")
                except Exception as e:
                    status_box.update(label="Agent execution failed!", state="error")
                    st.error(f"An error occurred: {str(e)}")
                    st.exception(e)

# Render results
if st.session_state.generated and st.session_state.results:
    st.markdown("---")
    
    res = st.session_state.results
    meta = res["metadata"]
    metrics = res["metrics"]
    eval_scores = res["evaluation"]
    
    st.subheader(f"📊 Agent Dashboard: {meta['title']}")
    
    # Render Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["execution_time"]}</div><div class="metric-label">Execution Time</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["transcript_length"]}</div><div class="metric-label">Transcript Length</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["words_generated"]}</div><div class="metric-label">Words Generated</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["model_used"]}</div><div class="metric-label">Model Used</div></div>', unsafe_allow_html=True)
    with c5:
        # Calculate Average Score
        avg_score = round(sum([eval_scores[k]["score"] for k in ["linkedin", "twitter", "instagram"]]) / 3, 1)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score}/100</div><div class="metric-label">Avg Quality Score</div></div>', unsafe_allow_html=True)

    # Completed Steps List
    st.caption(f"**Orchestrated Steps:** {' ➡️ '.join(metrics['steps_completed'])}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Split layout for Outputs & Interview Mode
    col_output, col_interview = st.columns([1.3, 1])
    
    with col_output:
        st.subheader("📱 Generated Platform Outputs")
        
        # LinkedIn
        with st.expander("💼 LinkedIn Post", expanded=True):
            st.code(res["linkedin"], language="text")
            st.markdown(f"**💡 Suitability Explanation:** *{eval_scores['linkedin']['why_it_fits']}*")
            
        # Twitter
        with st.expander("🐦 Twitter/X Thread"):
            st.code(res["twitter"], language="text")
            st.markdown(f"**💡 Suitability Explanation:** *{eval_scores['twitter']['why_it_fits']}*")
            
        # Instagram
        with st.expander("📸 Instagram Caption"):
            st.code(res["instagram"], language="text")
            st.markdown(f"**💡 Suitability Explanation:** *{eval_scores['instagram']['why_it_fits']}*")
            
        # Transcript Preview
        with st.expander("📝 Raw Transcript Preview"):
            st.text_area("Cleaned Subtitles", value=res["transcript"], height=200, disabled=True)

    with col_interview:
        st.subheader("💡 Interview Demonstration Mode")
        st.write("Use this pane during interviews to show the agent's internal reasoning, scores, and self-improvement loops.")
        
        show_workflow = st.toggle("Show Agent Workflow", value=True)
        
        if show_workflow:
            # 1. Goal & Plan
            st.markdown("#### 1. Agent Goal & Plan")
            st.info(f"**Goal:** Adapt YouTube video for **{audience_input}** with a **{tone_input}** tone.")
            st.markdown(f"**Plan Generated by PlanningTool:**\n*{metrics['plan']}*")
            
            # 2. Evaluation Review
            st.markdown("#### 2. Reflection Agent critiques & Scores")
            for platform, key in [("LinkedIn", "linkedin"), ("Twitter Thread", "twitter"), ("Instagram Caption", "instagram")]:
                score = eval_scores[key]["score"]
                color = "green" if score >= 90 else ("orange" if score >= 80 else "red")
                
                st.markdown(f"**{platform} Post Quality:** :{color}[**{score}/100**]")
                st.markdown(f"- **Hook Critique:** {eval_scores[key]['hook_critique']}")
                st.markdown(f"- **CTA Critique:** {eval_scores[key]['cta_critique']}")
                st.markdown(f"- **Hashtags Critique:** {eval_scores[key]['hashtags_critique']}")
                st.write("---")
                
            # 3. Self-Improvement Diffs (if any)
            if res["improvements"]:
                st.markdown("#### 🔄 3. Self-Improvement Diffs (Before & After)")
                st.write("These posts scored under 85. The agent ran a feedback loop to improve them autonomously:")
                
                for platform, diff in res["improvements"].items():
                    with st.expander(f"Improvement Diff: {platform.capitalize()}", expanded=True):
                        st.markdown("**Critique suggestions addressed:**")
                        st.write(diff["critique"])
                        
                        col_before, col_after = st.columns(2)
                        with col_before:
                            st.error("**Original Draft (Score < 85)**")
                            st.write(diff["original"])
                        with col_after:
                            st.success("**Improved Final Copy**")
                            st.write(diff["improved"])
            else:
                st.markdown("#### 🔄 3. Self-Improvement Loop")
                st.success("✅ All drafts scored above the 85/100 threshold on the first pass, so no self-improvement rewrites were needed!")
                
            # 4. Final Strategic Report
            st.markdown("#### 4. AI Strategic Reflection Report")
            st.markdown(res["report"])
