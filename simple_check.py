# simple_check.py
import os

print("Упрощенная проверка проекта")
print("=" * 50)

# Ключевые проверки
checks = [
    ("catalog/__init__.py существует", os.path.exists("catalog/__init__.py")),
    ("ProductDetailView защищен", False),  # Проверим ниже
    ("Header содержит users:login", False),
    ("Header содержит users:register", False),
    ("Регистрация через класс", False),
]

# Проверяем ProductDetailView
if os.path.exists("catalog/views.py"):
    with open("catalog/views.py", "r", encoding="utf-8") as f:
        content = f.read()
        checks[1] = ("ProductDetailView защищен",
                    "class ProductDetailView(LoginRequiredMixin" in content)

# Проверяем Header
if os.path.exists("catalog/templates/catalog/includes/header.html"):
    with open("catalog/templates/catalog/includes/header.html", "r", encoding="utf-8") as f:
        content = f.read()
        checks[2] = ("Header содержит users:login", "users:login" in content)
        checks[3] = ("Header содержит users:register", "users:register" in content)

# Проверяем users/views.py
if os.path.exists("users/views.py"):
    with open("users/views.py", "r", encoding="utf-8") as f:
        content = f.read()
        checks[4] = ("Регистрация через класс", "class UserRegisterView" in content)

# Выводим результаты
print("\nРезультаты:")
for i, (name, result) in enumerate(checks):
    status = "✅" if result else "❌"
    print(f"{i+1}. {status} {name}")

print("\n" + "=" * 50)
passed = sum(1 for _, r in checks if r)
print(f"Итог: {passed}/{len(checks)} критериев выполнено")

if passed == len(checks):
    print("\n🎉 ВСЕ КРИТЕРИИ ВЫПОЛНЕНЫ!")
else:
    print("\n⚠️  Есть невыполненные критерии")