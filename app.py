from config import Config
from flask import Flask
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

if __name__ == "__main__":
    app.run(debug=True)

