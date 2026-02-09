from app import create_app, db
from app.models import User

app = create_app()

def init_database():
    with app.app_context():
        try:
            # Создаем таблицы
            db.create_all()
            print("✓ Таблицы базы данных созданы")
            
            # Создаем тестовых пользователей если их нет
            users_data = [
                {'email': 'admin@resformpro.ru', 'password': 'admin123', 'role': 'admin', 'subscription_type': 'pro'},
                {'email': 'specialist@resformpro.ru', 'password': 'specialist123', 'role': 'specialist', 'subscription_type': 'premium'},
                {'email': 'user@resformpro.ru', 'password': 'user123', 'role': 'user', 'subscription_type': 'free'}
            ]
            
            for user_data in users_data:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        email=user_data['email'],
                        role=user_data['role'],
                        subscription_type=user_data['subscription_type']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"✓ Создан: {user_data['email']} ({user_data['role']})")
            
            db.session.commit()
            print("✓ База данных инициализирована")
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()

init_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
