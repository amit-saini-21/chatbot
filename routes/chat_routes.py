from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from services import chat_service
from utils.api_errors import json_error

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/api/roles/<role_id>/chats', methods=['GET'])
@token_required
def get_chats_list(current_user, role_id):
    page_value = request.args.get("page", default="1")
    limit_value = request.args.get("limit", default="10")

    try:
        page = max(1, int(page_value))
    except (TypeError, ValueError):
        page = 1

    try:
        limit = max(1, min(int(limit_value), 100))
    except (TypeError, ValueError):
        limit = 10

    try:
        paged = chat_service.list_role_chats_paginated(current_user["_id"], role_id, page=page, limit=limit)
        return jsonify({
            "chat_list": paged["items"],
            "pagination": {
                "page": paged["page"],
                "limit": paged["limit"],
                "total": paged["total"],
            }
        }), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except Exception:
        return json_error("An error occurred while fetching chats", 500)
    
@chat_bp.route('/api/roles/<role_id>/chats', methods=['POST'])
@token_required
def create_chat(current_user, role_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "New Chat")

    if not isinstance(title, str) or not title.strip():
        return json_error("Title must be a non-empty string", 400)

    try:
        chat_id = chat_service.create_chat_for_role(current_user["_id"], role_id, title)
        return jsonify({"message": "Chat created successfully", "chat_id": str(chat_id)}), 201
    except LookupError as exc:
        return json_error(str(exc), 404)
    except PermissionError as exc:
        return json_error(str(exc), 403)
    except RuntimeError as exc:
        return json_error(str(exc), 500)
    
@chat_bp.route('/api/roles/<role_id>/chats/<chat_id>', methods=['PUT'])
@token_required
def update_chat_title(current_user, role_id, chat_id):
    data = request.get_json(silent=True) or {}
    new_title = data.get("title")

    if not isinstance(new_title, str) or not new_title.strip():
        return json_error("Title is required", 400)
    try:
        chat_service.update_chat_title_for_user(current_user["_id"], role_id, chat_id, new_title)
        return jsonify({"message": "Chat title updated successfully"}), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except PermissionError as exc:
        return json_error(str(exc), 403)
    except RuntimeError as exc:
        return json_error(str(exc), 500)

@chat_bp.route('/api/chats/<chat_id>', methods=['GET'])
@token_required
def get_chat_messages(current_user, chat_id):
    page_value = request.args.get("page", default="1")
    limit_value = request.args.get("limit", default="10")

    try:
        page = max(1, int(page_value))
    except (TypeError, ValueError):
        page = 1

    try:
        limit = max(1, min(int(limit_value), 100))
    except (TypeError, ValueError):
        limit = 10

    try:
        paged = chat_service.get_chat_messages_for_user_paginated(
            current_user["_id"],
            chat_id,
            page=page,
            limit=limit,
        )
        return jsonify({
            "messages": paged["items"],
            "pagination": {
                "page": paged["page"],
                "limit": paged["limit"],
                "total": paged["total"],
            }
        }), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except Exception:
        return json_error("An error occurred while fetching chat messages", 500)
   
@chat_bp.route('/api/chats/<chat_id>', methods=['DELETE'])
@token_required
def delete_chat(current_user, chat_id):
    try:
        chat_service.delete_chat_for_user(current_user["_id"], chat_id)
        return jsonify({"message": "Chat deleted successfully"}), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except RuntimeError as exc:
        return json_error(str(exc), 500)
    