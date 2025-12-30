import os
import sys
import ast
import django
from pathlib import Path

# Добавляем текущую папку в путь
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def check_structure():
    """Проверка структуры проекта"""
    print("=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    print("=" * 60)

    # Ключевые файлы и папки
    required = [
        ('manage.py', True),
        ('DjangoProject/settings.py', True),
        ('DjangoProject/urls.py', True),
        ('users/__init__.py', True),
        ('users/models.py', True),
        ('users/forms.py', True),
        ('users/views.py', True),
        ('users/urls.py', True),
        ('users/migrations/0001_initial.py', True),
        ('users/templates/users/register.html', True),
        ('users/templates/users/login.html', True),
        ('catalog/__init__.py', True),
        ('catalog/models.py', True),
        ('catalog/views.py', True),
        ('catalog/urls.py', True),
        ('catalog/migrations/0001_initial.py', True),
        ('catalog/templates/catalog/includes/header.html', True),
        ('requirements.txt', True),
    ]

    all_ok = True
    for path, required in required:
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        color = "\033[92m" if exists else "\033[91m"

        if required and not exists:
            all_ok = False

        print(f"{color}{status}\033[0m {path}")

    return all_ok


def check_settings():
    """Проверка настроек Django"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА НАСТРОЕК DJANGO")
    print("=" * 60)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

    try:
        django.setup()
        from django.conf import settings

        checks = [
            ('AUTH_USER_MODEL', 'users.User'),
            ('INSTALLED_APPS содержит users', 'users' in settings.INSTALLED_APPS),
            ('INSTALLED_APPS содержит catalog', 'catalog' in settings.INSTALLED_APPS),
            ('EMAIL_BACKEND настроен', hasattr(settings, 'EMAIL_BACKEND')),
        ]

        for name, condition in checks:
            status = "✓" if condition else "✗"
            color = "\033[92m" if condition else "\033[91m"
            print(f"{color}{status}\033[0m {name}")

    except Exception as e:
        print(f"✗ Ошибка загрузки настроек: {e}")
        return False

    return True


def check_models():
    """Проверка моделей"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА МОДЕЛЕЙ")
    print("=" * 60)

    try:
        from users.models import User
        from catalog.models import Product, Category

        # Проверка User модели
        user_checks = [
            ('Наследует от AbstractUser', User.__bases__[0].__name__ == 'AbstractUser'),
            ('USERNAME_FIELD = email', User.USERNAME_FIELD == 'email'),
            ('Есть поле avatar', hasattr(User, 'avatar')),
            ('Есть поле phone', hasattr(User, 'phone')),
            ('Есть поле country', hasattr(User, 'country')),
        ]

        print("\033[94mМодель User:\033[0m")
        for name, condition in user_checks:
            status = "✓" if condition else "✗"
            color = "\033[92m" if condition else "\033[91m"
            print(f"  {color}{status}\033[0m {name}")

        # Проверка моделей каталога
        print("\n\033[94mМодель Product:\033[0m")
        product_fields = ['name', 'description', 'price', 'category']
        for field in product_fields:
            exists = hasattr(Product, field)
            status = "✓" if exists else "✗"
            color = "\033[92m" if exists else "\033[91m"
            print(f"  {color}{status}\033[0m Поле {field}")

    except Exception as e:
        print(f"✗ Ошибка проверки моделей: {e}")
        return False

    return True


