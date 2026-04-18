from flask import Blueprint, jsonify, request
from utils.hash import generate_password_hash, check_password_hash
import re
from utils import jwt_handler
from models import user_model as auth_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/api/auth/register', methods = ['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not email or not name or not password or not confirm_password:
        return jsonify({"error":"Name, Email and Password are required"}), 400
    
    if len(name)<3:
        return jsonify({"error": "Name must be atleast 3 characters long."}), 400
    
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    
    if not re.fullmatch(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$", password):
        return jsonify({"error": "Password must be at least 8 characters long and contain a mix of letters and numbers"}), 400

    if password != confirm_password:
        return jsonify({"error" : "Password not match with confirm password."}), 400
    
    existing_email = auth_db.get_user_by_email(email)
    if existing_email:
        return jsonify({"error": "An account with this email already exists"}), 400

    username = email.split('@')[0]
    
    hash_password = generate_password_hash(password)

    try:
        auth_db.create_user(email, hash_password, name, username)
        return jsonify({"message": "User registered successfully"}), 201
    
    except Exception as e:
        # print(f"Error registering user: {e}")
        return jsonify({"error": "An error occurred while registering the user"}), 500
    

@auth_bp.route('/api/auth/login', methods = ['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({"error": "Email and Password are required"}), 400
    
    user = None
    try:
        user = auth_db.get_user_by_email(email)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the user data"}), 500
    
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    if not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    jwt_token = jwt_handler.generate_jwt_token(user)

    return jsonify({"message": "Login successful", "token": jwt_token}), 200

