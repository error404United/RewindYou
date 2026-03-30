import fitz
import requests
import json
import os
from datetime import datetime
from urllib.parse import urlparse, unquote


def save_pdf_from_url(pdf_url):
    response = requests.get(pdf_url, timeout=30)

    if response.status_code != 200:
        raise Exception("Failed to download PDF")

    pdf_path = "temp.pdf"

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    doc = fitz.open(pdf_path)

    pages = []

    for page in doc:
        text = page.get_text("text")
        pages.append(text)

    doc.close()

    os.remove(pdf_path)

    os.makedirs("extracted_data", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"extracted_data/{timestamp}.json"

    data = {
        "source_type": "pdf",
        "url": pdf_url,
        "created_at": timestamp,
        "page_count": len(pages),
        "content": pages
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    joined_content = "\n\n".join(pages).strip()
    parsed = urlparse(pdf_url)
    inferred_title = os.path.basename(parsed.path) or "PDF Document"
    inferred_title = unquote(inferred_title)

    return {
        "filename": filename,
        "page_count": len(pages),
        "content": joined_content,
        "title": inferred_title,
    }