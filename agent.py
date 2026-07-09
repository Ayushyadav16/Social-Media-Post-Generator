import time
import json
import re
from typing import Dict, Any, Generator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import prompts
import utils

# Centralized model configuration
MODEL_NAME = "gemini-2.5-flash"

class YoutubeAgent:
    """
    An advanced, interview-worthy AI Agent orchestrating planning, tool usage,
    evaluation reflection, self-improvement, and execution metrics.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize LangChain Gemini wrapper on stable v1 API with system message conversions
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=0.7,
            api_version="v1",
            convert_system_message_to_human=True
        )

    def _invoke_llm(self, prompt: str) -> str:
        """
        Invokes the LLM and runs self-diagnostics if a 404/NOT_FOUND is thrown.
        """
        try:
            return self.llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            err_str = str(e)
            if "NOT_FOUND" in err_str or "404" in err_str:
                try:
                    from google import genai
                    client = genai.Client(api_key=self.api_key)
                    models_response = client.models.list()
                    available_models = [m.name.replace("models/", "") for m in models_response]
                    raise ValueError(
                        f"Gemini model '{MODEL_NAME}' was not found or is not supported.\n\n"
                        f"👉 **Available models for your API key:** {available_models}\n\n"
                        f"Please edit `MODEL_NAME` in `agent.py` (Line 10) to match one of these."
                    ) from e
                except Exception as list_err:
                    if isinstance(list_err, ValueError):
                        raise list_err
                    raise ValueError(
                        f"Model '{MODEL_NAME}' returned 404 NOT_FOUND. "
                        f"Could not retrieve authorized models: {str(list_err)}"
                    ) from e
            raise e

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """
        Helper to cleanly extract and load JSON from LLM markdown code blocks.
        """
        text = text.strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                text = match.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON substring: {str(e)}")
        raise ValueError("No JSON object found in response.")

    # =====================================================================
    # TOOL INSTRUMENTS
    # =====================================================================

    def planning_tool(self, title: str, creator: str, audience: str, tone: str) -> str:
        """TOOL: Generates the step-by-step agentic execution plan."""
        prompt = prompts.PLANNING_PROMPT.format(title=title, creator=creator, audience=audience, tone=tone)
        return self._invoke_llm(prompt)

    def transcript_tool(self, video_id: str) -> str:
        """TOOL: Downloads and cleans subtitles using youtube-transcript-api."""
        return utils.fetch_transcript(video_id)

    def analysis_tool(self, title: str, transcript: str) -> str:
        """TOOL: Reflects on raw transcript to isolate key insights and quotes."""
        # Truncate transcript to save input tokens and keep execution fast
        truncated = transcript[:35000] if len(transcript) > 35000 else transcript
        prompt = prompts.REFLECTION_PROMPT.format(title=title, transcript=truncated)
        return self._invoke_llm(prompt)

    def content_generator_tool(self, reflection: str, audience: str, tone: str, platform: str) -> str:
        """TOOL: Generates custom social copy tailored to audience and tone."""
        if platform == "linkedin":
            prompt = prompts.LINKEDIN_PROMPT.format(reflection=reflection, audience=audience, tone=tone)
        elif platform == "twitter":
            prompt = prompts.TWITTER_PROMPT.format(reflection=reflection, audience=audience, tone=tone)
        elif platform == "instagram":
            prompt = prompts.INSTAGRAM_PROMPT.format(reflection=reflection, audience=audience, tone=tone)
        elif platform == "summary":
            prompt = prompts.SUMMARY_PROMPT.format(reflection=reflection)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        return self._invoke_llm(prompt)

    def reviewer_tool(self, linkedin: str, twitter: str, instagram: str, audience: str, tone: str) -> Dict[str, Any]:
        """TOOL: Evaluation agent reviewing drafts against audience/tone criteria."""
        prompt = prompts.REVIEWER_PROMPT.format(
            linkedin=linkedin,
            twitter=twitter,
            instagram=instagram,
            audience=audience,
            tone=tone
        )
        response_text = self._invoke_llm(prompt)
        return self._parse_json(response_text)

    def improvement_tool(self, platform: str, original_post: str, suggestions: str, audience: str, tone: str) -> str:
        """TOOL: Self-improvement agent that rewrites weak assets based on critiques."""
        prompt = prompts.IMPROVEMENT_PROMPT.format(
            platform=platform,
            original_post=original_post,
            suggestions=suggestions,
            audience=audience,
            tone=tone
        )
        return self._invoke_llm(prompt)

    def report_tool(self, critiques_json: str, audience: str, tone: str) -> str:
        """TOOL: Synthesizes final strengths, weaknesses, and package recommendations."""
        prompt = prompts.REPORT_PROMPT.format(critiques_json=critiques_json, audience=audience, tone=tone)
        return self._invoke_llm(prompt)

    # =====================================================================
    # AGENT COORDINATION LOOP
    # =====================================================================

    def run(self, url: str, audience: str, tone: str) -> Generator[Dict[str, Any], None, None]:
        """
        Coordinates the agentic execution loop.
        Yields state updates in real-time for rendering the Agent Dashboard and Thought Trace.
        """
        start_time = time.time()
        steps_completed = []
        
        # --- 1. URL VALIDATION ---
        yield {"status": "info", "step": "Validation", "log": f"Validating YouTube URL: '{url}'"}
        
        if not utils.validate_url(url):
            raise ValueError("Invalid YouTube URL. Please provide a standard watch, shorts, or share link.")
            
        video_id = utils.extract_video_id(url)
        metadata = utils.get_metadata(video_id)
        steps_completed.append("URL Validation")
        
        yield {
            "status": "success", 
            "step": "Validation", 
            "log": f"Video validated: '{metadata['title']}' by {metadata['author_name']}."
        }

        # --- 2. AGENT PLANNING ---
        yield {"status": "info", "step": "Planning", "log": f"Formulating agent execution plan for Audience='{audience}' and Tone='{tone}'..."}
        
        plan = self.planning_tool(metadata["title"], metadata["author_name"], audience, tone)
        steps_completed.append("Agent Planning")
        
        yield {"status": "success", "step": "Planning", "log": f"Plan formulated:\n{plan}"}

        # --- 3. TRANSCRIPT TOOL ---
        yield {"status": "info", "step": "Transcript Fetching", "log": "Invoking Transcript Extraction Tool..."}
        
        transcript = self.transcript_tool(video_id)
        transcript_length = len(transcript.split())
        steps_completed.append("Transcript Fetching")
        
        yield {"status": "success", "step": "Transcript Fetching", "log": f"Tool complete. Transcript loaded ({transcript_length} words)."}

        # --- 4. DEEP ANALYSIS ---
        yield {"status": "info", "step": "Deep Analysis", "log": "Invoking Analysis Tool to reflect on content..."}
        
        reflection = self.analysis_tool(metadata["title"], transcript)
        steps_completed.append("Deep Analysis")
        
        yield {"status": "success", "step": "Deep Analysis", "log": f"Reflection completed:\n{reflection}"}

        # --- 5. CONTENT GENERATION ---
        yield {"status": "info", "step": "Generation", "log": "Generating first drafts (LinkedIn, Twitter Thread, Instagram Caption)..."}
        
        summary = self.content_generator_tool(reflection, audience, tone, "summary")
        linkedin_orig = self.content_generator_tool(reflection, audience, tone, "linkedin")
        twitter_orig = self.content_generator_tool(reflection, audience, tone, "twitter")
        instagram_orig = self.content_generator_tool(reflection, audience, tone, "instagram")
        steps_completed.append("Asset Generation")
        
        yield {
            "status": "success", 
            "step": "Generation", 
            "log": "Drafting completed. Handing over to Reflection Reviewer agent."
        }

        # --- 6. SELF-REFLECTION & EVALUATION ---
        yield {"status": "info", "step": "Review", "log": "Invoking Reviewer Tool to evaluate and score drafts..."}
        
        evaluation = self.reviewer_tool(linkedin_orig, twitter_orig, instagram_orig, audience, tone)
        steps_completed.append("Reflection & Evaluation")
        
        yield {
            "status": "success", 
            "step": "Review", 
            "log": f"Evaluation Scores: LinkedIn={evaluation['linkedin']['score']}/100, "
                   f"Twitter={evaluation['twitter']['score']}/100, Instagram={evaluation['instagram']['score']}/100."
        }

        # --- 7. SELF-IMPROVEMENT LOOP ---
        linkedin_final = linkedin_orig
        twitter_final = twitter_orig
        instagram_final = instagram_orig
        
        improvements_made = {}
        
        # We loop through platforms and conditionally trigger the improvement tool for scores < 85
        for platform, orig, score, key in [
            ("linkedin", linkedin_orig, evaluation["linkedin"]["score"], "linkedin"),
            ("twitter", twitter_orig, evaluation["twitter"]["score"], "twitter"),
            ("instagram", instagram_orig, evaluation["instagram"]["score"], "instagram")
        ]:
            if score < 85:
                yield {
                    "status": "info", 
                    "step": "Self-Improvement", 
                    "log": f"Score for {platform.capitalize()} ({score}/100) is below 85 threshold. Triggering Improvement Tool..."
                }
                
                critique = evaluation[key]["suggestions"]
                improved = self.improvement_tool(platform, orig, critique, audience, tone)
                
                # Save final and track diff
                if platform == "linkedin":
                    linkedin_final = improved
                elif platform == "twitter":
                    twitter_final = improved
                elif platform == "instagram":
                    instagram_final = improved
                    
                improvements_made[platform] = {
                    "original": orig,
                    "improved": improved,
                    "critique": critique
                }
                
                yield {
                    "status": "success", 
                    "step": "Self-Improvement", 
                    "log": f"Successfully completed self-improvement for {platform.capitalize()}!"
                }
                
        steps_completed.append("Self-Improvement Loop")

        # --- 8. AI REFLECTION REPORT ---
        yield {"status": "info", "step": "Strategic Report", "log": "Synthesizing final strategic review report..."}
        
        report = self.report_tool(json.dumps(evaluation), audience, tone)
        steps_completed.append("Reflection Report")
        
        # Calculate execution metrics
        elapsed_time = round(time.time() - start_time, 2)
        total_generated_words = len(
            (summary + linkedin_final + twitter_final + instagram_final + report).split()
        )
        
        yield {
            "status": "done",
            "step": "Complete",
            "log": f"All tools successfully orchestrated in {elapsed_time}s!",
            "results": {
                "metadata": metadata,
                "transcript": transcript,
                "summary": summary,
                "linkedin": linkedin_final,
                "twitter": twitter_final,
                "instagram": instagram_final,
                "evaluation": evaluation,
                "report": report,
                "improvements": improvements_made,
                "metrics": {
                    "execution_time": f"{elapsed_time} seconds",
                    "transcript_length": f"{transcript_length} words",
                    "words_generated": f"{total_generated_words} words",
                    "model_used": MODEL_NAME,
                    "steps_completed": steps_completed,
                    "plan": plan
                }
            }
        }
