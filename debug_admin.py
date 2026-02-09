from app import create_app, db
from app.models import User
from flask import session, g

app = create_app()

with app.app_context():
    print("=== ДИАГНОСТИКА АДМИН ПАНЕЛИ ===")
    
    # Получаем администратора
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    
    if admin:
        print(f"1. Администратор найден:")
        print(f"   Email: {admin.email}")
        print(f"   Роль в БД: {admin.role}")
        print(f"   is_admin(): {admin.is_admin()}")
        print(f"   Проверка пароля admin123: {admin.check_password('admin123')}")
        
        # Проверяем сессию
        print("\n2. Тестируем сессию и аутентификацию:")
        
        with app.test_client() as client:
            # Входим
            response = client.post('/login', data={
                'email': 'admin@resformpro.ru',
                'password': 'admin123',
                'remember': 'y'
            }, follow_redirects=True)
            
            print(f"   Статус входа: {response.status_code}")
            print(f"   Перенаправлен на: {response.request.path}")
            
            # Проверяем сессию
            with client.session_transaction() as sess:
                print(f"   ID пользователя в сессии: {sess.get('_user_id')}")
                print(f"   Сессия: {dict(sess)}")
            
            # Пробуем получить админ панель
            print("\n3. Пробуем получить /admin/:")
            response = client.get('/admin/', follow_redirects=False)
            print(f"   Статус: {response.status_code}")
            print(f"   Локация: {response.headers.get('Location', 'Нет редиректа')}")
            
            if response.status_code == 200:
                print("   ✓ Админ панель открылась!")
                print(f"   Заголовок: {'Административная панель' in response.get_data(as_text=True)}")
            elif response.status_code == 302:
                print("   ✗ Редирект на логин - проблема с аутентификацией или правами")
                
                # Пробуем следовать за редиректом
                response2 = client.get('/admin/', follow_redirects=True)
                print(f"   После редиректа: {response2.status_code}")
                print(f"   Путь: {response2.request.path}")
                
                if 'login' in response2.request.path:
                    print("   ❗ Пользователь не аутентифицирован или сессия сброшена")
            
            # Проверяем dashboard
            print("\n4. Проверяем dashboard:")
            response = client.get('/dashboard', follow_redirects=False)
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✓ Dashboard открывается")
                # Проверяем меню администратора в dashboard
                content = response.get_data(as_text=True)
                if 'Админ' in content:
                    print("   ✓ Ссылка 'Админ' найдена в навигации")
                else:
                    print("   ✗ Ссылка 'Админ' НЕ найдена в навигации")
    
    # Проверяем маршруты
    print("\n5. Проверяем зарегистрированные маршруты:")
    for rule in app.url_map.iter_rules():
        if 'admin' in rule.endpoint or 'specialist' in rule.endpoint:
            print(f"   {rule.endpoint:30} {rule.rule}")
    
    print("\n=== ДИАГНОСТИКА ЗАВЕРШЕНА ===")
