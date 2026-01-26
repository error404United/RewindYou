"""Unified Flask application for RewindYou."""

import os
import re
import uuid
from datetime import datetime
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo.errors import DuplicateKeyError, PyMongoError
import jwt

from ai.embedding_allminilm import embed_text
from ai.summarize import MAX_INPUT_TOKENS, summarize_text
from auth.jwt_utils import (
    ACCESS_TOKEN_MINUTES,
    REFRESH_TOKEN_DAYS,
    generate_access_token,
    generate_refresh_token,
    verify_refresh_token,
)
from auth.middleware import jwt_required
from db.chroma_db import add_embedding, query_embeddings
from db.mongodb import get_pages_collection, get_users_collection


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CORS(app)

limiter = Limiter(get_remote_address, app=app, default_limits=["500 per hour"])


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")
URL_REGEX = re.compile(r"^https?://.+")
MAX_CONTENT_LENGTH = 10000000
MIN_CONTENT_LENGTH = 50
MAX_QUERY_LENGTH = 500


class ValidationError(Exception):
    def __init__(self, message: str, field: Optional[str] = None, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.field = field
        self.status_code = status_code


@app.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"error": err.message, "field": err.field}), err.status_code


@app.errorhandler(PyMongoError)
def handle_db_error(err: PyMongoError):
    app.logger.error("Database error: %s", err)
    response = jsonify({"error": "Database error"})
    return response, 500


@app.errorhandler(Exception)
def handle_generic_error(err: Exception):
    app.logger.exception(err)
    if isinstance(err, jwt.InvalidTokenError):
        return jsonify({"error": "Invalid token"}), 401
    return jsonify({"error": "Internal server error"}), 500


def _validate_email(email: str) -> None:
    if not email or not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email format", "email")


def _validate_password(password: str) -> None:
    if not password or not PASSWORD_REGEX.match(password):
        raise ValidationError(
            "Password must be 8+ chars with upper, lower, number, and special",
            "password",
        )


def _validate_url(url: str) -> None:
    if not url or not URL_REGEX.match(url):
        raise ValidationError("Invalid URL", "url")


def _rate_key_user():
    return getattr(request, "user", {}).get("user_id") or get_remote_address()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "unified"}), 200


@app.route("/api/signup", methods=["POST"])
@limiter.limit("5 per minute")
def signup():
    users = get_users_collection()
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username:
        raise ValidationError("Username is required", "username")

    _validate_email(email)
    _validate_password(password)

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_id = str(uuid.uuid4())
    token_version = str(uuid.uuid4())

    user = {
        "_id": user_id,
        "username": username,
        "email": email,
        "password": hashed_password,
        "token_version": token_version,
        "created_at": datetime.utcnow(),
    }

    try:
        users.insert_one(user)
    except DuplicateKeyError:
        raise ValidationError("Username or email already exists", "username")

    access_token = generate_access_token(user_id, username, email, token_version)
    refresh_token = generate_refresh_token(user_id, token_version)

    return (
        jsonify(
            {
                "message": "Signup successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"id": user_id, "username": username, "email": email},
            }
        ),
        201,
    )


@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    users = get_users_collection()
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    _validate_email(email)
    if not password:
        raise ValidationError("Password is required", "password")

    user = users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        raise ValidationError("Invalid credentials", None, 401)

    token_version = str(uuid.uuid4())
    users.update_one({"_id": user["_id"]}, {"$set": {"token_version": token_version}})

    access_token = generate_access_token(user["_id"], user["username"], email, token_version)
    refresh_token = generate_refresh_token(user["_id"], token_version)

    return jsonify(
        {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user["_id"],
                "username": user.get("username"),
                "email": email,
            },
            "expires_in_minutes": ACCESS_TOKEN_MINUTES,
        }
    ), 200


@app.route("/api/refresh", methods=["POST"])
@limiter.limit("5 per minute")
def refresh():
    users = get_users_collection()
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token required", "refresh_token")

    try:
        payload = verify_refresh_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise ValidationError("Refresh token expired", "refresh_token", 401)
    except jwt.InvalidTokenError:
        raise ValidationError("Invalid refresh token", "refresh_token", 401)

    user = users.find_one({"_id": payload.get("user_id")})
    if not user:
        raise ValidationError("User not found", None, 401)

    if user.get("token_version") != payload.get("token_version"):
        raise ValidationError("Refresh token revoked", "refresh_token", 401)

    new_version = str(uuid.uuid4())
    users.update_one({"_id": user["_id"]}, {"$set": {"token_version": new_version}})

    access_token = generate_access_token(
        user["_id"], user.get("username"), user.get("email"), new_version
    )
    new_refresh = generate_refresh_token(user["_id"], new_version)

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "expires_in_minutes": ACCESS_TOKEN_MINUTES,
            "refresh_expires_in_days": REFRESH_TOKEN_DAYS,
        }
    ), 200


