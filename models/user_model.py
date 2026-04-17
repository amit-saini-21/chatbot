from db.mongo import users_collection
from bson import ObjectId

def create_user(email, password, name="", username="", age=None, tags=[]):
    try:
        user = {
            "email": email,
            "password": password,
            "profile": {
                "name": name,
                "username": username,
                "age": age,
                "tags": tags
            }
        }
        return users_collection.insert_one(user).inserted_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return "Error creating user"

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

def get_user_by_id(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})

def get_user_by_email(email):
    return users_collection.find_one({"email": email})


def get_user_by_id(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})


def update_profile(user_id, profile_data):
    try:
        users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile": profile_data}}
            )
    except Exception as e:
        print(f"Error updating profile: {e}")
        return "Error updating profile"