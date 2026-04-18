from models import chat_model, role_model
from utils.id_utils import to_object_id


def _load_owned_role(user_id, role_id):
    role = role_model.get_role(role_id, user_id=user_id)
    if not role:
        raise LookupError("Role not found")
    return role


def list_role_chats(user_id, role_id):
    _load_owned_role(user_id, role_id)
    return chat_model.get_chats_by_role(role_id, user_id=user_id)


def list_role_chats_paginated(user_id, role_id, page=1, limit=10):
    _load_owned_role(user_id, role_id)
    return chat_model.get_chats_by_role_paginated(role_id, user_id=user_id, page=page, limit=limit)


def create_chat_for_role(user_id, role_id, title="New Chat"):
    _load_owned_role(user_id, role_id)
    chat_id = chat_model.create_chat(role_id, user_id, title)
    if chat_id is None:
        raise RuntimeError("Unable to create chat")
    return chat_id


def update_chat_title_for_user(user_id, role_id, chat_id, title):
    role = _load_owned_role(user_id, role_id)
    chat = chat_model.get_chat(chat_id, user_id=user_id)
    if not chat:
        raise LookupError("Chat not found")
    if to_object_id(chat.get("role_id")) != to_object_id(role.get("_id")):
        raise PermissionError("Chat does not belong to this role")

    updated = chat_model.update_chat_title(chat_id, title, user_id=user_id)
    if not updated:
        raise RuntimeError("Unable to update chat title")
    return True


def get_chat_for_user(user_id, chat_id):
    chat = chat_model.get_chat(chat_id, user_id=user_id)
    if not chat:
        raise LookupError("Chat not found")
    return chat


def get_chat_messages_for_user(user_id, chat_id, limit=10):
    _ = get_chat_for_user(user_id, chat_id)
    return chat_model.get_last_messages(chat_id, limit=limit, user_id=user_id)


def get_chat_messages_for_user_paginated(user_id, chat_id, page=1, limit=10):
    _ = get_chat_for_user(user_id, chat_id)
    result = chat_model.get_chat_messages_paginated(chat_id, user_id=user_id, page=page, limit=limit)
    if result is None:
        raise LookupError("Chat not found")
    return result


def delete_chat_for_user(user_id, chat_id):
    chat = chat_model.get_chat(chat_id, user_id=user_id)
    if not chat:
        raise LookupError("Chat not found")

    deleted = chat_model.delete_chat(chat_id, user_id=user_id)
    if not deleted:
        raise RuntimeError("Unable to delete chat")
    return True
