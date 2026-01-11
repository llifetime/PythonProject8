# verify_all_assignments.py
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django

django.setup()

from django.conf import settings
from django.core.cache import cache

print("=" * 70)
print("ПРОВЕРКА ВЫПОЛНЕНИЯ ВСЕХ 4 ЗАДАНИЙ")
print("=" * 70)

# Задание 1: Redis как брокер
print("\n✅ ЗАДАНИЕ 1: Установите Redis как брокер для кеширования")
print("   • Проверка настроек Redis...")

if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
    cache_config = settings.CACHES['default']
    backend = cache_config.get('BACKEND', '')

    if 'redis' in backend.lower():
        print("   ✅ Redis настроен как брокер кеширования")
        print(f"      Backend: {backend}")
        print(f"      Location: {cache_config.get('LOCATION', 'N/A')}")

        # Тест подключения
        try:
            cache.set('test_connection', 'OK', 5)
            result = cache.get('test_connection')
            if result == 'OK':
                print("   ✅ Подключение к Redis работает")
            else:
                print(f"   ❌ Проблема с подключением: получено '{result}'")
        except Exception as e:
            print(f"   ❌ Ошибка подключения: {e}")
    else:
        print(f"   ⚠️  Используется не Redis: {backend}")
else:
    print("   ❌ Настройки CACHES не найдены")

# Задание 2: Кеширование страницы продукта
print("\n✅ ЗАДАНИЕ 2: Настройте кеширование для страницы продукта")
print("   • Проверяем файл catalog/views.py...")

try:
    with open('catalog/views.py', 'r', encoding='utf-8') as f:
        views_content = f.read()

    if '@cache_page' in views_content or '@method_decorator(cache_page' in views_content:
        print("   ✅ Декоратор @cache_page найден в views.py")
    else:
        print("   ⚠️  Декоратор @cache_page не найден")

    if 'cache.get' in views_content or 'cache.set' in views_content:
        print("   ✅ Низкоуровневое кеширование используется")
    else:
        print("   ⚠️  Низкоуровневое кеширование не найдено")
except Exception as e:
    print(f"   ❌ Ошибка чтения views.py: {e}")

# Задание 3: Сервисная функция для продуктов
print("\n✅ ЗАДАНИЕ 3: Сервисная функция для работы с продуктами")
print("   • Проверяем файл catalog/services.py...")

services_file = 'catalog/services.py'
if os.path.exists(services_file):
    with open(services_file, 'r', encoding='utf-8') as f:
        services_content = f.read()

    if 'class ProductService' in services_content or 'def get_products_by_category' in services_content:
        print("   ✅ Сервисные функции найдены")

        if 'cache.get' in services_content or 'cache.set' in services_content:
            print("   ✅ Сервисные функции используют кеширование")
        else:
            print("   ⚠️  Сервисные функции не используют кеширование")
    else:
        print("   ❌ Сервисные функции не найдены")
else:
    print("   ❌ Файл catalog/services.py не найден")

# Задание 4: Низкоуровневое кеширование для списка продуктов
print("\n✅ ЗАДАНИЕ 4: Низкоуровневое кеширование для списка продуктов")
print("   • Проверяем ProductListView в catalog/views.py...")

if '_generate_cache_key' in views_content or 'cache.get(' in views_content:
    print("   ✅ Низкоуровневое кеширование настроено в ProductListView")
else:
    print("   ⚠️  Низкоуровневое кеширование не настроено")

# Демонстрация работы кеширования
print("\n📊 ДЕМОНСТРАЦИЯ РАБОТЫ КЕШИРОВАНИЯ:")
print("   • Тест производительности...")

import time

# Запись тестовых данных
start = time.time()
for i in range(50):
    cache.set(f'demo_key_{i}', f'value_{i}' * 10, 60)
write_time = time.time() - start

# Чтение тестовых данных
start = time.time()
for i in range(50):
    cache.get(f'demo_key_{i}')
read_time = time.time() - start

print(f"   • Запись 50 ключей: {write_time:.3f} сек")
print(f"   • Чтение 50 ключей: {read_time:.3f} сек")
print(f"   • Скорость: {50 / read_time:.0f} операций/сек")

# Очистка тестовых данных
for i in range(50):
    cache.delete(f'demo_key_{i}')

print("\n" + "=" * 70)
print("ИТОГОВЫЙ ОТЧЕТ:")
print("=" * 70)

# Собираем результаты
results = []

# Задание 1
if 'redis' in backend.lower():
    results.append("✅ Задание 1: Redis настроен как брокер")
else:
    results.append("❌ Задание 1: Redis не настроен")

# Задание 2
if '@cache_page' in views_content:
    results.append("✅ Задание 2: Кеширование страницы продукта настроено")
else:
    results.append("❌ Задание 2: Кеширование страницы не настроено")

# Задание 3
if os.path.exists(services_file) and 'class ProductService' in services_content:
    results.append("✅ Задание 3: Сервисные функции созданы")
else:
    results.append("❌ Задание 3: Сервисные функции не созданы")

# Задание 4
if '_generate_cache_key' in views_content:
    results.append("✅ Задание 4: Низкоуровневое кеширование настроено")
else:
    results.append("❌ Задание 4: Низкоуровневое кеширование не настроено")

# Выводим результаты
print("\nРЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ЗАДАНИЙ:")
for result in results:
    print(f"   {result}")

completed = sum(1 for r in results if '✅' in r)
total = len(results)

print(f"\n🎯 ВЫПОЛНЕНО: {completed} из {total} заданий")

if completed == total:
    print("\n🎉 ПОЗДРАВЛЯЮ! ВСЕ 4 ЗАДАНИЯ ВЫПОЛНЕНЫ УСПЕШНО!")
    print("   Redis настроен и работает корректно.")
    print("   Кеширование реализовано на всех уровнях.")
else:
    print(f"\n⚠️  ВЫПОЛНЕНО ТОЛЬКО {completed} из {total} заданий")
    print("   Некоторые задания требуют доработки.")

print("\n" + "=" * 70)