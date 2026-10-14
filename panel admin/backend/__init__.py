import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load root .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'admin-panel-secret-key-pipl-2024')
    app.config['SESSION_COOKIE_NAME'] = 'admin_session'
    app.config['REMEMBER_COOKIE_NAME'] = 'admin_remember_token'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    from datetime import timedelta
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@127.0.0.1:3306/si_pengaduan')
    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.dashboard import dashboard_bp
    from backend.routes.complaints import complaints_bp
    from backend.routes.users import users_bp
    from backend.routes.reports import reports_bp
    from backend.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    @app.route('/')
    def root():
        from flask_login import current_user
        from flask import redirect, url_for
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Serve user attachments & avatars from root frontend/static/uploads
    from flask import send_from_directory
    root_uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'uploads'))
    admin_uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads'))

    @app.route('/static/uploads/<path:filename>')
    def serve_shared_static_uploads(filename):
        if os.path.exists(os.path.join(admin_uploads_dir, filename)):
            return send_from_directory(admin_uploads_dir, filename)
        if os.path.exists(os.path.join(root_uploads_dir, filename)):
            return send_from_directory(root_uploads_dir, filename)
        return send_from_directory(root_uploads_dir, filename)

    @app.route('/uploads/<path:filename>')
    def serve_shared_uploads(filename):
        return send_from_directory(root_uploads_dir, filename)

    return app
