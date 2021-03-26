from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from .views import SignUpView, GoodByeView, PasswordResetView, ActivateAccountView

app_name = 'django_users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='django_users/login.html'), name='login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('bye/', GoodByeView.as_view(), name='bye'),
    # path('activate/<uidb64>/<token>/', activate, name='activate'),

    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='django_users/registration/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='django_users/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='django_users/registration/password_reset_complete.html'),
         name='password_reset_complete'),

    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account')
]
