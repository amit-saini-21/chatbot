from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from models import chat_model as chat_db

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/api/roles/<role_id>/chats', methods=['GET'])
@token_required
def get_chats_list(current_user, role_id):
    # Placeholder for fetching chats for a specific role
    try:
        # Here you would typically fetch chats from the database based on the role_id
        chat_list = chat_db.get_chats_by_role(role_id)  # Replace with actual chat fetching logic
        return jsonify({"chat_list": chat_list}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching chats", "details": str(e)}), 500
    
@chat_bp.route('/api/roles/<role_id>/chats', methods=['POST'])
@token_required
def create_chat(current_user, role_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "New Chat")

    role = chat_db.get_role(role_id)
    if not role:
        return jsonify({"error": "Role not found for this chat"}), 404
    if role.get("user_id") != current_user["_id"]:
        return jsonify({"error": "You do not have permission to create a chat for this role"}), 403
    
    try:
        chat_id = chat_db.create_chat(role_id, title)
        return jsonify({"message": "Chat created successfully", "chat_id": str(chat_id)}), 201
    except Exception as e:
        return jsonify({"error": "An error occurred while creating the chat", "details": str(e)}), 500
    
@chat_bp.route('/api/roles/<role_id>/chats/<chat_id>', methods=['PUT'])
@token_required
def update_chat_title(current_user, role_id, chat_id):
    data = request.get_json(silent=True) or {}
    new_title = data.get("title")

    role = chat_db.get_role(role_id)
    if not role:
        return jsonify({"error": "Role not found for this chat"}), 404
    if role.get("user_id") != current_user["_id"]:
        return jsonify({"error": "You do not have permission to update this chat"}), 403
    
    if not new_title:
        return jsonify({"error": "Title is required"}), 400
    try:
        chat_db.update_chat_title(chat_id, new_title)
        return jsonify({"message": "Chat title updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while updating the chat title", "details": str(e)}), 500

@chat_bp.route('/api/chats/<chat_id>', methods=['GET'])
@token_required
def get_chat_messages(current_user, chat_id):
    limit_value = request.args.get("limit", default="10")
    try:
        limit = max(1, min(int(limit_value), 100))
    except (TypeError, ValueError):
        limit = 10
    try:
        messages = chat_db.get_last_messages(chat_id, limit)
        return jsonify({"messages": messages}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching chat messages", "details": str(e)}), 500
   
@chat_bp.route('/api/chats/<chat_id>', methods=['DELETE'])
@token_required
def delete_chat(current_user, chat_id):
    chat = chat_db.get_chat(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    if chat.get("user_id") != current_user["_id"]:
        return jsonify({"error": "You do not have permission to delete this chat"}), 403
    try:
        chat_db.delete_chat(chat_id)
        return jsonify({"message": "Chat deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the chat", "details": str(e)}), 500
    