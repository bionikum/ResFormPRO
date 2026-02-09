from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("=== ВСЕ ДАННЫЕ ДЛЯ АВТОРИЗАЦИИ ===")
    print("")
    
    users = User.query.order_by(db.func.lower(User.role)).all()
    
    print("📋 АДМИНИСТРАТОРЫ:")
    print("═" * 50)
    admins = [u for u in users if u.is_admin()]
    for admin in admins:
        print(f"  • {admin.email}")
        print(f"    Пароль: admin123")
        print(f"    Имя: {admin.get_full_name()}")
        print(f"    Роль: {admin.role}")
        print()
    
    print("📋 СПЕЦИАЛИСТЫ:")
    print("═" * 50)
    specialists = [u for u in users if u.is_specialist()]
    for specialist in specialists:
        print(f"  • {specialist.email}")
        print(f"    Пароль: specialist123")
        print(f"    Имя: {specialist.get_full_name()}")
        print(f"    Роль: {specialist.role}")
        print()
    
    print("📋 ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ:")
    print("═" * 50)
    regular_users = [u for u in users if u.is_user() and not u.is_admin() and not u.is_specialist()]
    for user in regular_users:
        print(f"  • {user.email}")
        print(f"    Пароль: {'password123' if 'user@resformpro.ru' in user.email else 'test123'}")
        print(f"    Имя: {user.get_full_name()}")
        print(f"    Роль: {user.role}")
        print()
    
    print("📋 ССЫЛКИ ДЛЯ ПРОВЕРКИ:")
    print("═" * 50)
    print("  • Вход: http://31.130.135.151/login")
    print("  • Регистрация: http://31.130.135.151/register")
    print("  • Панель управления: http://31.130.135.151/dashboard")
    print("  • Админ панель: http://31.130.135.151/admin/")
    print("  • Панель специалиста: http://31.130.135.151/specialist/")
    print("  • Загрузка фото: http://31.130.135.151/upload")
    print("  • Профиль: http://31.130.135.151/profile")
    print()
    print("📋 ОСОБЕННОСТИ:")
    print("═" * 50)
    print("  • Навигационная панель БЕЛАЯ с зеленой рамкой на всех страницах")
    print("  • Страница загрузки фото: окна для загрузки пока в разработке")
    print("  • Админ панель: должна открываться только для администраторов")
    print("  • Панель специалиста: должна открываться только для специалистов и администраторов")
