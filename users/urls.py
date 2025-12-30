from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, EditBlogPostView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('posts/<int:pk>/edit/', EditBlogPostView.as_view(), name='edit_blog_post')
]
