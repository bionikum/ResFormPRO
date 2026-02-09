from app import create_app

app = create_app()

print("=== ПРОВЕРКА МАРШРУТОВ ===")

with app.test_client() as client:
    # 1. Проверяем главную страницу (должен быть редирект на login)
    print("1. Главная страница /:")
    response = client.get('/', follow_redirects=False)
    print(f"   Статус: {response.status_code}, Редирект на: {response.headers.get('Location', 'Нет')}")
    
    # 2. Проверяем login
    print("\n2. Страница входа /login:")
    response = client.get('/login', follow_redirects=False)
    print(f"   Статус: {response.status_code}")
    
    # 3. Проверяем dashboard без авторизации
    print("\n3. Dashboard без авторизации:")
    response = client.get('/dashboard', follow_redirects=False)
    print(f"   Статус: {response.status_code}, Редирект на: {response.headers.get('Location', 'Нет')}")
    
    # 4. Пробуем войти
    print("\n4. Попытка входа:")
    response = client.post('/login', data={
        'email': 'admin@resformpro.ru',
        'password': 'admin123'
    }, follow_redirects=True)
    print(f"   Статус: {response.status_code}")
    print(f"   Путь после входа: {response.request.path}")
    
    # 5. Проверяем dashboard после входа
    print("\n5. Dashboard после входа:")
    response = client.get('/dashboard', follow_redirects=False)
    print(f"   Статус: {response.status_code}")
    
    # 6. Проверяем админ панель
    print("\n6. Админ панель /admin/:")
    response = client.get('/admin/', follow_redirects=False)
    print(f"   Статус: {response.status_code}")
    
    # 7. Проверяем доступные маршруты
    print("\n7. Доступные маршруты:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('main.') or rule.endpoint.startswith('auth.'):
            print(f"   {rule.endpoint:30} {rule.rule}")

print("\n=== ТЕСТ ЗАВЕРШЕН ===")
