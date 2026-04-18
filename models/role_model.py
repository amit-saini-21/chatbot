from datetime import datetime

from db.mongo import chats_collection, roles_collection
from pymongo.errors import DuplicateKeyError
from utils.id_utils import to_object_id


def _serialize_role(role):
    if not role:
        return None

    serialized = dict(role)
    serialized["_id"] = str(serialized["_id"])
    serialized["user_id"] = str(serialized["user_id"])
    serialized["memory"] = list(serialized.get("memory", []))
    if serialized.get("created_at"):
        serialized["created_at"] = serialized["created_at"].isoformat()
    if serialized.get("updated_at"):
        serialized["updated_at"] = serialized["updated_at"].isoformat()
    return serialized


def _normalize_memory(memory):
    if memory is None:
        return []
    if isinstance(memory, str):
        memory = [memory]

    cleaned = []
    seen = set()
    for item in memory:
        text = str(item).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


def create_role(user_id, role_type, config=None, memory=None):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return None

    role = {
        "user_id": user_object_id,
        "role_type": role_type,
        "config": config or {},
        "memory": _normalize_memory(memory),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        return roles_collection.insert_one(role).inserted_id
    except DuplicateKeyError:
        raise
    except Exception:
        return None


def ensure_default_role(user_id):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return None

    existing_role = roles_collection.find_one({"user_id": user_object_id, "role_type": "assistant"})
    if existing_role:
        return existing_role["_id"]

    try:
        return create_role(user_object_id, "assistant", {"tone": "friendly", "style": "casual"}, memory=[])
    except DuplicateKeyError:
        existing_role = roles_collection.find_one({"user_id": user_object_id, "role_type": "assistant"})
        return existing_role["_id"] if existing_role else None


def get_all_roles(user_id):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return []

    roles = list(roles_collection.find({"user_id": user_object_id}).sort("created_at", 1))
    return [_serialize_role(role) for role in roles]


def get_role(role_id, user_id=None):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return None

    query = {"_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return None
        query["user_id"] = user_object_id

    role = roles_collection.find_one(query)
    return _serialize_role(role) if role else None


def role_exists(user_id, role_type):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return False
    return roles_collection.find_one({"user_id": user_object_id, "role_type": role_type}) is not None


def update_role(role_id, config=None, user_id=None):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return False

    query = {"_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    update_fields = {"updated_at": datetime.utcnow()}
    if config is not None:
        update_fields["config"] = config

    result = roles_collection.update_one(query, {"$set": update_fields})
    return result.matched_count > 0


def update_memory(role_id, memory, user_id=None):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return False

    query = {"_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    result = roles_collection.update_one(
        query,
        {"$set": {"memory": _normalize_memory(memory), "updated_at": datetime.utcnow()}},
    )
    return result.matched_count > 0


def append_memory_entries(role_id, entries, user_id=None):
    role = get_role(role_id, user_id=user_id)
    if not role:
        return False

    merged = role.get("memory", []) + _normalize_memory(entries)
    return update_memory(role_id, merged, user_id=user_id)


def delete_role(role_id, user_id=None):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return False

    query = {"_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    deleted_role = roles_collection.delete_one(query)
    if deleted_role.deleted_count == 0:
        return False

    chat_query = {"role_id": role_object_id}
    if "user_id" in query:
        chat_query["user_id"] = query["user_id"]
    chats_collection.delete_many(chat_query)
    return True

