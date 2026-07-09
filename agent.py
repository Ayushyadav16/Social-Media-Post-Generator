from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import prompts
import utils

# Configurable model name - using Google's standard gemini-1.5-flash.
MODEL_NAME = "gemini-2.5-flash"

class YoutubeAgent:
    """
    An AI Agent that automates the repurposing of YouTube content.
    Demonstrates Agentic AI concepts: Planning, Tool Execution, Reflection, and Generation.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Instantiate the Gemini Chat Model via LangChain.
        # We target the stable v1 API and set convert_system_message_to_human=True
        # to prevent v1 payload structure errors.
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=0.7,
            api_version="v1",
            convert_system_message_to_human=True
        )

    def _invoke_llm(self, prompt: str) -> str:
        """
        Helper method to invoke the LLM. 
        Catches 404 NOT_FOUND errors and runs diagnostics to find available models.
        """
        try:
            return self.llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            err_str = str(e)
            if "NOT_FOUND" in err_str or "404" in err_str:
                try:
                    from google import genai
                    # Initialize official SDK client to list available models
                    client = genai.Client(api_key=self.api_key)
                    models_response = client.models.list()
                    available_models = [m.name.replace("models/", "") for m in models_response]
                    
                    raise ValueError(
                        f"Gemini model '{MODEL_NAME}' was not found or is not supported for your API key.\n\n"
                        f"👉 **Available models for your Google API key are:** {available_models}\n\n"
                        f"Please edit the `MODEL_NAME` variable in `agent.py` (Line 7) to match one of these."
                    ) from e
                except Exception as list_err:
                    if isinstance(list_err, ValueError):
                        raise list_err
                    raise ValueError(
                        f"Model '{MODEL_NAME}' returned 404 NOT_FOUND. "
                        f"Could not retrieve authorized models: {str(list_err)}"
                    ) from e
            raise e

    def run(self, url: str):
        """
        Coordinates the agentic loop.
        Yields status updates dynamically to provide a visual trace of the agent's thought process.
        """
        # --- STEP 1: VALIDATE INPUT & PARSE ---
        yield {"status": "info", "step": "Validation", "log": f"Analyzing URL: '{url}'"}
        
        if not utils.validate_url(url):
            raise ValueError("Invalid YouTube URL format. Please input a standard video link.")
            
        video_id = utils.extract_video_id(url)
        metadata = utils.get_metadata(video_id)
        
        yield {
            "status": "success", 
            "step": "Validation", 
            "log": f"Valid YouTube URL parsed. Extracted ID: '{video_id}'\n"
                   f"Found Video Title: '{metadata['title']}' by '{metadata['author_name']}'"
        }

        # --- STEP 2: PLANNING (Agentic Thought) ---
        yield {"status": "info", "step": "Planning", "log": "Formulating execution plan based on video metadata..."}
        
        plan_prompt = prompts.PLANNING_PROMPT.format(
            title=metadata["title"], 
            creator=metadata["author_name"]
        )
        
        # Invoke LLM to generate the step-by-step plan
        plan_response = self._invoke_llm(plan_prompt)
        
        yield {"status": "success", "step": "Planning", "log": f"Generated Agent Plan:\n{plan_response}"}

        # --- STEP 3: TOOL EXECUTION (Agentic Action) ---
        yield {"status": "info", "step": "Tool Use", "log": "Running transcript extractor tool..."}
        
        try:
            # The agent calls the transcript fetcher tool
            transcript_text = utils.fetch_transcript(video_id)
        except Exception as e:
            raise RuntimeError(f"Transcript Extractor Tool failed: {str(e)}")
            
        word_count = len(transcript_text.split())
        
        yield {
            "status": "success", 
            "step": "Tool Use", 
            "log": f"Successfully extracted transcript via tool. Total size: {word_count} words."
        }

        # --- STEP 4: REFLECTION (Agentic Reasoning) ---
        yield {"status": "info", "step": "Reflection", "log": "Analyzing transcript content and reflecting on core insights..."}
        
        # Truncate transcript to standard safe margins to save tokens and speed up API response
        truncated_transcript = transcript_text[:35000] if len(transcript_text) > 35000 else transcript_text
        
        reflect_prompt = prompts.REFLECTION_PROMPT.format(
            title=metadata["title"], 
            transcript=truncated_transcript
        )
        
        # Invoke LLM to reflect and digest raw subtitles
        reflection_response = self._invoke_llm(reflect_prompt)
        
        yield {"status": "success", "step": "Reflection", "log": f"Agent Reflection & Digested Takeaways:\n{reflection_response}"}

        # --- STEP 5: GENERATION (Execution Output) ---
        yield {"status": "info", "step": "Generation", "log": "Drafting summaries and platform-specific copy..."}
        
        # Create prompts for each output type based on the digested reflection
        summary_prompt = prompts.SUMMARY_PROMPT.format(reflection=reflection_response)
        linkedin_prompt = prompts.LINKEDIN_PROMPT.format(reflection=reflection_response)
        twitter_prompt = prompts.TWITTER_PROMPT.format(reflection=reflection_response)
        instagram_prompt = prompts.INSTAGRAM_PROMPT.format(reflection=reflection_response)
        
        # Execute generations sequentially
        summary = self._invoke_llm(summary_prompt)
        linkedin = self._invoke_llm(linkedin_prompt)
        twitter = self._invoke_llm(twitter_prompt)
        instagram = self._invoke_llm(instagram_prompt)
        
        yield {
            "status": "done", 
            "step": "Complete", 
            "log": "Marketing assets successfully generated!",
            "results": {
                "metadata": metadata,
                "transcript": transcript_text,
                "summary": summary,
                "linkedin": linkedin,
                "twitter": twitter,
                "instagram": instagram
            }
        }
