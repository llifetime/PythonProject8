# final_test.py
import os
import sys

print("ФИНАЛЬНАЯ ПРОВЕРКА ПРОЕКТА")
print("=" * 60)

# Добавляем текущую директорию в путь
sys.path.insert(0, os.getcwd())

# 1. Проверяем Django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'DjangoProject.settings'
    import django

    django.setup()
    print("✅ Django успешно загружен")

    from django.conf import settings

    print(f"✅ AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    print(f"✅ INSTALLED_APPS: {[app for app in settings.INSTALLED_APPS if app in ['users', 'catalog']]}")

except Exception as e:
    print(f"❌ Ошибка Django: {e}")

# 2. Проверяем модели
try:
    from users.models import User
    from catalog.models import Product

    print(f"✅ Модель User: {User}")
    print(f"✅ Модель Product: {Product}")

    # Проверка полей User
    required_fields = ['email', 'avatar', 'phone', 'country']
    for field in required_fields:
        if hasattr(User, field):
            print(f"   ✓ Поле {field} есть")
        else:
            print(f"   ✗ Поле {field} отсутствует")

except Exception as e:
    print(f"❌ Ошибка моделей: {e}")

# 3. Проверяем представления
print("\nПроверка представлений:")

# catalog/views.py
if os.path.exists('catalog/views.py'):
    with open('catalog/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ('ProductListView', 'ProductListView' in content),
            ('ProductDetailView с LoginRequiredMixin', 'ProductDetailView(LoginRequiredMixin' in content),
            ('ProductCreateView с LoginRequiredMixin', 'ProductCreateView(LoginRequiredMixin' in content),
        ]

        for name, condition in checks:
            print(f"   {'✅' if condition else '❌'} {name}")

# users/views.py
if os.path.exists('users/views.py'):
    with open('users/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ('UserRegisterView (класс)', 'class UserRegisterView' in content),
            ('form_valid переопределен', 'def form_valid' in content),
            ('send_welcome_email', 'send_welcome_email' in content),
        ]

        for name, condition in checks:
            print(f"   {'✅' if condition else '❌'} {name}")

# 4. Проверяем шаблоны
print("\nПроверка шаблонов:")
if os.path.exists('catalog/templates/catalog/includes/header.html'):
    with open('catalog/templates/catalog/includes/header.html', 'r', encoding='utf-8') as f:
        content = f.read()
        has_login = 'users:login' in content or '"/users/login/"' in content
        has_register = 'users:register' in content or '"/users/register/"' in content

        print(f"   {'✅' if has_login else '❌'} Кнопка 'Войти' ведет на users:login")
        print(f"   {'✅' if has_register else '❌'} Кнопка 'Регистрация' есть")

print("\n" + "=" * 60)
print("Запуск тестового сервера...")
print("Откройте http://127.0.0.1:8000")
print("Нажмите Ctrl+C для остановки")
print("=" * 60)

# Запускаем сервер
os.system("python manage.py runserver")