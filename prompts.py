# Prompts file supporting advanced Agentic AI behaviors:
# Planning, Reflection, Evaluation, Diffs, and Report Generation.

SYSTEM_GUIDELINES = """
You write naturally, like an expert human copywriter.
- NEVER use robotic clichés like "In this video...", "Unlock the power of...", "Here are key takeaways:", "A game-changer", "Revolutionize", "Furthermore", "In conclusion".
- Write conversationally. Adapt writing structures to match the specific audience and tone requested.
"""

PLANNING_PROMPT = """
You are an AI planning agent. You have been asked to repurpose a video.
Video Title: "{title}"
Video Creator: "{creator}"
Target Audience: {audience}
Target Tone: {tone}

Draft a 3-step execution plan of how you will extract key insights from the transcript and shape them into custom content for this specific audience and tone.
Write in the first person ("I will..."). Keep it under 100 words.
"""

REFLECTION_PROMPT = """
You are an AI analysis agent. Reflect on this video transcript:
Video Title: "{title}"

Outline:
1. Core problem discussed.
2. Top 3 essential insights/lessons.
3. 2 memorable direct quotes.

Transcript:
{transcript}

Keep your reflection concise (under 200 words).
"""

SUMMARY_PROMPT = SYSTEM_GUIDELINES + """
Based on the transcript reflection, write a clean 3-sentence summary of the video.
Ensure it is engaging, direct, and hooks the reader.

Reflection:
{reflection}
"""

LINKEDIN_PROMPT = SYSTEM_GUIDELINES + """
Create a LinkedIn post based on the video reflection.
Target Audience: {audience}
Target Tone: {tone}

- Word count: 150-250 words.
- Include an attention-grabbing hook customized for {audience} in a {tone} tone.
- Detail 3 structured, high-value bullet points showing key lessons.
- End with a strong CTA that encourages discussion relevant to this audience.

Reflection:
{reflection}
"""

TWITTER_PROMPT = SYSTEM_GUIDELINES + """
Create a high-impact Twitter/X thread based on the video reflection.
Target Audience: {audience}
Target Tone: {tone}

- Create exactly 5 tweets, numbered clearly ("1/5", "2/5", etc.).
- Tweet 1: A powerful hook tailored to {audience} using a {tone} tone.
- Tweets 2-4: Core lessons and insights from the reflection, structured for readability.
- Tweet 5: A summary takeaway and a CTA asking a question to drive comments.
- Keep each tweet under 280 characters.

Reflection:
{reflection}
"""

INSTAGRAM_PROMPT = SYSTEM_GUIDELINES + """
Create an Instagram caption based on the video reflection.
Target Audience: {audience}
Target Tone: {tone}

- Begin with a highly visual, eye-catching hook.
- Tell a brief narrative story conveying the core message in a {tone} tone, appealing to {audience}.
- Add a clear CTA.
- Add 4-6 relevant hashtags at the bottom.

Reflection:
{reflection}
"""

# The Reviewer Prompt forces the model to return structured JSON evaluating each post
REVIEWER_PROMPT = """
You are an AI quality assurance agent. Evaluate the generated social media posts against the target audience and tone.
Target Audience: {audience}
Target Tone: {tone}

Generated Content to Evaluate:
---
LINKEDIN:
{linkedin}
---
TWITTER:
{twitter}
---
INSTAGRAM:
{instagram}
---

Provide a critique and assign a quality score (0 to 100) for each platform. 
Explain exactly WHY the hook, hashtags, and CTA fit the audience and tone, or list weaknesses if they do not.

You must respond ONLY with a valid JSON object matching the following structure. Do not include any explanations or extra text outside the JSON.

JSON Structure:
{{
  "linkedin": {{
    "score": 90,
    "why_it_fits": "Explain why the hook, CTA, and tone fit the target audience",
    "hook_critique": "Critique of the hook",
    "cta_critique": "Critique of the CTA",
    "hashtags_critique": "Critique of the hashtags (or note if N/A)",
    "suggestions": "Specific bullet points for improvement, or 'None' if score is high"
  }},
  "twitter": {{
    "score": 80,
    "why_it_fits": "...",
    "hook_critique": "...",
    "cta_critique": "...",
    "hashtags_critique": "...",
    "suggestions": "..."
  }},
  "instagram": {{
    "score": 95,
    "why_it_fits": "...",
    "hook_critique": "...",
    "cta_critique": "...",
    "hashtags_critique": "...",
    "suggestions": "..."
  }}
}}
"""

# Prompt to improve a weak post
IMPROVEMENT_PROMPT = SYSTEM_GUIDELINES + """
You are an AI optimization agent. Rewrite the following post to make it stronger based on the provided critique.
Platform: {platform}
Target Audience: {audience}
Target Tone: {tone}

Original Post:
{original_post}

Critique & Suggestions:
{suggestions}

Rewrite this post completely, implementing all suggestions.
Your output must contain ONLY the new rewritten post. Do not include preambles, explanations, or quotes around the output.
"""

# Prompt for the final AI Reflection Report
REPORT_PROMPT = """
You are a senior AI marketing strategist. Review the final generated social media assets and the critiques.
Target Audience: {audience}
Target Tone: {tone}

Critiques and Scores:
{critiques_json}

Write a short executive reflection report. Summarize:
1. **Strengths**: What does this content package do exceptionally well for {audience}?
2. **Weaknesses**: What minor compromises were made?
3. **Strategic Suggestions**: Tips for the creator to maximize engagement.
4. **Final Confidence Rating**: Give an overall package rating (e.g. "90% - Recommended for publication").

Keep the report concise, structured with clear markdown headings, and under 150 words.
"""
