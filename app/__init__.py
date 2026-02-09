from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Конфигурация
    app.config['SECRET_KEY'] = 'resformpro-secret-key-2024-school-resource'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/resformpro_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = '/var/www/ResFormPRO/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB

    # Инициализация
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    # User loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация Blueprint
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.upload import bp as upload_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.specialist import bp as specialist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(specialist_bp)

    # Создаем необходимые директории
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('/var/www/ResFormPRO/logs', exist_ok=True)

    return app
