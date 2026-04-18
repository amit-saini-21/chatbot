from datetime import datetime

from db.mongo import chats_collection
from utils.id_utils import to_object_id


def _serialize_chat(chat):
    if not chat:
        return None

    serialized = dict(chat)
    serialized["_id"] = str(serialized["_id"])
    serialized["role_id"] = str(serialized["role_id"])
    serialized["user_id"] = str(serialized["user_id"])
    if serialized.get("created_at"):
        serialized["created_at"] = serialized["created_at"].isoformat()
    if serialized.get("updated_at"):
        serialized["updated_at"] = serialized["updated_at"].isoformat()

    serialized_messages = []
    for message in serialized.get("messages", []):
        message_copy = dict(message)
        if message_copy.get("timestamp"):
            message_copy["timestamp"] = message_copy["timestamp"].isoformat()
        serialized_messages.append(message_copy)
    serialized["messages"] = serialized_messages
    return serialized


def create_chat(role_id, user_id, title="New Chat"):
    role_object_id = to_object_id(role_id)
    user_object_id = to_object_id(user_id)
    if role_object_id is None or user_object_id is None:
        return None

    chat = {
        "role_id": role_object_id,
        "user_id": user_object_id,
        "title": title,
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        return chats_collection.insert_one(chat).inserted_id
    except Exception:
        return None


def update_chat_title(chat_id, new_title, user_id=None):
    chat_object_id = to_object_id(chat_id)
    if chat_object_id is None:
        return False

    query = {"_id": chat_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    result = chats_collection.update_one(
        query,
        {"$set": {"title": new_title, "updated_at": datetime.utcnow()}},
    )
    return result.matched_count > 0


def get_chats_by_role(role_id, user_id=None):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return []

    query = {"role_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return []
        query["user_id"] = user_object_id

    chats = list(chats_collection.find(query).sort("created_at", 1))
    return [
        {
            "id": str(chat["_id"]),
            "title": chat.get("title", "New Chat"),
            "role_id": str(chat["role_id"]),
        }
        for chat in chats
    ]


def get_chat(chat_id, user_id=None):
    chat_object_id = to_object_id(chat_id)
    if chat_object_id is None:
        return None

    query = {"_id": chat_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return None
        query["user_id"] = user_object_id

    return _serialize_chat(chats_collection.find_one(query))


def add_message(chat_id, sender, text, message_type="text", data=None, user_id=None):
    chat_object_id = to_object_id(chat_id)
    if chat_object_id is None:
        return False

    message = {
        "sender": sender,
        "text": text,
        "type": message_type,
        "timestamp": datetime.utcnow(),
    }
    if data is not None:
        message["data"] = data

    query = {"_id": chat_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    result = chats_collection.update_one(
        query,
        {"$push": {"messages": message}, "$set": {"updated_at": datetime.utcnow()}},
    )
    return result.matched_count > 0


def get_last_messages(chat_id, limit=5, user_id=None):
    chat = get_chat(chat_id, user_id=user_id)
    if not chat:
        return []

    messages = chat.get("messages", [])
    return messages[-limit:]


def get_chats_by_role_paginated(role_id, user_id=None, page=1, limit=10):
    role_object_id = to_object_id(role_id)
    if role_object_id is None:
        return {"items": [], "total": 0, "page": 1, "limit": limit}

    query = {"role_id": role_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return {"items": [], "total": 0, "page": 1, "limit": limit}
        query["user_id"] = user_object_id

    safe_page = max(1, int(page))
    safe_limit = max(1, min(int(limit), 100))
    skip = (safe_page - 1) * safe_limit

    total = chats_collection.count_documents(query)
    chats = list(
        chats_collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(safe_limit)
    )

    items = [
        {
            "id": str(chat["_id"]),
            "title": chat.get("title", "New Chat"),
            "role_id": str(chat["role_id"]),
        }
        for chat in chats
    ]

    return {
        "items": items,
        "total": total,
        "page": safe_page,
        "limit": safe_limit,
    }


def get_chat_messages_paginated(chat_id, user_id=None, page=1, limit=10):
    chat = get_chat(chat_id, user_id=user_id)
    if not chat:
        return None

    safe_page = max(1, int(page))
    safe_limit = max(1, min(int(limit), 100))

    messages = chat.get("messages", [])
    total = len(messages)
    start = max(0, total - (safe_page * safe_limit))
    end = total - ((safe_page - 1) * safe_limit)
    page_items = messages[start:end]

    return {
        "items": page_items,
        "total": total,
        "page": safe_page,
        "limit": safe_limit,
    }


def delete_chat(chat_id, user_id=None):
    chat_object_id = to_object_id(chat_id)
    if chat_object_id is None:
        return False

    query = {"_id": chat_object_id}
    if user_id is not None:
        user_object_id = to_object_id(user_id)
        if user_object_id is None:
            return False
        query["user_id"] = user_object_id

    result = chats_collection.delete_one(query)
    return result.deleted_count > 0