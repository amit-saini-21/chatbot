from flask import Blueprint, jsonify, request
from utils.jwt_handler import token_required
from services import role_service
from utils.api_errors import json_error

role_bp = Blueprint("role", __name__)

@role_bp.route('/api/roles', methods=['GET'])
@token_required
def get_roles(current_user):
    try:
        roles = role_service.list_roles_for_user(current_user["_id"])
        return jsonify({"roles": roles}), 200
    except Exception:
        return json_error("An error occurred while fetching roles", 500)
    

@role_bp.route('/api/roles', methods=['POST'])
@token_required
def create_role(current_user):
    data = request.get_json(silent=True) or {}
    role_type = data.get("role_type")
    config = data.get("config", {})
    if not isinstance(config, dict):
        return json_error("Config must be an object", 400)

    try:
        role_id = role_service.create_role_for_user(current_user["_id"], role_type, config)
        return jsonify({"message": "Role created successfully", "role_id": str(role_id)}), 201
    except ValueError as exc:
        return json_error(str(exc), 400)
    except FileExistsError as exc:
        return json_error(str(exc), 409)
    except Exception:
        return json_error("An error occurred while creating the role", 500)
    
@role_bp.route('/api/roles/<role_id>', methods=['PUT'])
@token_required
def update_role(current_user, role_id):
    data = request.get_json(silent=True) or {}
    config = data.get("config", {})
    if not isinstance(config, dict):
        return json_error("Config must be an object", 400)

    try:
        updated_role = role_service.update_role_for_user(current_user["_id"], role_id, config)
        return jsonify({"message": "Role updated successfully", "role": updated_role}), 200
    except ValueError as exc:
        return json_error(str(exc), 400)
    except LookupError as exc:
        return json_error(str(exc), 404)
    except PermissionError as exc:
        return json_error(str(exc), 403)
    except RuntimeError as exc:
        return json_error(str(exc), 500)


@role_bp.route('/api/roles/delete/<role_id>', methods=['DELETE'])
@token_required
def delete_role(current_user, role_id):
    try:
        role_service.delete_role_for_user(current_user["_id"], role_id)
        return jsonify({"message": "Role deleted successfully"}), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except PermissionError as exc:
        return json_error(str(exc), 403)
    except RuntimeError as exc:
        return json_error(str(exc), 500)


@role_bp.route('/api/roles/<role_id>/memory', methods=['PUT'])
@token_required
def update_role_memory(current_user, role_id):
    data = request.get_json(silent=True) or {}
    memory = data.get("memory")
    replace = bool(data.get("replace", False))

    if memory is None:
        return json_error("Memory is required", 400)

    if not isinstance(memory, (str, list)):
        return json_error("Memory must be a string or a list of strings", 400)

    if isinstance(memory, list) and any(not isinstance(item, str) for item in memory):
        return json_error("Memory list items must be strings", 400)

    try:
        updated_role = role_service.update_role_memory_for_user(
            current_user["_id"],
            role_id,
            memory,
            replace=replace,
        )
        return jsonify({"message": "Role memory updated successfully", "role": updated_role}), 200
    except LookupError as exc:
        return json_error(str(exc), 404)
    except RuntimeError as exc:
        return json_error(str(exc), 500)