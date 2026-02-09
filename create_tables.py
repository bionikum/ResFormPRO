#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/var/www/ResFormPRO')

from app import create_app, db
from app.models import User, PostureAnalysis

app = create_app()

with app.app_context():
    print("Создание таблиц базы данных...")
    
    try:
        # Создаем все таблицы
        db.create_all()
        print("✅ Таблицы успешно созданы")
        
        # Проверяем существование администратора
        admin = User.query.filter_by(email='admin@resformpro.ru').first()
        
        if not admin:
            admin = User(
                email='admin@resformpro.ru',
                full_name='Администратор',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Администратор создан: admin@resformpro.ru / admin123")
        else:
            print("ℹ️ Администратор уже существует")
            print(f"Email: {admin.email}, Role: {admin.role}")
            
        # Проверяем таблицы
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Таблицы в базе данных: {tables}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
