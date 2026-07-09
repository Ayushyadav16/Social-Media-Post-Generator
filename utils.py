import re
import requests
import time
from typing import Dict, Any, Optional, List
from youtube_transcript_api import YouTubeTranscriptApi

# Compiled regex matching standard, shortened, embed, and shorts YouTube URLs
YOUTUBE_URL_REGEX = re.compile(
    r'^(?:https?://)?(?:www\.|m\.)?'
    r'(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|v/|e/)|youtu\.be/)'
    r'([a-zA-Z0-9_-]{11})'
)

def validate_url(url: str) -> bool:
    """
    Validates if a URL is a valid YouTube link.
    Returns True if valid, False otherwise.
    """
    if not url:
        return False
    return bool(YOUTUBE_URL_REGEX.match(url.strip()))

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the 11-character YouTube video ID from a URL.
    Returns the string ID or None if not found.
    """
    match = YOUTUBE_URL_REGEX.match(url.strip())
    return match.group(1) if match else None

def get_metadata(video_id: str) -> Dict[str, Any]:
    """
    Fetches the video title, author, and thumbnail URL keylessly 
    using YouTube's public oEmbed endpoint.
    
    Returns a dictionary of metadata, with placeholder fallbacks on failure.
    """
    fallback_data = {
        "title": f"YouTube Video ({video_id})",
        "author_name": "Creator",
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    }
    
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", fallback_data["title"]),
                "author_name": data.get("author_name", fallback_data["author_name"]),
                "thumbnail_url": data.get("thumbnail_url", fallback_data["thumbnail_url"])
            }
    except Exception:
        # Silently log/fallback if there is no internet or call fails
        pass
        
    return fallback_data

def fetch_transcript(video_id: str) -> str:
    """
    Downloads subtitles/transcript for a given video.
    Implements a robust 2-pass retry loop and a 5-tier translation fallback:
      Tier 1: Fetch English transcript directly.
      Tier 2: Find manually created English transcript.
      Tier 3: Find auto-generated English transcript.
      Tier 4: Auto-translate any manual/generated foreign transcript into English.
      Tier 5: Fetch raw first available language.
      
    If completely failed, suggests supported languages instead of crashing.
    """
    api = YouTubeTranscriptApi()
    last_error = None
    
    # 2-Pass Retry Loop
    for attempt in range(1, 3):
        try:
            # Tier 1: Try fetching English directly (fast path)
            raw_segments = api.fetch(video_id, languages=['en'])
            return _clean_and_concat(raw_segments)
        except Exception as e:
            last_error = e
            
        # Wait slightly on retry attempt
        if attempt == 2:
            time.sleep(1)
            
        # Tier 2-5: Try list available transcripts and fetch/translate
        try:
            transcript_list = api.list(video_id)
            chosen = None
            
            try:
                # Tier 2: Try manual English
                chosen = transcript_list.find_manually_created_transcript(['en'])
            except Exception:
                try:
                    # Tier 3: Try auto English
                    chosen = transcript_list.find_generated_transcript(['en'])
                except Exception:
                    # Tier 4: Look for a translatable foreign language
                    for t in transcript_list:
                        if t.is_translatable:
                            chosen = t.translate('en')
                            break
                    # Tier 5: Fall back to the absolute first language
                    if not chosen:
                        chosen = next(iter(transcript_list))
                        
            if chosen:
                raw_segments = chosen.fetch()
                return _clean_and_concat(raw_segments)
        except Exception as inner_e:
            last_error = inner_e

    # Handle final failure and suggest available languages
    try:
        transcript_list = api.list(video_id)
        available = [f"{t.language} ({t.language_code})" for t in transcript_list]
        raise RuntimeError(
            f"Could not load English transcript. "
            f"Available languages for this video: {available}. "
            f"Please choose a video with captions in one of these languages."
        ) from last_error
    except Exception as list_err:
        if isinstance(list_err, RuntimeError):
            raise list_err
        raise RuntimeError(
            "Subtitles are completely disabled for this video, or it is unavailable. "
            "Please try a video with closed captions enabled."
        ) from last_error

def _clean_and_concat(raw_segments: List[Any]) -> str:
    """
    Helper function to clean time-coded segments and concatenate them.
    Supports both dictionary outputs and newer FetchedTranscriptSnippet structures.
    """
    clean_lines = []
    for segment in raw_segments:
        if isinstance(segment, dict):
            text = segment.get("text", "")
        else:
            text = getattr(segment, "text", "")
            
        text = text.strip().replace("\n", " ")
        if text:
            clean_lines.append(text)
            
    full_text = " ".join(clean_lines)
    full_text = " ".join(full_text.split()) # Normalize spaces
    
    if not full_text:
        raise ValueError("Transcript text resolved to empty.")
        
    return full_text
