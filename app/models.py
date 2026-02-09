from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    
    # Дополнительные поля
    full_name = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), nullable=True)
    
    # Поля для подписки
    is_active = db.Column(db.Boolean, nullable=True)
    subscription_type = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    
    # Временные метки
    date_created = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)  # Для обратной совместимости
    
    # Связи
    analyses = db.relationship('PostureAnalysis', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_specialist(self):
        return self.role == 'specialist'
    
    def is_user(self):
        return self.role == 'user' or self.role is None
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.full_name:
            return self.full_name
        return self.email
    
    # Свойства для совместимости
    @property
    def created_date(self):
        return self.date_created or self.created_at or datetime.utcnow()

class PostureAnalysis(db.Model):
    __tablename__ = 'posture_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Пути к фотографиям
    body_front_image = db.Column(db.String(255), nullable=True)
    body_side_image = db.Column(db.String(255), nullable=True)
    body_back_image = db.Column(db.String(255), nullable=True)
    face_front_image = db.Column(db.String(255), nullable=True)
    face_side_image = db.Column(db.String(255), nullable=True)
    
    # Результаты анализа (могут быть NULL)
    posture_score = db.Column(db.Float, nullable=True)
    symmetry_score = db.Column(db.Float, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'posture_score': self.posture_score,
            'symmetry_score': self.symmetry_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_body_front': bool(self.body_front_image),
            'has_body_side': bool(self.body_side_image),
            'has_body_back': bool(self.body_back_image),
            'has_face_front': bool(self.face_front_image),
            'has_face_side': bool(self.face_side_image)
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    
    # Связи
    creator = db.relationship('User', backref='created_recommendations')
