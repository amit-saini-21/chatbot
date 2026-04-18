from flask import current_app, has_app_context, jsonify


def json_error(message, status_code=400, details=None):
    payload = {"error": message}
    if details is not None and has_app_context() and current_app.debug:
        payload["details"] = details
    return jsonify(payload), status_code


def internal_error(details=None):
    return json_error("An internal server error occurred", 500, details)
