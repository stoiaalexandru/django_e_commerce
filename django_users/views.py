from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import CustomUser
from . import forms


class SignUpView(CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'django_users/register.html'
