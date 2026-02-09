from app import create_app
from app.models import User

app = create_app()

print("=== ФИНАЛЬНЫЙ ТЕСТ АДМИН ПАНЕЛИ ===")

with app.test_client() as client:
    # 1. Входим как администратор
    print("1. Вход администратора...")
    response = client.post('/login', data={
        'email': 'admin@resformpro.ru',
        'password': 'admin123'
    }, follow_redirects=True)
    
    print(f"   Статус: {response.status_code}")
    print(f"   Путь: {response.request.path}")
    
    # 2. Проверяем dashboard
    print("\n2. Проверяем dashboard:")
    response = client.get('/dashboard')
    print(f"   Статус: {response.status_code}")
    
    # 3. Проверяем админ панель
    print("\n3. Проверяем админ панель:")
    response = client.get('/admin/')
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        content = response.get_data(as_text=True)
        if 'Административная панель' in content:
            print("   ✓ Админ панель работает!")
        else:
            print("   ✗ Заголовок не найден")
    else:
        print(f"   ✗ Ошибка: {response.status_code}")
        print(f"   Тело: {response.get_data(as_text=True)[:500]}")
    
    # 4. Проверяем управление пользователями
    print("\n4. Проверяем управление пользователями:")
    response = client.get('/admin/users')
    print(f"   Статус: {response.status_code}")
    
    # 5. Выходим и проверяем как обычный пользователь
    print("\n5. Выходим и проверяем как пользователь...")
    client.get('/logout')
    
    response = client.post('/login', data={
        'email': 'test_user@resformpro.ru',
        'password': 'test123'
    }, follow_redirects=True)
    
    print("\n6. Пробуем получить админ панель как пользователь:")
    response = client.get('/admin/')
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 302 and 'dashboard' in response.headers.get('Location', ''):
        print("   ✓ Доступ запрещен (как и должно быть)")
    else:
        print("   ✗ Неправильное поведение")

print("\n=== ТЕСТ ЗАВЕРШЕН ===")
