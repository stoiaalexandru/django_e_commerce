from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import SignUpView
app_name = 'django_users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='django_users/login.html'), name='login'),
    path('register/', SignUpView.as_view(), name='register'),
]