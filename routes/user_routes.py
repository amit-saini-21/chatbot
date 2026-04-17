from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from models import user_model as user_db

user_bp = Blueprint("user", __name__)   

@user_bp.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        email = current_user.get("email")
        user_id = current_user.get("_id")
        profile = current_user.get("profile", {})
        return jsonify({
            "email": email,
            "user_id": str(user_id),
            "profile": profile
        }), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the profile"}), 500
    
@user_bp.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json(silent=True) or {}
        profile_data = data.get("profile", {})
        name = (profile_data.get('name') or '').strip()
        username = (profile_data.get('username') or '').strip()
        age = profile_data.get('age')
        tags = profile_data.get('tags', [])
        
        if name and len(name) < 3:
            return jsonify({"error": "Name must be at least 3 characters long."}), 400
        
        profile_data = {
            "name": name,
            "username": username,
            "age": age,
            "tags": tags
        }
        
        user_db.update_profile(current_user["_id"], profile_data)
        
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while updating the profile"}), 500