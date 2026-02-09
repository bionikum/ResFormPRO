import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Временно убираем создание администратора чтобы не вызывать ошибку
    print("Проверяем структуру базы данных...")
    
    # Получаем текущие столбцы таблицы users
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    
    columns = inspector.get_columns('users')
    print("Столбцы таблицы users:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Добавляем недостающие столбцы если их нет
    with db.engine.connect() as conn:
        # Проверяем наличие date_created
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='date_created'
        """))
        
        if not result.fetchone():
            print("Добавляем столбец date_created...")
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN date_created TIMESTAMP DEFAULT NOW()"))
                print("Столбец date_created добавлен")
            except Exception as e:
                print(f"Ошибка при добавлении date_created: {e}")
        
        # Проверяем наличие last_login
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='last_login'
        """))
        
        if not result.fetchone():
            print("Добавляем столбец last_login...")
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
                print("Столбец last_login добавлен")
            except Exception as e:
                print(f"Ошибка при добавлении last_login: {e}")
        
        conn.commit()
    
    print("Структура базы данных обновлена")
    
    # Теперь создаем администратора если его нет
    admin = User.query.filter_by(email='admin@resformpro.ru').first()
    if not admin:
        print("Создаем администратора...")
        admin = User(
            email='admin@resformpro.ru',
            role='admin',
            subscription_type='premium'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Администратор создан: admin@resformpro.ru / admin123')
    else:
        print('Администратор уже существует')