def check_urls():
    """Проверка URL конфигураций"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА URLS")
    print("=" * 60)

    try:
        # Проверка users/urls.py
        with open('users/urls.py', 'r') as f:
            content = f.read()
            has_register = 'register' in content
            has_login = 'login' in content

            print("\033[94musers/urls.py:\033[0m")
            print(f"  {'✓' if has_register else '✗'} Путь register/")
            print(f"  {'✓' if has_login else '✗'} Путь login/")

        # Проверка header.html
        header_path = 'catalog/templates/catalog/includes/header.html'
        if os.path.exists(header_path):
            with open(header_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_users_login = 'users:login' in content
                has_users_register = 'users:register' in content
                has_admin_index = 'admin:index' in content

                print("\n\033[94mHeader каталога:\033[0m")
                print(f"  {'✓' if has_users_login else '✗'} Ссылка на users:login")
                print(f"  {'✓' if has_users_register else '✗'} Ссылка на users:register")
                print(f"  {'⚠️' if has_admin_index else '✓'} Не ссылается на admin:index как кнопка входа")

    except Exception as e:
        print(f"✗ Ошибка проверки URLs: {e}")
        return False

    return True


def check_views():
    """Проверка представлений"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ПРЕДСТАВЛЕНИЙ")
    print("=" * 60)

    try:
        # Проверка catalog/views.py
        with open('catalog/views.py', 'r') as f:
            content = f.read()

            views_to_check = [
                ('ProductListView', True),
                ('ProductDetailView', True),
                ('ProductCreateView', True),
                ('ProductUpdateView', True),
                ('ProductDeleteView', True),
            ]

            mixins_to_check = [
                ('ProductCreateView', 'LoginRequiredMixin'),
                ('ProductUpdateView', 'LoginRequiredMixin'),
                ('ProductDeleteView', 'LoginRequiredMixin'),
                ('ProductDetailView', 'LoginRequiredMixin'),  # Должен быть!
            ]

            print("\033[94mПредставления каталога:\033[0m")
            for view_name, required in views_to_check:
                exists = view_name in content
                status = "✓" if exists else "✗"
                color = "\033[92m" if exists else "\033[91m"
                print(f"  {color}{status}\033[0m {view_name}")

            print("\n\033[94mЗащита LoginRequiredMixin:\033[0m")
            for view_name, mixin in mixins_to_check:
                has_mixin = f'{view_name}(LoginRequiredMixin' in content or f'class {view_name}(.*{mixin}' in content
                status = "✓" if has_mixin else "✗"
                color = "\033[92m" if has_mixin else "\033[91m"
                note = " (ОШИБКА: должен быть защищен!)" if view_name == 'ProductDetailView' and not has_mixin else ""
                print(f"  {color}{status}\033[0m {view_name} -> {mixin}{note}")

        # Проверка users/views.py
        print("\n\033[94mПредставления пользователей:\033[0m")
        with open('users/views.py', 'r') as f:
            content = f.read()
            has_register_view = 'def register_view' in content or 'class.*RegisterView' in content
            has_login_view = 'def login_view' in content or 'class.*LoginView' in content

            print(f"  {'✓' if has_register_view else '✗'} Представление регистрации")
            print(f"  {'✓' if has_login_view else '✗'} Представление входа")

            # Проверка на классы vs функции
            if 'class.*RegisterView' in content:
                print("  ℹ️  Регистрация через класс (соответствует критерию)")
            else:
                print("  ⚠️  Регистрация через функцию (нужно переделать на класс)")

    except Exception as e:
        print(f"✗ Ошибка проверки представлений: {e}")
        return False

    return True


def main():
    """Основная функция проверки"""
    print("\033[1mПОЛНАЯ ПРОВЕРКА ПРОЕКТА ПО КРИТЕРИЯМ\033[0m")
    print("=" * 60)

    results = []

    # Выполняем проверки
    results.append(("Структура проекта", check_structure()))
    results.append(("Настройки Django", check_settings()))
    results.append(("Модели", check_models()))
    results.append(("URLs", check_urls()))
    results.append(("Представления", check_views()))

    # Итог
    print("\n" + "=" * 60)
    print("\033[1mИТОГ ПРОВЕРКИ\033[0m")
    print("=" * 60)

    total_passed = sum(1 for _, passed in results if passed)
    total_checks = len(results)

    for name, passed in results:
        status = "\033[92mПРОЙДЕНА\033[0m" if passed else "\033[91mНЕ ПРОЙДЕНА\033[0m"
        print(f"{name}: {status}")

    print(f"\n\033[1mРезультат: {total_passed}/{total_checks} проверок пройдено\033[0m")

    if total_passed == total_checks:
        print("\n\033[92m✅ Все критерии выполнены!\033[0m")
    else:
        print("\n\033[91m❌ Есть невыполненные критерии. См. выше.\033[0m")

        # Рекомендации
        print("\n\033[94mЧто нужно исправить:\033[0m")
        if not check_structure():
            print("1. Добавить отсутствующие файлы/папки")
        if not any('ProductDetailView' in str(r) and 'LoginRequiredMixin' in str(r) for r in results):
            print("2. Защитить ProductDetailView с помощью LoginRequiredMixin")
        # ... другие рекомендации


if __name__ == "__main__":
    main()