@app.route("/api/summarize", methods=["POST"])
@jwt_required
@limiter.limit("10 per minute", key_func=_rate_key_user)
def summarize_route():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text or len(text.strip()) < MIN_CONTENT_LENGTH:
        raise ValidationError("Text is too short to summarize", "text")
    if len(text) > MAX_CONTENT_LENGTH:
        raise ValidationError("Text exceeds maximum length", "text")
    try:
        summary = summarize_text(text)
    except Exception as exc:  # model errors
        app.logger.exception(exc)
        resp = jsonify({"error": "Model unavailable, try again"})
        resp.headers["Retry-After"] = "30"
        return resp, 503
    return jsonify({"summary": summary}), 200


@app.route("/api/embed", methods=["POST"])
@jwt_required
@limiter.limit("15 per minute", key_func=_rate_key_user)
def embed_route():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text.strip():
        raise ValidationError("Text cannot be empty", "text")
    try:
        embedding = embed_text(text).tolist()
    except Exception as exc:
        app.logger.exception(exc)
        return jsonify({"error": "Embedding model error"}), 503
    return jsonify({"embedding": embedding}), 200


@app.route("/api/save-page-data", methods=["POST"])
@jwt_required
@limiter.limit("10 per minute", key_func=_rate_key_user)
def save_page_data():
    pages = get_pages_collection()
    data = request.get_json(silent=True) or {}

    url = (data.get("url") or "").strip()
    title = (data.get("title") or "Untitled").strip() or "Untitled"
    content = data.get("articleContent") or data.get("content") or ""

    _validate_url(url)
    if len(content) < MIN_CONTENT_LENGTH:
        raise ValidationError("Content too short", "content")
    if len(content) > MAX_CONTENT_LENGTH:
        raise ValidationError("Content too long", "content")

    try:
        summary = data.get("summary") or summarize_text(content)
        embedding = embed_text(summary).tolist()
    except ValidationError:
        raise
    except Exception as exc:
        app.logger.exception(exc)
        resp = jsonify({"error": "AI processing failed"})
        resp.headers["Retry-After"] = "30"
        return resp, 503

    page_id = str(uuid.uuid4())
    doc = {
        "_id": page_id,
        "user_id": request.user["user_id"],
        "url": url,
        "title": title,
        "summary": summary,
        "word_count": len(content.split()),
        "created_at": datetime.utcnow(),
    }

    pages.insert_one(doc)

    add_embedding(
        doc_id=page_id,
        embedding=embedding,
        metadata={
            "page_id": page_id,
            "user_id": request.user["user_id"],
            "url": url,
            "title": title,
            "summary": summary,
            "created_at": doc["created_at"].isoformat(),
        },
    )

    return jsonify({"message": "Saved", "page_id": page_id, "summary": summary}), 201


@app.route("/api/search", methods=["POST"])
@jwt_required
@limiter.limit("30 per minute", key_func=_rate_key_user)
def search():
    pages = get_pages_collection()
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        raise ValidationError("Query required", "query")
    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError("Query too long", "query")

    try:
        query_embedding = embed_text(query).tolist()
        results = query_embeddings(
            query_embedding,
            where={"user_id": request.user["user_id"]},
            n_results=5,
        )
    except Exception as exc:
        app.logger.exception(exc)
        resp = jsonify({"error": "Search unavailable"})
        resp.headers["Retry-After"] = "10"
        return resp, 503

    matches = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx, page_id in enumerate(ids):
        meta = metadatas[idx] if idx < len(metadatas) else {}
        doc = pages.find_one({"_id": page_id})
        matches.append(
            {
                "page_id": page_id,
                "title": meta.get("title") or doc.get("title") if doc else None,
                "url": meta.get("url") or doc.get("url") if doc else None,
                "summary": meta.get("summary") or doc.get("summary") if doc else None,
                "score": distances[idx] if idx < len(distances) else None,
                "created_at": meta.get("created_at")
                or (doc.get("created_at").isoformat() if doc and doc.get("created_at") else None),
            }
        )

    return jsonify({"results": matches}), 200


@app.route("/api/timeline", methods=["GET"])
@jwt_required
def timeline():
    pages = get_pages_collection()
    results = (
        pages.find({"user_id": request.user["user_id"]}).sort("created_at", -1).limit(20)
    )
    data = [
        {
            "id": doc["_id"],
            "title": doc.get("title"),
            "url": doc.get("url"),
            "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        }
        for doc in results
    ]
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
