from flask import Blueprint, jsonify
from db.mongo import get_client

other_bp = Blueprint("other", __name__)

@other_bp.route('/api/health', methods=['GET'])
def health_check():
    db_status = "unknown"
    try:
        get_client().admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "degraded"

    return jsonify({"status": "ok", "database": db_status, "message": "API is healthy"}), 200

