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
        
        # Создаем тестовый анализ
        test_analysis = PostureAnalysis(
            user_id=admin.id,
            front_image='/tmp/front.jpg',
            side_image='/tmp/side.jpg',
            back_image='/tmp/back.jpg',
            face_image='/tmp/face.jpg',
            overall_score=85.0,
            is_completed=True
        )
        test_analysis.set_analysis_results({
            'summary': {'score': 85, 'issues': ['Небольшая асимметрия плеч']},
            'recommendations': ['Упражнения для плеч']
        })
        db.session.add(test_analysis)
        db.session.commit()
        print("✅ Тестовый анализ создан")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
