# final_fix.py
import os

print("Финальное исправление проекта...")
print("=" * 60)

# 1. Исправляем catalog/views.py
print("1. Проверяю защиту ProductDetailView...")
views_path = "catalog/views.py"

with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем и исправляем ProductDetailView
if "class ProductDetailView(LoginRequiredMixin, DetailView):" not in content:
    print("  ❌ ProductDetailView не защищен")

    # Ищем старую строку и заменяем
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith("class ProductDetailView"):
            print(f"  Найдена строка: {line}")
            # Меняем на правильную
            new_line = "class ProductDetailView(LoginRequiredMixin, DetailView):"
            new_lines.append(new_line)
            print(f"  Исправлено на: {new_line}")
        else:
            new_lines.append(line)

    # Проверяем импорт LoginRequiredMixin
    if "from django.contrib.auth.mixins import LoginRequiredMixin" not in content:
        for i, line in enumerate(new_lines):
            if "from django.views.generic import" in line:
                new_lines[
                    i] = "from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView\nfrom django.contrib.auth.mixins import LoginRequiredMixin"
                print("  ✓ Добавлен импорт LoginRequiredMixin")
                break

    # Сохраняем
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("  ✅ Файл исправлен")
else:
    print("  ✅ ProductDetailView уже защищен")

# 2. Проверяем users/views.py на классы
print("\n2. Проверяю регистрацию через классы...")
users_views_path = "users/views.py"

with open(users_views_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "class UserRegisterView(CreateView)" in content:
    print("  ✅ Регистрация через класс")
else:
    print("  ❌ Регистрация не через класс")
    # Создаем простую версию
    simple_class = '''from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegisterForm, UserLoginForm
from .models import User

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance

        # Отправка письма
        subject = 'Добро пожаловать!'
        message = f'Привет, {user.email}!'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        # Автовход
        user = form.get_user()
        login(self.request, user)

        return response

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('catalog:product_list')
'''

    with open(users_views_path, 'w', encoding='utf-8') as f:
        f.write(simple_class)
    print("  ✅ Создана классовая версия")

# 3. Проверяем users/urls.py
print("\n3. Проверяю users/urls.py...")
users_urls_path = "users/urls.py"

with open(users_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "UserRegisterView.as_view()" in content and "UserLoginView.as_view()" in content:
    print("  ✅ URLs настроены на классы")
else:
    print("  ❌ URLs не настроены на классы")
    # Создаем правильный файл
    correct_urls = '''from django.urls import path
from .views import UserRegisterView, UserLoginView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
]
'''
    with open(users_urls_path, 'w', encoding='utf-8') as f:
        f.write(correct_urls)
    print("  ✅ URLs исправлены")

print("\n" + "=" * 60)
print("Исправления завершены!")
print("Запустите: python manage.py runserver")
print("=" * 60)