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

def save_transcript_to_json(youtube_url: str):
    video_id = extract_video_id(youtube_url)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Create folder if it doesn't exist
    folder_name = "extracted_data"
    os.makedirs(folder_name, exist_ok=True)

    # Timestamp-based filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(folder_name, f"{timestamp}.json")

    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)

    # Clean transcript: text only
    lines = [item.text for item in transcript]

    data = {
        "video_id": video_id,
        "created_at": timestamp,
        "transcript": lines
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return file_path


youtube_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

saved_file = save_transcript_to_json(youtube_link)

print(f"Transcript saved at: {saved_file}")

