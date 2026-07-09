# Simple and clean prompt templates for the Agentic AI content generator.
# Designed to write naturally, avoid robotic clichés, and tailor copy per platform.

# General system guidelines to avoid robotic AI voice
SYSTEM_GUIDELINES = """
You write like a human.
- NEVER use robotic clichés like "In this video...", "Unlock the power of...", "Here are key takeaways:", "A game-changer", "Revolutionize", "Furthermore", "In conclusion".
- Write conversationally. Speak directly to the reader. Use formatting (like line breaks and short paragraphs) to make it highly readable.
"""

PLANNING_PROMPT = """
You are an AI distribution agent. You have been asked to help a creator repurpose their video content.
Video Title: "{title}"
Video Creator: "{creator}"

Outline a short, 3-step action plan of how you will extract value from this video and adapt it for LinkedIn, Twitter/X, and Instagram.
Write in the first person ("I will..."). Keep it under 100 words.
"""

REFLECTION_PROMPT = """
You are an AI analysis agent. You have been provided with the transcript of a video.
Video Title: "{title}"

Read the transcript and reflect on it:
1. What is the core problem being solved?
2. What are the 3 most important insights or takeaways?
3. What is a key quote or memorable statement?

Transcript:
{transcript}

Write a concise reflection detailing your findings. Keep it under 200 words.
"""

SUMMARY_PROMPT = SYSTEM_GUIDELINES + """
Based on the transcript and your reflection, write a clean 3-sentence summary of the video.
Ensure it is engaging and directly tells the reader what the video is about.

Reflection:
{reflection}
"""

LINKEDIN_PROMPT = SYSTEM_GUIDELINES + """
Create a LinkedIn post based on the video reflection.
- Word count: 150-250 words.
- Structure:
  * A strong hook (e.g. a counter-intuitive statement, a question, or a bold claim).
  * 3 bulleted key insights from the reflection (with spaces between bullets).
  * A clear call-to-action (CTA) inviting comments or thoughts.

Reflection:
{reflection}
"""

TWITTER_PROMPT = SYSTEM_GUIDELINES + """
Create a high-impact Twitter/X thread based on the video reflection.
- Length: exactly 5 tweets.
- Tweet 1: Hook the reader (make them want to read the thread).
- Tweets 2-4: Deliver 3 core insights or lessons from the reflection.
- Tweet 5: Summary takeaway and a question to drive engagement (CTA).
- Format each tweet clearly (e.g., "1/5", "2/5"...) and keep each tweet under 280 characters.

Reflection:
{reflection}
"""

INSTAGRAM_PROMPT = SYSTEM_GUIDELINES + """
Create a storytelling Instagram caption based on the video reflection.
- Structure:
  * Visual attention-grabbing hook.
  * Short narrative story explaining the main idea.
  * Clear call-to-action (CTA).
  * 4-6 relevant hashtags at the bottom.

Reflection:
{reflection}
"""
