from db.mongo import roles_collection
from bson import ObjectId


def _to_object_id(value):
    return value if isinstance(value, ObjectId) else ObjectId(value)


def _serialize_role(role):
    role["_id"] = str(role["_id"])
    role["user_id"] = str(role["user_id"])
    return role


def create_role(user_id, role_type, config):
    try:
        role = {
            "user_id": _to_object_id(user_id),
            "role_type": role_type,
            "config": config,
            "memory": []
        }
        return roles_collection.insert_one(role).inserted_id
    except Exception as e:
       # print(f"Error creating role: {e}")
        return "Error creating role"


def ensure_default_role(user_id):
    existing_role = roles_collection.find_one({"user_id": _to_object_id(user_id), "role_type": "assistant"})
    if not existing_role:
        try:
            create_role(user_id, "assistant", {"tone": "friendly", "style": "casual"})
        except Exception as e:
            # print(f"Error ensuring default role: {e}")
            pass

def update_memory(role_id, memory):
    roles_collection.update_one(
        {"_id": _to_object_id(role_id)},
        {"$set": {"memory": memory}}
    )
    return 


def get_role_appearance(role):
    if not role:
        return None
    config = role.get("config", {}) or {}
    return role.get("appearance") or config.get("appearance")


def set_role_appearance(role_id, appearance):
    if not appearance:
        return

    roles_collection.update_one(
        {"_id": _to_object_id(role_id)},
        {"$set": {"appearance": appearance, "config.appearance": appearance}},
    )


def get_all_roles(user_id):
    roles = list(roles_collection.find({"user_id": _to_object_id(user_id)}))
    return [_serialize_role(role) for role in roles]


def get_role(role_id):
    role = roles_collection.find_one({"_id": _to_object_id(role_id)})
    return _serialize_role(role) if role else None


def update_role(role_id, config):
    try:
        roles_collection.update_one(
            {"_id": _to_object_id(role_id)},
            {"$set": {"config": config}}
        )
    except Exception as e:
        # print(f"Error updating role: {e}")
        return "Error updating role"
    
def delete_role(role_id):
    try:
        roles_collection.delete_one({"_id": _to_object_id(role_id)})
    except Exception as e:
        #print(f"Error deleting role: {e}")
        return "Error deleting role"

def add_memory(role_id, text):
    roles_collection.update_one(
        {"_id": _to_object_id(role_id)},
        {
            "$push": {
                "memory": {
                    "$each": [text],
                    "$slice": -20   # max 20 memory
                }
            }
        }
    )
