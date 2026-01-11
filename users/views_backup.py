# users/views.py
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegisterForm, UserLoginForm
from .models import User


# ИСПРАВЛЕНО: класс-представление с переопределением form_valid()
class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        """Переопределяем для отправки письма и автоматического входа"""
        response = super().form_valid(form)

        # Отправка приветственного письма
        user = form.instance
        self.send_welcome_email(user)

        # Автоматический вход после регистрации
        user = form.get_user()
        login(self.request, user)

        return response

    def send_welcome_email(self, user):
        """Отправка приветственного письма"""
        subject = 'Добро пожаловать в наш магазин!'
        message = f'''
        Уважаемый {user.email},

        Добро пожаловать в наш магазин!

        Благодарим вас за регистрацию.

        С уважением,
        Команда магазина
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('catalog:product_list')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('catalog:product_list')


# Оставьте старые функции для совместимости (можно удалить позже)
def register_view(request):
    """Старая версия (можно удалить после тестирования)"""
    from django.shortcuts import render, redirect
    from django.contrib import messages

    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Отправка письма
            subject = 'Добро пожаловать!'
            message = f'Привет, {user.email}! Спасибо за регистрацию.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Регистрация успешна!')
            return redirect('catalog:product_list')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})