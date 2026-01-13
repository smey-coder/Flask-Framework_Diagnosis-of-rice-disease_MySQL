from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, csrf, login_manager, mail
from app.models.user import UserTable
from dotenv import load_dotenv
import os

def create_app(config_class: type[Config] = Config):
    load_dotenv()
    app = Flask(__name__)
    
    # Secret key from environment or fallback
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # Flask-Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id: int) -> "UserTable | None":
        return UserTable.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.role_routes import role_bp
    from app.routes.permission_routes import permission_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_bp)
    
    # Home redirect
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for("tbl_users.index"))  # Adjust blueprint name
        return redirect(url_for("auth.login"))
    
    # Create tables (dev only)
    with app.app_context():
        from app.models import UserTable, RoleTable, PermissionTable
        db.create_all()
    
    return app
