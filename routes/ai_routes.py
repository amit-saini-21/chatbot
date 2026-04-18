from flask import Blueprint, jsonify, request
from models import chat_model as chat_db, role_model as role_db
from services import memory_service
from utils.jwt_handler import token_required
from services.ai_service import get_ai_response

ai_bp = Blueprint("ai", __name__)

@ai_bp.route('/api/ai/chat', methods=['POST'])
@token_required
def chat_with_ai(current_user):
    data = request.get_json(silent=True) or {}

    chat_id = data.get("chat_id")
    user_message = data.get("message", "")

    if not chat_id or not user_message:
        return jsonify({"error": "Chat ID and message are required"}), 400

    try:
        # 1. Get chat
        chat = chat_db.get_chat(chat_id)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        # 2. Get role
        role_id = chat.get("role_id")
        role = role_db.get_role(role_id)
        if not role:
            return jsonify({"error": "Role not found for this chat"}), 404
        if role.get("user_id") != current_user["_id"]:
            return jsonify({"error": "You do not have permission to access this chat"}), 403
        
        # 3. Build memory context from profile + saved role memory
        memory = memory_service.build_memory_context(role, current_user)
        # 3. Save user message FIRST
        chat_db.add_message(chat_id, "user", user_message)

        # 4. Get last messages
        last_messages = chat_db.get_last_messages(chat_id, 4)

        # 5. Call AI (full context)
        ai_result = get_ai_response(
            user_message=user_message,
            role=role,
            messages=last_messages,
            memory=memory
        )

        if not ai_result:
            return jsonify({"error": "AI failed", "details": "Missing Gemini API key or Gemini request error"}), 500

        # 6. Save AI response
        chat_db.add_message(
                chat_id,
                "assistant",
                ai_result.get("data", ""),
                message_type="text",
            )

        # 7. Extract memory, with explicit save intent support
        save_requested = memory_service.should_save_memory(user_message)
        new_memories = memory_service.extract_memories(
            user_message,
            save_requested=save_requested
        )

        # 8. update memory
        memory_service.update_memory(role_id, new_memories)

        return jsonify(ai_result), 200

    except Exception as e:
        return jsonify({
            "error": "AI processing failed",
            "details": str(e)
        }), 500
