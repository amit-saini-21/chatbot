from flask import Blueprint, jsonify

other_bp = Blueprint("other", __name__)

@other_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API is healthy"}), 200

