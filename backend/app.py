# 
from flask import Flask, request, jsonify
from db.mongodb import get_users_collection, get_pages_collection
import uuid
from datetime import datetime
import bcrypt
from dotenv import load_dotenv
import os
from auth.jwt_utils import generate_access_token, generate_refresh_token, verify_refresh_token
from auth.middleware import jwt_required
from pymongo.errors import DuplicateKeyError
import jwt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    users = get_users_collection()
    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "All fields required"}), 400

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    try:
        users.insert_one(user)
    except DuplicateKeyError:
        return jsonify({"message": "Username or email already exists"}), 409

    return jsonify({"message": "Signup successful"}), 201

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    users = get_users_collection()
    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = generate_access_token(user["_id"], user["username"])
    refresh_token = generate_refresh_token(user["_id"])

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# ---------------- REFRESH ----------------
@app.route("/refresh", methods=["POST"])
def refresh():
    data = request.json
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"message": "Refresh token required"}), 400

    try:
        payload = verify_refresh_token(refresh_token)
        new_access = generate_access_token(payload["user_id"], "user")
        return jsonify({"access_token": new_access}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid refresh token"}), 401

# ---------------- STORE PAGE ----------------
@app.route("/store", methods=["POST"])
@jwt_required
def store_page():
    pages = get_pages_collection()
    data = request.json

    doc = {
        "_id": str(uuid.uuid4()),
        "user_id": request.user["user_id"],
        "url": data.get("url"),
        "title": data.get("title"),
        "summary": data.get("summary"),
        "timestamp": datetime.utcnow()
    }

    pages.insert_one(doc)

    return jsonify({"message": "Stored"}), 201

# ---------------- TIMELINE ----------------
@app.route("/timeline", methods=["GET"])
@jwt_required
def timeline():
    pages = get_pages_collection()

    results = pages.find(
        {"user_id": request.user["user_id"]}
    ).sort("timestamp", -1)

    data = []
    for doc in results:
        data.append({
            "id": doc["_id"],
            "title": doc.get("title"),
            "url": doc.get("url"),
            "timestamp": doc.get("timestamp")
        })

    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True)
