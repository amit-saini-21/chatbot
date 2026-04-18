from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(value):
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return value

    try:
        return ObjectId(str(value))
    except (InvalidId, TypeError, ValueError):
        return None


def is_valid_object_id(value):
    return to_object_id(value) is not None


def object_id_equals(first, second):
    first_id = to_object_id(first)
    second_id = to_object_id(second)
    if first_id is None or second_id is None:
        return False
    return first_id == second_id
