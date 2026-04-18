from db.mongo import users_collection
from utils.id_utils import to_object_id


def _serialize_user(user):
    if not user:
        return None
    return dict(user)


def create_user(email, password, name="", username="", age=None, tags=None):
    user = {
        "email": email,
        "password": password,
        "profile": {
            "name": name,
            "username": username,
            "age": age,
            "tags": list(tags or []),
        },
    }
    return users_collection.insert_one(user).inserted_id


def get_user_by_email(email):
    return _serialize_user(users_collection.find_one({"email": email}))


def get_user_by_id(user_id):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return None
    return _serialize_user(users_collection.find_one({"_id": user_object_id}))


def update_profile(user_id, profile_data):
    user_object_id = to_object_id(user_id)
    if user_object_id is None:
        return False

    result = users_collection.update_one({"_id": user_object_id}, {"$set": {"profile": profile_data}})
    return result.matched_count > 0