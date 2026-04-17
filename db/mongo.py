# db/mongo.py

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

try:
	import certifi
except Exception:  # pragma: no cover - fallback when certifi is unavailable
	certifi = None

load_dotenv()

MONGO_URI = os.getenv("DATABASE_URI", "").strip()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_chat_db").strip() or "ai_chat_db"


def _build_mongo_client() -> MongoClient:
	if not MONGO_URI:
		raise RuntimeError("DATABASE_URI is not set")

	# Assumption: Flask app is a long-running API workload (OLTP style), so fail fast
	# on connectivity while keeping pooled connections reusable across requests.
	client_options = {
		"serverSelectionTimeoutMS": 8000,
		"connectTimeoutMS": 10000,
		"socketTimeoutMS": 30000,
		"tls": True,
		"appname": "flask-ai-chatbot",
		"server_api": ServerApi("1"),
	}

	# Atlas TLS handshakes are more reliable with certifi CA bundle on some hosts.
	if certifi is not None:
		client_options["tlsCAFile"] = certifi.where()

	return MongoClient(MONGO_URI, **client_options)


client = _build_mongo_client()
db = client[MONGO_DB_NAME]

# Collections
users_collection = db["users"]
roles_collection = db["roles"]
chats_collection = db["chats"]