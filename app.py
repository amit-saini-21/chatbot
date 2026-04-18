from config import Config
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from db.mongo import initialize_database
from routes.auth_routes import auth_bp
from routes.other_routes import other_bp
from routes.user_routes import user_bp
from routes.role_routes import role_bp
from routes.chat_routes import chat_bp
from routes.ai_routes import ai_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(other_bp)
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(ai_bp)


@app.errorhandler(HTTPException)
def handle_http_exception(exc):
    response = jsonify({"error": exc.description or "Request failed"})
    response.status_code = exc.code or 500
    return response


@app.errorhandler(Exception)
def handle_unexpected_exception(exc):
    app.logger.exception("Unhandled exception: %s", exc)
    response = jsonify({"error": "An internal server error occurred"})
    response.status_code = 500
    return response


initialize_database()

if __name__ == "__main__":
    app.run(debug=False)

