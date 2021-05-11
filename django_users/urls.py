from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (SignUpView, GoodByeView, PasswordResetView, PasswordResetDoneView,
                    PasswordResetConfirmView,PasswordResetCompleteView, ActivateAccountView,RegisterSuccessView,
                    ResendActivationEmailView,ResendActivationEmailSuccess,)

app_name = 'django_users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='django_users/login.html'), name='login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('bye/', GoodByeView.as_view(), name='bye'),

    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/',   PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('register/success/', RegisterSuccessView.as_view(), name='register_success'),
    path('resend-activation/', ResendActivationEmailView.as_view(),name='resend_activation_email'),
    path('resend-activation/submitted/', ResendActivationEmailSuccess.as_view(), name='resend_activation_email_success')
]
