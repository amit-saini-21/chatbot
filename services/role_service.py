from pymongo.errors import DuplicateKeyError

from models import role_model


ALLOWED_ROLES = ["friend", "girlfriend", "teacher", "boyfriend"]
ALLOWED_TONES = ["friendly", "caring", "romantic", "professional", "strict", "funny"]
ALLOWED_STYLES = ["casual", "formal", "playful"]
DEFAULT_ASSISTANT_CONFIG = {"tone": "friendly", "style": "casual"}


def _validate_config(config):
    config = config or {}
    tone = config.get("tone")
    style = config.get("style")

    if tone and tone not in ALLOWED_TONES:
        raise ValueError(f"Invalid tone. Allowed values are: {ALLOWED_TONES}")
    if style and style not in ALLOWED_STYLES:
        raise ValueError(f"Invalid style. Allowed values are: {ALLOWED_STYLES}")
    return config


def list_roles_for_user(user_id):
    role_model.ensure_default_role(user_id)
    return role_model.get_all_roles(user_id)


def create_role_for_user(user_id, role_type, config=None):
    if not role_type:
        raise ValueError("Role type is required")
    if role_type == "assistant":
        raise ValueError("Cannot create role with type 'assistant'")
    if role_type not in ALLOWED_ROLES:
        raise ValueError(f"Invalid role type. Allowed values are: {ALLOWED_ROLES}")

    normalized_config = _validate_config(config)

    if role_model.role_exists(user_id, role_type):
        raise FileExistsError(f"You already have a role of type '{role_type}'")

    try:
        role_id = role_model.create_role(user_id, role_type, config=normalized_config)
    except DuplicateKeyError:
        raise FileExistsError(f"You already have a role of type '{role_type}'")

    if role_id is None:
        raise RuntimeError("Unable to create role")
    return role_id


def get_role_for_user(user_id, role_id):
    role = role_model.get_role(role_id, user_id=user_id)
    if not role:
        raise LookupError("Role not found")
    return role


def update_role_for_user(user_id, role_id, config):
    normalized_config = _validate_config(config)
    role = get_role_for_user(user_id, role_id)
    if role["role_type"] == "assistant":
        raise PermissionError("Cannot update default assistant role")

    updated = role_model.update_role(role_id, config=normalized_config, user_id=user_id)
    if not updated:
        raise RuntimeError("Unable to update role")
    return role_model.get_role(role_id, user_id=user_id)


def update_role_memory_for_user(user_id, role_id, memory_items, replace=False):
    get_role_for_user(user_id, role_id)
    if replace:
        updated = role_model.update_memory(role_id, memory_items, user_id=user_id)
    else:
        updated = role_model.append_memory_entries(role_id, memory_items, user_id=user_id)

    if not updated:
        raise RuntimeError("Unable to update role memory")
    return role_model.get_role(role_id, user_id=user_id)


def delete_role_for_user(user_id, role_id):
    role = get_role_for_user(user_id, role_id)
    if role["role_type"] == "assistant":
        raise PermissionError("Cannot delete default assistant role")

    deleted = role_model.delete_role(role_id, user_id=user_id)
    if not deleted:
        raise RuntimeError("Unable to delete role")
    return True
