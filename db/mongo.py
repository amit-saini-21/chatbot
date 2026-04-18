import atexit
import logging
import os
import time

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.server_api import ServerApi

try:
	import certifi
except Exception:  # pragma: no cover - fallback when certifi is unavailable
	certifi = None

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("DATABASE_URI", "").strip()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_chat_db").strip() or "ai_chat_db"

_client = None


def _build_mongo_client():
	if not MONGO_URI:
		raise RuntimeError("DATABASE_URI is not set")

	client_options = {
		"serverSelectionTimeoutMS": 5000,
		"connectTimeoutMS": 5000,
		"socketTimeoutMS": 30000,
		"retryReads": True,
		"retryWrites": True,
		"appname": "flask-ai-chatbot",
		"server_api": ServerApi("1"),
	}

	if certifi is not None:
		client_options["tlsCAFile"] = certifi.where()

	return MongoClient(MONGO_URI, **client_options)


def get_client():
	global _client
	if _client is None:
		_client = _build_mongo_client()
	return _client


def get_db():
	return get_client()[MONGO_DB_NAME]


db = get_db()

# Collections
users_collection = db["users"]
roles_collection = db["roles"]
chats_collection = db["chats"]


def initialize_indexes():
	users_collection.create_index([("email", ASCENDING)], unique=True, name="uniq_user_email")
	roles_collection.create_index(
		[("user_id", ASCENDING), ("role_type", ASCENDING)], unique=True, name="uniq_user_role_type"
	)
	roles_collection.create_index([("user_id", ASCENDING)], name="idx_roles_user_id")
	roles_collection.create_index([("role_type", ASCENDING)], name="idx_roles_role_type")
	chats_collection.create_index([("user_id", ASCENDING)], name="idx_chats_user_id")
	chats_collection.create_index([("role_id", ASCENDING)], name="idx_chats_role_id")
	chats_collection.create_index([("created_at", DESCENDING)], name="idx_chats_created_at")


def initialize_database():
	last_error = None
	for attempt in range(2):
		try:
			get_client().admin.command("ping")
			initialize_indexes()
			return True
		except Exception as exc:
			last_error = exc
			if attempt == 0:
				time.sleep(0.25)

	logger.warning("MongoDB initialization failed: %s", last_error)
	return False


def close_client():
	global _client
	if _client is not None:
		_client.close()
		_client = None


atexit.register(close_client)