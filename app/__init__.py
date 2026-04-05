import importlib
from flask import Flask, redirect, request, session, url_for
from flask_login import current_user
from config import Config
from extensions import db, csrf, login_manager, mail
from app.models.user import UserTable
from dotenv import load_dotenv
import os
import json

def create_app(config_class: type[Config] = Config):
    load_dotenv()
    app = Flask(__name__)

    # ================= BASIC CONFIG =================
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
    app.config.from_object(config_class)

    # ================= INIT EXTENSIONS =================
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # ================= LOGIN MANAGER =================
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: int):
        return UserTable.query.get(int(user_id))

    # ================= LANGUAGE GLOBAL =================
    # ================= LANGUAGE GLOBAL =================
    @app.context_processor
    def inject_lang():
        # Load translations directly
        translations = {}
        base_path = os.path.join(app.root_path, '..', 'translations')
        
        try:
            with open(os.path.join(base_path, 'en.json'), 'r', encoding='utf-8') as f:
                translations['en'] = json.load(f)
            with open(os.path.join(base_path, 'km.json'), 'r', encoding='utf-8') as f:
                translations['km'] = json.load(f)
        except Exception as e:
            # Fallback to empty dicts
            translations = {'en': {}, 'km': {}}
        
        lang_code = session.get("lang", "en")
        lang = translations.get(lang_code, translations.get('en', {}))
        return dict(lang=lang)

    # ================= LANGUAGE SWITCH =================
    @app.route('/set_language', methods=['POST'])
    def set_language():
        lang = request.form.get('lang')

        if lang in ['en', 'km']:
            session['lang'] = lang

        # IMPORTANT: force reload
        return redirect(request.referrer or url_for('home'))

    # ================= HOME REDIRECT =================
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            if current_user.has_role("Admin"):
                return redirect(url_for("admin.dashboard"))
            elif current_user.has_role("Expert"):
                return redirect(url_for("expert.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    # ================= REGISTER BLUEPRINTS =================
    from app.routes.user_routes import user_bp
    from app.routes.role_routes import role_bp
    from app.routes.permission_routes import permission_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_route.admin_route import admin_bp
    from app.routes.user_route.user_route import user_bp as user_dashboard_bp
    from app.routes.disease_route import disease_bp
    from app.routes.symptom_routes import symptom_bp
    from app.routes.expert_route.expert_route import expert_bp
    from app.routes.rule_condition_route import rule_condition_bp
    from app.routes.prevention_route import prevention_bp
    from app.routes.treatment_route import treatment_bp
    from app.routes.audit_routes import audit_bp
    from app.routes.rule_routes import rule_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(expert_bp)
    app.register_blueprint(user_dashboard_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(symptom_bp)
    app.register_blueprint(rule_condition_bp)
    app.register_blueprint(prevention_bp)
    app.register_blueprint(treatment_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(rule_bp)

    # ================= CREATE TABLES =================
    with app.app_context():
        db.create_all()

    return app