from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("=== СОЗДАНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ ===")
    
    test_users = [
        {
            'email': 'test_user@resformpro.ru',
            'password': 'test123',
            'first_name': 'Тестовый',
            'last_name': 'Пользователь',
            'role': 'user'
        },
        {
            'email': 'test_specialist@resformpro.ru',
            'password': 'specialist123',
            'first_name': 'Тестовый',
            'last_name': 'Специалист',
            'role': 'specialist'
        },
        {
            'email': 'test_admin2@resformpro.ru',
            'password': 'admin123',
            'first_name': 'Тестовый',
            'last_name': 'Администратор',
            'role': 'admin'
        }
    ]
    
    for user_data in test_users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user:
            print(f"✓ Пользователь уже существует: {user_data['email']}")
            # Обновляем пароль если нужно
            if not existing_user.check_password(user_data['password']):
                existing_user.password_hash = generate_password_hash(user_data['password'])
                print(f"  Обновлен пароль: {user_data['password']}")
            
            # Обновляем роль если нужно
            if existing_user.role != user_data['role']:
                existing_user.role = user_data['role']
                print(f"  Обновлена роль: {user_data['role']}")
        else:
            print(f"✗ Создаем пользователя: {user_data['email']}")
            user = User(
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            db.session.add(user)
    
    db.session.commit()
    
    print("\n=== ВСЕ ПОЛЬЗОВАТЕЛИ ===")
    users = User.query.all()
    for user in users:
        print(f"{user.email} - {user.role or 'user'}")
    
    print("\n=== ДАННЫЕ ДЛЯ АВТОРИЗАЦИИ ===")
    print("1. Администраторы:")
    print("   - admin@resformpro.ru / admin123")
    print("   - test_admin2@resformpro.ru / admin123")
    print("\n2. Специалисты:")
    print("   - specialist@resformpro.ru / specialist123")
    print("   - test_specialist@resformpro.ru / specialist123")
    print("\n3. Пользователи:")
    print("   - user@resformpro.ru / password123")
    print("   - test_user@resformpro.ru / test123")
