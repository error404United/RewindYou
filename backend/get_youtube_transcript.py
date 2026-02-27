from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import os


def extract_video_id(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    return None


def fetch_transcript(youtube_url: str) -> dict:
    """Fetch transcript from YouTube. Returns dict with video_id, url, and transcript lines."""
    video_id = extract_video_id(youtube_url)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)

    lines = [item.text for item in transcript]

    return {
        "video_id": video_id,
        "url": youtube_url,
        "transcript": lines
    }


def save_transcript_to_json(youtube_url: str) -> str:
    """Fetch transcript and save to local JSON file. Returns file path."""
    result = fetch_transcript(youtube_url)

    folder_name = "extracted_data"
    os.makedirs(folder_name, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(folder_name, f"{timestamp}.json")

    data = {
        **result,
        "created_at": timestamp,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return file_path

