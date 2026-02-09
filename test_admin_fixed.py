from app import create_app, db
from app.models import User
from flask_login import login_user

app = create_app()

with app.app_context():
    print("=== ТЕСТ АДМИН ПАНЕЛИ ПОСЛЕ ИСПРАВЛЕНИЙ ===")
    
    # Получаем администратора
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    
    if admin:
        print(f"1. Администратор: {admin.email}, роль: {admin.role}")
        print(f"   is_admin(): {admin.is_admin()}")
        
        # Тест через test client
        with app.test_client() as client:
            # Логинимся
            response = client.post('/login', data={
                'email': 'admin@resformpro.ru',
                'password': 'admin123'
            }, follow_redirects=True)
            
            print(f"\n2. Вход в систему:")
            print(f"   Статус: {response.status_code}")
            print(f"   Редирект на: {response.request.path}")
            
            # Пробуем получить админ панель
            response = client.get('/admin/')
            print(f"\n3. Доступ к /admin/:")
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✓ Админ панель доступна!")
                # Проверяем содержимое
                if 'Административная панель' in response.get_data(as_text=True):
                    print("   ✓ Заголовок админ панели найден")
                else:
                    print("   ✗ Заголовок админ панели не найден")
            else:
                print(f"   ✗ Ошибка доступа: {response.status_code}")
                print(f"   Тело ответа: {response.get_data(as_text=True)[:500]}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")
