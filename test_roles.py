from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("=== ТЕСТ РОЛЕЙ И ДОСТУПА ===")
    
    # Получаем всех пользователей
    users = User.query.all()
    
    for user in users:
        print(f"\nПользователь: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Роль в БД: {user.role}")
        print(f"  is_admin(): {user.is_admin()}")
        print(f"  is_specialist(): {user.is_specialist()}")
        print(f"  is_user(): {user.is_user()}")
        print(f"  created_at: {user.created_at}")
        print(f"  date_created: {user.date_created}")
    
    print("\n=== ТЕСТ АУТЕНТИФИКАЦИИ ===")
    
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    if admin:
        print(f"Администратор {admin.email}:")
        print(f"  Пароль проверен: {admin.check_password('admin123')}")
        print(f"  Может войти в админку: {admin.is_admin()}")
        
        # Тест доступа к админ панели
        from flask_login import login_user
        from flask import session
        
        # Симулируем вход
        print(f"  ID для login_user: {admin.id}")
        print(f"  is_authenticated: {admin.is_authenticated}")
    
    print("\n=== КОНЕЦ ТЕСТА ===")
