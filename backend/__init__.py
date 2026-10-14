import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')),
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')),
    )

    # Config
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'si-pengaduan-prodi-ti-super-secret-2024')
    app.config['SESSION_COOKIE_NAME'] = 'student_session'
    app.config['REMEMBER_COOKIE_NAME'] = 'student_remember_token'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Database Config (PostgreSQL Supabase / MySQL / SQLite)
    default_sqlite = 'sqlite:///' + os.path.join(
        os.path.dirname(__file__), '..', 'database.db'
    )
    db_url = os.environ.get('DATABASE_URL', default_sqlite)
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(
        os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads'
    )
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.complaint import complaint_bp
    from .routes.profile import profile_bp
    from .routes.notification import notification_bp
    from .routes.about import about_bp
    from .routes.category import category_bp
    from .routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(settings_bp)

    # Create tables
    with app.app_context():
        db.create_all()
        from .models import seed_default_data
        seed_default_data()

    return app
