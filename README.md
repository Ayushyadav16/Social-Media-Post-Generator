# 🤖 Upgraded Agentic AI YouTube Content Repurposer

An AI agent project that autonomously repurposes YouTube transcripts into optimized, high-impact social media posts. This project is specifically engineered for software engineering and AI developer interviews to showcase advanced **Agentic AI** behaviors (planning, tool calling, self-reflection, and self-improvement loops) while remaining simple and readable.

---

## 🌟 Advanced Agentic Features

- **Agent Planning**: The agent analyzes video metadata, the selected **Audience**, and the target **Tone** to generate an autonomous execution plan.
- **Tool Orchestration**: Orchestrates modular tools (`PlanningTool`, `TranscriptTool`, `AnalysisTool`, `ContentGeneratorTool`, `ReviewerTool`, `ImprovementTool`, and `ReportTool`).
- **Reflection & Evaluation**: Evaluates drafts against target metrics and assigns scores (0-100) for LinkedIn, Twitter, and Instagram. Explains exactly *why* the hook, CTA, and hashtags fit the target audience.
- **Autonomous Self-Improvement**: If any post scores below **85/100**, the agent intercepts the output, processes the critiques, and runs a rewrite loop to self-correct. Diffs are shown in the UI.
- **Session Memory**: Remembers past generations in the current session, letting users reload and compare outputs with different audience/tone configurations.
- **Live Agent Dashboard**: Displays execution metrics in real-time, including elapsed time, word counts, model used, and a checklist of completed steps.
- **Interview Mode**: A dedicated "Show Agent Workflow" toggle reveals the agent's internal plans, decision metrics, raw critiques, and self-improvement diffs.

---

## 🛠️ File Structure

The project maintains a minimalist design under 6 code/configuration files:
```
project/
├── app.py              # Streamlit User Interface with Dashboard & Interview Mode
├── agent.py            # The YoutubeAgent orchestrating tools & self-improvement loops
├── prompts.py          # Prompt templates for planning, generation, and evaluations
├── utils.py            # Utilities (URL validation, transcript fetcher with retry logic)
├── requirements.txt    # Minimal pinned dependencies
├── .env.example        # Environment variable template
└── INTERVIEW_NOTES.md  # Detailed interview cheat sheet and Q&A study guide
```

---

## 🚀 Quick Start

### 1. Install Dependencies
Ensure you have Python 3.11+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Set Up Credentials
Create a `.env` file in the project folder:
```bash
copy .env.example .env
```
Open `.env` and fill in your Gemini API Key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
*Note: You can generate a free key from [Google AI Studio](https://aistudio.google.com/). If not saved in `.env`, you can paste it directly into the Streamlit sidebar.*

### 3. Run the App
Launch the Streamlit interface:
```bash
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.
Select an **Audience** and **Tone**, paste a YouTube URL, and click **Run AI Agent ⚡** to watch the reasoning loop execute live!
