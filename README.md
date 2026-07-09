# 🎬 AI YouTube Transcript to Social Content Repurposer (Agentic AI)

A minimalist, interview-focused AI agent project that autonomously converts YouTube video transcripts into platform-specific social media posts. This project is engineered specifically for software engineering and AI developer interviews to showcase **Agentic AI** concepts (planning, tool use, and reflection) without production-level architectural bloat.

---

## 🧠 What is Agentic AI?

Traditional AI applications run on static, deterministic pipelines. In contrast, **Agentic AI** operates via a reasoning loop:
1. **Planning (Thought)**: The agent receives the task (a video title) and outlines a plan of how it will approach the translation.
2. **Tool Execution (Action)**: The agent programmatically calls an external tool (the transcript downloader) to gather data.
3. **Reflection (Reasoning)**: The agent digests the raw transcript and extracts core insights, themes, and quotes before drafting posts.
4. **Generation (Execution)**: The agent outputs tailored copy for LinkedIn, Twitter/X, and Instagram.

---

## 🛠️ File Structure

The project contains only 6 key files for maximum readability:
```
project/
├── app.py              # Streamlit User Interface
├── agent.py            # The core YoutubeAgent class (Planning, Tool, Reflection loop)
├── prompts.py          # Plain text prompt templates
├── utils.py            # Utilities (URL validation, transcript & oEmbed fetchers)
├── requirements.txt    # Minimal dependencies
├── .env.example        # Environment template (API keys)
└── INTERVIEW_NOTES.md  # Detailed interview study guide / Q&A cheat sheet
```

---

## 🚀 Quick Start

### 1. Install Dependencies
Make sure you have Python 3.11+ installed. Run the following command:
```bash
pip install -r requirements.txt
```

### 2. Set Up Credentials
Create a `.env` file in the root folder:
```bash
copy .env.example .env
```
Open `.env` and fill in your Gemini API Key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
*Note: You can get a free API key from [Google AI Studio](https://aistudio.google.com/). If you don't use a `.env` file, you can also paste the key directly into the Streamlit sidebar during runtime.*

### 3. Run the App
Launch the Streamlit interface:
```bash
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 💡 Key Architectural Details (For Interviews)
- **Centralized Model Configuration**: The model name is set in one place: `MODEL_NAME = "gemini-2.0-flash"` in `agent.py`.
- **Version-Agnostic Utilities**: `utils.py` uses checks (`isinstance` and `getattr`) to support both old dictionary outputs and new `@dataclass` structures from `youtube-transcript-api`.
- **Stable Endpoint Mapping**: Connects to Google's stable `v1` endpoint and converts system messages under the hood to bypass `systemInstruction` validation errors.
- **Thought Streaming**: The agent uses Python generators (`yield`) so the UI can print reasoning steps in real-time.
