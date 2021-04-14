from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from .mixins import CustomerRequiredMixin
from .models import Customer, ShoppingCart, LineItem, Product
from django.db.models import F


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=10)


class ProductQuantityForm(LoginRequiredMixin, SingleObjectMixin, CustomerRequiredMixin, FormView):
    template_name = 'django_shop/product_detail.html'
    login_url = reverse_lazy('django_users:login')
    success_url = reverse_lazy('django_shop:add_success')
    model = Product
    form_class = QuantityForm


class ProductListViewForm(LoginRequiredMixin, SingleObjectMixin, CustomerRequiredMixin, FormView):
    template_name = 'django_shop/product_list.html'
    login_url = reverse_lazy('django_users:login')
    success_url = reverse_lazy('django_shop:add_success')
    model = Product
    form_class = QuantityForm


