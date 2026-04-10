"""
Archive cleaned/preprocessed content to extracted_data folder.
Used for evaluation metrics to compare original content against summaries.
"""

import os
import json
from datetime import datetime


def save_cleaned_content(content: str, source_type: str, page_id: str, url: str = "", title: str = "") -> str:
    """
    Save cleaned/preprocessed content to extracted_data folder.
    
    Args:
        content: The cleaned/preprocessed content text
        source_type: 'webpage', 'youtube_transcript', or 'pdf'
        page_id: Unique page identifier (UUID)
        url: Source URL (optional)
        title: Content title (optional)
        
    Returns:
        Path to saved content file (relative to backend root)
    """
    os.makedirs("extracted_data", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"extracted_data/{page_id}_{source_type}_{timestamp}.json"
    
    data = {
        "page_id": page_id,
        "source_type": source_type,
        "url": url,
        "title": title,
        "cleaned_content": content,
        "word_count": len(content.split()),
        "character_count": len(content),
        "saved_at": timestamp,
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Cleaned content saved: {filename}")
    return filename


def load_cleaned_content(filename: str) -> str:
    """
    Load cleaned content from extracted_data folder.
    
    Args:
        filename: Path to content file
        
    Returns:
        Cleaned content text, or empty string if not found
    """
    try:
        if not os.path.exists(filename):
            print(f"⚠️  Content file not found: {filename}")
            return ""
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("cleaned_content", "")
    except Exception as e:
        print(f"❌ Error loading content: {e}")
        return ""
