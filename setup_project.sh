#!/bin/bash
# Setup ResFormPRO Flask project

echo "Setting up ResFormPRO project..."

# Create directory structure
mkdir -p app/{models,routes,templates/{auth,includes},static/{css,js,images}}
mkdir -p uploads/{body,face} logs migrations

# Create app/__init__.py
cat > app/__init__.py << 'APPINIT'
"""
ResFormPRO - Flask Application
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
cors = CORS()

def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    if config:
        app.config.from_object(config)
    else:
        # Basic configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        
        # Database
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            db_url = 'postgresql://resformpro_user:StrongPassword123!@localhost/resformpro_db'
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Upload settings
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '../uploads')
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
        # Mail settings
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        
        # App settings
        app.config['APP_NAME'] = 'ResFormPRO'
        app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # Flask-Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create app context for initialization
    with app.app_context():
        # Import models
        from . import models
        
        # Create database tables
        db.create_all()
        
        # Create upload directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'body'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'face'), exist_ok=True)
        
        # Create initial admin user
        create_admin_user(app)
        
        # Register blueprints
        register_blueprints(app)
    
    return app


def create_admin_user(app):
    """Create default admin user"""
    from .models import User
    
    admin_email = 'admin@resformpro.ru'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            email=admin_email,
            name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('AdminPassword123!')
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f'Created admin user: {admin_email}')


def register_blueprints(app):
    """Register all blueprints"""
    try:
        from .routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError as e:
        app.logger.warning(f'Failed to register auth blueprint: {e}')
    
    try:
        from .routes.main import bp as main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        app.logger.warning(f'Failed to register main blueprint: {e}')
    
    try:
        from .routes.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        app.logger.warning(f'Failed to register api blueprint: {e}')

APPINIT

# Create models
cat > app/models/__init__.py << 'MODELSINIT'
"""
Database models
"""

from .user import User
from .analysis import AnalysisSession, PosturePhoto, PostureAnalysis, RecommendationTemplate, Recommendation

__all__ = [
    'User',
    'AnalysisSession', 
    'PosturePhoto',
    'PostureAnalysis',
    'RecommendationTemplate',
    'Recommendation'
]
MODELSINIT

# User model
cat > app/models/user.py << 'USERMODEL'
"""
User model
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # user, specialist, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    stripe_customer_id = db.Column(db.String(100))
    subscription_status = db.Column(db.String(20), default='inactive')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_specialist(self):
        return self.role == 'specialist'
    
    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
USERMODEL

# Analysis models
cat > app/models/analysis.py << 'ANALYSISMODEL'
"""
Analysis models
"""

from datetime import datetime
from app import db

class AnalysisSession(db.Model):
    __tablename__ = 'analysis_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed
    
    def __repr__(self):
        return f'<AnalysisSession {self.id}>'


class PosturePhoto(db.Model):
    __tablename__ = 'posture_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('analysis_sessions.id'), nullable=False)
    view_type = db.Column(db.String(50), nullable=False)  # front_body, side_body, back_body, front_face, side_face
    file_path = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PosturePhoto {self.filename}>'


class PostureAnalysis(db.Model):
    __tablename__ = 'posture_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('analysis_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    deviation_type = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(20))  # low, medium, high
    confidence = db.Column(db.Float)
    coordinates = db.Column(db.JSON)
    description = db.Column(db.Text)
    detected_by_ai = db.Column(db.Boolean, default=True)
    verified_by_specialist = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostureAnalysis {self.deviation_type}>'


class RecommendationTemplate(db.Model):
    __tablename__ = 'recommendation_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    deviation_type = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    for_specialist_only = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<RecommendationTemplate {self.title}>'


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('posture_analyses.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('recommendation_templates.id'), nullable=True)
    custom_text = db.Column(db.Text)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Recommendation {self.id}>'
ANALYSISMODEL

# Create routes
cat > app/routes/__init__.py << 'ROUTESINIT'
"""
Application routes
"""

from . import auth, main, api

__all__ = ['auth', 'main', 'api']
ROUTESINIT

# Main routes
cat > app/routes/main.py << 'MAINROUTES'
"""
Main routes
"""

from flask import Blueprint, render_template, jsonify, current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'app': current_app.config.get('APP_NAME', 'ResFormPRO'),
        'version': '1.0.0'
    })

@bp.route('/about')
def about():
    return render_template('about.html')
MAINROUTES

# Auth routes
cat > app/routes/auth.py << 'AUTHROUTES'
"""
Authentication routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('User with this email already exists.', 'danger')
            return render_template('auth/register.html')
        
        user = User(
            email=email,
            name=name,
            role='user',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
AUTHROUTES

# API routes
cat > app/routes/api.py << 'APIROUTES'
"""
API routes
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, AnalysisSession
from app import db

bp = Blueprint('api', __name__)

@bp.route('/user')
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'role': current_user.role,
        'subscription_status': current_user.subscription_status
    })

@bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    if request.method == 'GET':
        sessions = AnalysisSession.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': s.id,
            'created_at': s.created_at.isoformat(),
            'status': s.status,
            'notes': s.notes
        } for s in sessions])
    
    elif request.method == 'POST':
        data = request.get_json()
        session = AnalysisSession(
            user_id=current_user.id,
            notes=data.get('notes', '')
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'id': session.id,
            'message': 'Analysis session created'
        })

@bp.route('/test')
def test():
    return jsonify({'message': 'API is working'})
APIROUTES

# Create templates
# Base template
cat > app/templates/base.html << 'BASETEMPLATE'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ResFormPRO{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 20px; }
        .navbar { margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">ResFormPRO</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('main.index') }}">Home</a>
                <a class="nav-link" href="{{ url_for('main.about') }}">About</a>
                {% if current_user.is_authenticated %}
                    <a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a>
                    <a class="nav-link" href="{{ url_for('auth.profile') }}">Profile</a>
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
BASETEMPLATE

# Index template
cat > app/templates/index.html << 'INDEXTEMPLATE'
{% extends "base.html" %}

{% block title %}Home - ResFormPRO{% endblock %}

{% block content %}
<div class="jumbotron bg-light p-5 rounded">
    <h1 class="display-4">Welcome to ResFormPRO!</h1>
    <p class="lead">Professional posture analysis and personalized recommendations.</p>
    <hr class="my-4">
    <p>Upload photos for posture analysis and get personalized recommendations from specialists.</p>
    
    {% if not current_user.is_authenticated %}
        <a class="btn btn-primary btn-lg" href="{{ url_for('auth.register') }}" role="button">
            Get Started
        </a>
        <a class="btn btn-outline-primary btn-lg" href="{{ url_for('auth.login') }}" role="button">
            Login
        </a>
    {% else %}
        <a class="btn btn-primary btn-lg" href="{{ url_for('main.dashboard') }}" role="button">
            Go to Dashboard
        </a>
    {% endif %}
</div>
{% endblock %}
INDEXTEMPLATE

# Login template
cat > app/templates/auth/login.html << 'LOGINTEMPLATE'
{% extends "base.html" %}

{% block title %}Login - ResFormPRO{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">Login</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                
                <div class="mt-3 text-center">
                    <p>Don't have an account? <a href="{{ url_for('auth.register') }}">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
LOGINTEMPLATE

# Register template
cat > app/templates/auth/register.html << 'REGTEMPLATE'
{% extends "base.html" %}

{% block title %}Register - ResFormPRO{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">Register</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Full Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                </form>
                
                <div class="mt-3 text-center">
                    <p>Already have an account? <a href="{{ url_for('auth.login') }}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
REGTEMPLATE

# Dashboard template
cat > app/templates/dashboard.html << 'DASHTEMPLATE'
{% extends "base.html" %}

{% block title %}Dashboard - ResFormPRO{% endblock %}

{% block content %}
<h1 class="mb-4">Dashboard</h1>
<p class="lead">Welcome back, {{ current_user.name }}!</p>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h2 class="card-title">0</h2>
                <p class="card-text">Analysis Sessions</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h2 class="card-title">0</h2>
                <p class="card-text">Recommendations</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h2 class="card-title">0%</h2>
                <p class="card-text">Progress</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h2 class="card-title">{{ current_user.role|title }}</h2>
                <p class="card-text">Account Type</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="#" class="btn btn-primary mb-2">
                    <i class="fas fa-plus"></i> New Analysis
                </a>
                <a href="#" class="btn btn-outline-primary mb-2">
                    <i class="fas fa-history"></i> View History
                </a>
                <a href="#" class="btn btn-outline-primary mb-2">
                    <i class="fas fa-list-check"></i> Recommendations
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
DASHTEMPLATE

# About template
cat > app/templates/about.html << 'ABOUTTEMPLATE'
{% extends "base.html" %}

{% block title %}About - ResFormPRO{% endblock %}

{% block content %}
<h1>About ResFormPRO</h1>

<div class="card mt-4">
    <div class="card-body">
        <h5 class="card-title">Our Mission</h5>
        <p class="card-text">
            ResFormPRO is a professional posture analysis platform that combines 
            artificial intelligence with expert kinesiology knowledge to help 
            individuals improve their physical health and posture.
        </p>
    </div>
</div>

<div class="card mt-3">
    <div class="card-body">
        <h5 class="card-title">How It Works</h5>
        <ol>
            <li>Upload photos from different angles (front, side, back)</li>
            <li>AI analyzes your posture and detects deviations</li>
            <li>Kinesiologists review and provide personalized recommendations</li>
            <li>Track your progress over time</li>
        </ol>
    </div>
</div>
ABOUTTEMPLATE

# Create run.py
cat > run.py << 'RUNPY'
#!/usr/bin/env python3
"""
Application entry point
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting ResFormPRO on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
RUNPY

chmod +x run.py

# Create .env file
cat > .env << 'ENVFILE'
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://resformpro_user:StrongPassword123!@localhost/resformpro_db
UPLOAD_FOLDER=./uploads
DEBUG=True
ENVFILE

echo "Project setup completed!"
