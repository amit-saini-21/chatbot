from functools import wraps

from flask import current_app, request, jsonify
import jwt
from pymongo.errors import PyMongoError
from models import user_model as db
import datetime
from utils.api_errors import json_error
#db = models.user_repo


def _jwt_error_response(message, details=None):
    return json_error(message, 401, details)


def _service_error_response(message, details=None):
    return json_error(message, 503, details)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        elif auth_header:
            token = auth_header.strip()
        
        if not token:
            return _jwt_error_response("Token is missing")
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            if user_id is None:
                return _jwt_error_response("Token payload missing user_id")

            current_user = db.get_user_by_id(user_id)

            if not current_user:
                return _jwt_error_response("User not found")
        except jwt.ExpiredSignatureError:
            current_app.logger.info("JWT expired")
            return _jwt_error_response("Token has expired")
        except jwt.InvalidTokenError as exc:
            current_app.logger.warning("Invalid JWT token: %s", exc)
            return _jwt_error_response("Token is invalid", str(exc))
        except PyMongoError as exc:
            current_app.logger.exception("MongoDB error during token validation")
            return _service_error_response("Database unavailable", str(exc))
        except Exception as exc:
            current_app.logger.exception("Unexpected token validation error")
            return _jwt_error_response("Token validation failed", str(exc))
        
        return f(current_user, *args, **kwargs)

    return decorated

def generate_jwt_token(user):
    user_id = user.get("id") or user.get("_id")
    jwt_token = jwt.encode({
        'email': user['email'],
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jwt_token