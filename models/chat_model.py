from db.mongo import chats_collection
from bson import ObjectId
from datetime import datetime

def create_chat(role_id, title="New Chat"):
    try:
        chat = {
            "role_id": ObjectId(role_id),
            "title": title,
            "messages": [],
            "created_at": datetime.utcnow()
        }
        return chats_collection.insert_one(chat).inserted_id
    except Exception as e:
        #print(f"Error creating chat: {e}")
        return "Error creating chat"
    
def update_chat_title(chat_id, new_title):
    try:
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"title": new_title}}
        )
    except Exception as e:
       # print(f"Error updating chat title: {e}")
        return "Error updating chat title"
def get_chats_by_role(role_id):
    try:
        chats = list(chats_collection.find({"role_id": ObjectId(role_id)}))
        chat_list =[]
        for chat in chats:
            chat_list.append({
                "id": str(chat["_id"]),
                "title": chat["title"]
            })
        return chat_list
    except Exception as e:
        return "Error fetching chats"


def get_chat(chat_id):
    return chats_collection.find_one({"_id": ObjectId(chat_id)})


def add_message(chat_id, sender, text, message_type="text", data=None):
    message = {
        "sender": sender,
        "text": text,
        "type": message_type,
        "timestamp": datetime.utcnow()
    }
    if data is not None:
        message["data"] = data

    try:
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": message}}
        )
    except Exception as e:
       # print(f"Error adding message: {e}")
        return "Error adding message"

def get_last_messages(chat_id, limit=5):
    chat = get_chat(chat_id)
    if not chat:
        return []
    messages = chat.get("messages", [])
    return messages[-limit:]