from flask import Flask, request, jsonify, session
from db.mongodb import get_pages_collection, get_users_collection
import uuid
from datetime import datetime
import bcrypt
from dotenv import load_dotenv
import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# -------------------- SIGNUP --------------------
@app.route("/signup", methods=["POST"])
def signup():
    users = get_users_collection()
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    # Check if user already exists
    if users.find_one({"username": username}):
        return jsonify({"message": "User already exists"}), 409

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    users.insert_one(user)

    return jsonify({"message": "User signed up successfully"}), 201


# -------------------- LOGIN --------------------
@app.route("/login", methods=["POST"])
def login():
    users = get_users_collection()
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = users.find_one({"username": username})

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Store session
    session["user_id"] = user["_id"]
    session["username"] = user["username"]

    return jsonify({"message": "Login successful"}), 200


# -------------------- LOGOUT --------------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# -------------------- STORE PAGE (AUTH REQUIRED) --------------------
@app.route("/store", methods=["POST"])
def store_page():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    pages = get_pages_collection()
    data = request.json

    content_id = str(uuid.uuid4())

    document = {
        "_id": content_id,
        "user_id": session["user_id"],
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


# -------------------- TIMELINE (AUTH REQUIRED) --------------------
@app.route("/timeline", methods=["GET"])
def get_timeline():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    pages = get_pages_collection()
    results = pages.find(
        {"user_id": session["user_id"]}
    ).sort("timestamp", -1)

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
