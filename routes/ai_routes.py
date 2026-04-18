from flask import Blueprint, jsonify, request
from models import chat_model as chat_db, role_model as role_db
from services import memory_service
from utils.jwt_handler import token_required
from services.ai_service import get_ai_response
from utils.api_errors import json_error

ai_bp = Blueprint("ai", __name__)

@ai_bp.route('/api/ai/chat', methods=['POST'])
@token_required
def chat_with_ai(current_user):
    data = request.get_json(silent=True) or {}

    chat_id = data.get("chat_id")
    user_message = data.get("message", "")

    if not chat_id or not isinstance(user_message, str) or not user_message.strip():
        return json_error("Chat ID and message are required", 400)

    try:
        chat = chat_db.get_chat(chat_id, user_id=current_user["_id"])
        if not chat:
            return json_error("Chat not found", 404)

        role_id = chat.get("role_id")
        role = role_db.get_role(role_id, user_id=current_user["_id"])
        if not role:
            return json_error("Role not found for this chat", 404)

        memory = memory_service.build_memory_context(role, current_user)
        if not chat_db.add_message(chat_id, "user", user_message, user_id=current_user["_id"]):
            return json_error("Unable to store user message", 500)

        last_messages = chat_db.get_last_messages(chat_id, 5, user_id=current_user["_id"])
        ai_result = get_ai_response(
            user_message=user_message,
            role=role,
            messages=last_messages,
            memory=memory,
        )

        if not chat_db.add_message(
            chat_id,
            "assistant",
            ai_result.get("data", ""),
            message_type="text",
            user_id=current_user["_id"],
        ):
            return json_error("Unable to store assistant response", 500)

        save_requested = memory_service.should_save_memory(user_message)
        new_memories = memory_service.extract_memories(user_message, save_requested=save_requested)
        memory_service.update_memory(role_id, new_memories, user_id=current_user["_id"])

        return jsonify(ai_result), 200
    except Exception:
        return json_error("AI processing failed", 500)
