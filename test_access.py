from app import create_app, db
from app.models import User
from flask_login import login_user
from flask import g, session

app = create_app()

with app.app_context():
    print("=== ТЕСТ ДОСТУПА К АДМИН ПАНЕЛИ ===")
    
    # Получаем администратора
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    
    if admin:
        print(f"1. Администратор найден: {admin.email}")
        print(f"   Роль: {admin.role}")
        print(f"   is_admin(): {admin.is_admin()}")
        
        # Тестируем доступ к админ панели
        print("\n2. Тестируем доступ к админ панели:")
        
        # Создаем тестовый контекст запроса
        with app.test_client() as client:
            # Логинимся
            response = client.post('/login', data={
                'email': 'admin@resformpro.ru',
                'password': 'admin123',
                'remember': 'y'
            }, follow_redirects=False)
            
            print(f"   Статус входа: {response.status_code}")
            print(f"   Перенаправление: {response.headers.get('Location', 'Нет')}")
            
            # Пробуем получить админ панель
            if 'Location' in response.headers:
                # Следуем за редиректом
                response = client.get(response.headers['Location'], follow_redirects=True)
                print(f"   После редиректа: {response.status_code}")
            
            # Прямой доступ к админ панели
            print(f"\n3. Прямой доступ к /admin/:")
            response = client.get('/admin/', follow_redirects=False)
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 302:
                print(f"   Перенаправление на: {response.headers.get('Location', 'Нет')}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")
