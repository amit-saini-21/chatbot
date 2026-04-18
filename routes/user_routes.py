from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from models import user_model as user_db
from utils.api_errors import json_error

user_bp = Blueprint("user", __name__)   

@user_bp.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    email = current_user.get("email")
    user_id = current_user.get("_id")
    profile = current_user.get("profile", {})
    return jsonify({
        "email": email,
        "user_id": str(user_id),
        "profile": profile,
    }), 200
    
@user_bp.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json(silent=True) or {}
    profile_data = data.get("profile", {})

    if not isinstance(profile_data, dict):
        return json_error("Profile must be an object", 400)

    name = (profile_data.get("name") or "").strip()
    username = (profile_data.get("username") or "").strip()
    age = profile_data.get("age")
    tags = profile_data.get("tags", [])

    if name and len(name) < 3:
        return json_error("Name must be at least 3 characters long.", 400)

    if age is not None and not isinstance(age, int):
        return json_error("Age must be an integer", 400)

    if not isinstance(tags, list):
        return json_error("Tags must be a list", 400)

    normalized_profile = {
        "name": name,
        "username": username,
        "age": age,
        "tags": tags,
    }

    updated = user_db.update_profile(current_user["_id"], normalized_profile)
    if not updated:
        return json_error("Profile could not be updated", 404)

    return jsonify({"message": "Profile updated successfully"}), 200