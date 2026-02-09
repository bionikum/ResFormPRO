from app import create_app, db
from app.models import User

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Создаем таблицы если их нет...")
        db.create_all()
        
        # Проверяем наличие администратора
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
        
        print("База данных инициализирована")

if __name__ == '__main__':
    init_database()
