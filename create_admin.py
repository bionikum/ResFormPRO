from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("=== СОЗДАНИЕ/ПРОВЕРКА АДМИНИСТРАТОРА ===")
    
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    
    if admin:
        print(f"✓ Администратор уже существует: {admin.email}")
        print(f"  Текущая роль: {admin.role}")
        
        # Обновляем роль если нужно
        if admin.role != 'admin':
            admin.role = 'admin'
            print("  Обновляю роль на 'admin'")
        
        # Обновляем пароль если нужно
        if not admin.check_password('admin123'):
            admin.password_hash = generate_password_hash('admin123')
            print("  Устанавливаю пароль: admin123")
        
        db.session.commit()
        print("✓ Администратор обновлен")
        
    else:
        print("✗ Администратор не найден, создаю...")
        
        admin = User(
            email='admin@resformpro.ru',
            password_hash=generate_password_hash('admin123'),
            first_name='Администратор',
            last_name='Системы',
            role='admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✓ Администратор создан: admin@resformpro.ru / admin123")
    
    print("\n=== ТЕКУЩИЕ ПОЛЬЗОВАТЕЛИ ===")
    users = User.query.all()
    for user in users:
        print(f"  {user.id}: {user.email} - {user.role or 'user'}")
