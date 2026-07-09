import re
import requests
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
    Concatenates timecoded segments into a continuous readable paragraph.
    
    Handles both older API (dict structures) and newer API (object/dataclass structure)
    versions of youtube-transcript-api to prevent crashing.
    """
    # Instantiate client API (required by version 1.2.4+)
    api = YouTubeTranscriptApi()
    
    # Fetch segments
    try:
        # Try retrieving standard manual/generated transcripts (defaults to English first)
        raw_segments = api.fetch(video_id)
    except Exception:
        # Fallback: List transcripts and grab the first available option
        transcript_list = api.list(video_id)
        # Try English manual, then English auto, then any language, translate to English
        try:
            chosen = transcript_list.find_manually_created_transcript(['en'])
        except Exception:
            try:
                chosen = transcript_list.find_generated_transcript(['en'])
            except Exception:
                # Grab whatever language is available
                chosen = next(iter(transcript_list))
                
        # Auto-translate to English if supported
        if chosen.language_code != 'en' and chosen.is_translatable:
            chosen = chosen.translate('en')
            
        raw_segments = chosen.fetch()
        
    # Clean and concatenate lines
    clean_lines = []
    for segment in raw_segments:
        # Read text field, checking both dict format and dataclass attribute format
        if isinstance(segment, dict):
            text = segment.get("text", "")
        else:
            text = getattr(segment, "text", "")
            
        text = text.strip().replace("\n", " ")
        if text:
            clean_lines.append(text)
            
    # Join into a single continuous paragraph
    full_text = " ".join(clean_lines)
    full_text = " ".join(full_text.split()) # normalize spaces
    
    if not full_text:
        raise ValueError("Transcript fetched was empty.")
        
    return full_text
