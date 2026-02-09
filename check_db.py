from app import create_app, db
from app.models import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
    
    # Проверяем подключение
    try:
        db.session.execute(text('SELECT 1'))
        print("✓ Подключение к БД успешно")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        exit(1)
    
    # Проверяем таблицу users
    print("\n=== ТАБЛИЦА users ===")
    try:
        users = User.query.all()
        print(f"✓ Запрос выполнен успешно")
        print(f"Всего пользователей: {len(users)}")
        
        for user in users:
            print(f"  {user.id}: {user.email} - роль: {user.role or 'не установлена'}")
        
        # Проверяем администратора
        admin = User.query.filter_by(email='admin@resformpro.ru').first()
        if admin:
            print(f"\n✓ Администратор найден: {admin.email}")
            print(f"  Роль: {admin.role}")
            print(f"  Пароль установлен: {'ДА' if admin.password_hash else 'НЕТ'}")
            if admin.password_hash:
                print(f"  Проверка пароля: {'admin123' if admin.check_password('admin123') else 'НЕВЕРНЫЙ'}")
        else:
            print("\n✗ Администратор не найден!")
            
    except Exception as e:
        print(f"✗ Ошибка при запросе пользователей: {e}")
    
    print("\n=== ПРОВЕРКА ЗАВЕРШЕНА ===")
