from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from models import role_model as role_db

role_bp = Blueprint("role", __name__)

@role_bp.route('/api/roles', methods=['GET'])
@token_required
def get_roles(current_user):
    try:
        role_db.ensure_default_role(current_user["_id"])
        roles = role_db.get_all_roles(current_user["_id"])
        return jsonify({"roles": roles}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching roles", "details": str(e)}), 500
    

@role_bp.route('/api/roles', methods=['POST'])
@token_required
def create_role(current_user):
    ALLOWED_ROLES = ["friend", "girlfriend", "teacher", "boyfriend"]
    ALLOWED_TONES = [
    "friendly",
    "caring",
    "romantic",
    "professional",
    "strict",
    "funny"
    ]
    ALLOWED_STYLES = [
    "casual",
    "formal",
    "playful"
    ]
    data = request.get_json(silent=True) or {}
    role_type = data.get("role_type")
    config = data.get("config", {})
    
    
    if not role_type:
        return jsonify({"error": "Role type is required"}), 400
    
    if role_type == "assistant":
        return jsonify({"error": "Cannot create role with type 'assistant'"}), 400
    
    if config.get("tone") and config["tone"] not in ALLOWED_TONES:
        return jsonify({"error": f"Invalid tone. Allowed values are: {ALLOWED_TONES}"}), 400
    
    if config.get("style") and config["style"] not in ALLOWED_STYLES:
        return jsonify({"error": f"Invalid style. Allowed values are: {ALLOWED_STYLES}"}), 400
    
    if role_type not in ALLOWED_ROLES:
        return jsonify({"error": f"Invalid role type. Allowed values are: {ALLOWED_ROLES}"}), 400
    if role_db.role_exists(current_user["_id"], role_type):
        return jsonify({"error": f"You already have a role of type '{role_type}'"}), 400
    try:
        role_id = role_db.create_role(current_user["_id"], role_type, config)
        return jsonify({"message": "Role created successfully", "role_id": str(role_id)}), 201
    except Exception as e:
        return jsonify({"error": "An error occurred while creating the role"}), 500
    
@role_bp.route('/api/roles/<role_id>', methods=['PUT'])
@token_required
def update_role(current_user, role_id):
    data = request.get_json(silent=True) or {}
    config = data.get("config", {})
    
    if not config:
        return jsonify({"error": "Config is required for updating the role"}), 400
    
    role = role_db.get_role(role_id)

    if not role:
        return jsonify({"error": "Role not found"}), 404
    
    if role["role_type"] == "assistant":
        return jsonify({"error": "Cannot update default assistant role"}), 400
    
    if str(role["user_id"]) != str(current_user["_id"]):
        return jsonify({"error": "Unauthorized to update this role"}), 403
    
    try:
        role_db.update_role(role_id, config)
        return jsonify({"message": "Role updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while updating the role"}), 500


@role_bp.route('/api/roles/delete/<role_id>', methods=['DELETE'])
@token_required
def delete_role(current_user, role_id):
    role = role_db.get_role(role_id)

    if not role:
        return jsonify({"error": "Role not found"}), 404
    
    if role["role_type"] == "assistant":
        return jsonify({"error": "Cannot delete default assistant role"}), 400
    
    if str(role["user_id"]) != str(current_user["_id"]):
        return jsonify({"error": "Unauthorized to delete this role"}), 403
    
    try:
        role_db.delete_role(role_id)
        return jsonify({"message": "Role deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the role"}), 500