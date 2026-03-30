from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ MongoDB connection successful")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

db = client[DB_NAME]

# ---------- Index Initialization ----------
def init_indexes():
    users = db["users"]
    pages = db["pages"]
    sessions = db["auth_sessions"]

    # Unique identity constraints
    users.create_index("username", unique=True)
    users.create_index("email", unique=True)

    # Performance indexes
    pages.create_index("user_id")
    pages.create_index("created_at")

    # Auth session indexes
    sessions.create_index("user_id")
    sessions.create_index("revoked_at")
    sessions.create_index("refresh_expires_at", expireAfterSeconds=0)

    print("✅ Indexes initialized")

init_indexes()

# ---------- Collections ----------
def get_pages_collection():
    return db["pages"]

def get_users_collection():
    return db["users"]

def get_sessions_collection():
    return db["auth_sessions"]
