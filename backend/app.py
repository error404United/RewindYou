from flask import Flask, request, jsonify
from backend.db.mongodb import get_pages_collection
import uuid
from datetime import datetime

app = Flask(__name__)

@app.route("/store", methods=["POST"])
def store_page():
    pages = get_pages_collection()
    
    data = request.json
    content_id = str(uuid.uuid4())

    document = {
        "_id": content_id,
        "url": data.get("url"),
        "title": data.get("title"),
        "summary": data.get("summary"),
        "timestamp": datetime.utcnow()
    }

    pages.insert_one(document)

    return jsonify({
        "message": "Page stored successfully",
        "content_id": content_id
    })

@app.route("/timeline", methods=["GET"])
def get_timeline():
    pages = get_pages_collection()
    
    results = pages.find().sort("timestamp", -1)
    timeline = []

    for doc in results:
        timeline.append({
            "id": doc["_id"],
            "title": doc["title"],
            "url": doc["url"],
            "timestamp": doc["timestamp"]
        })

    return jsonify(timeline)

if __name__ == "__main__":
    app.run(debug=True)
