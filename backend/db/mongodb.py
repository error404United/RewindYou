from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

try:
    # Use certifi CA bundle to ensure proper TLS verification with Atlas
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tls=True, tlsCAFile=certifi.where())
    client.server_info()
    print("✅ MongoDB connection successful")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

db = client[DB_NAME]

# ---------- Index Initialization ----------
def init_indexes():
    users = db["users"]
    pages = db["pages"]

    # Unique identity constraints
    users.create_index("username", unique=True)
    users.create_index("email", unique=True)

    # Performance indexes
    pages.create_index("user_id")
    pages.create_index("timestamp")

    print("✅ Indexes initialized")

try:
    init_indexes()
except Exception as e:
    print("⚠️ Index initialization skipped due to error:", e)

# ---------- Collections ----------
def get_pages_collection():
    return db["pages"]

def get_users_collection():
    return db["users"]
