from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.views import View

from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.utils import timezone
from django.http import HttpResponse
from .mixins import CustomerRedirectMixin
from .forms import QuantityForm, ProductQuantityForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'django_shop/product_list.html'


class ProductView(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data()
        context['form'] = QuantityForm()
        return context


class ProductDetailView(LoginRequiredMixin, CustomerRedirectMixin, View):
    def get(self, request, *args, **kwargs):
        view = ProductView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductQuantityForm.as_view()
        return view(request, *args, **kwargs)


class CartView(LoginRequiredMixin, CustomerRedirectMixin, TemplateView):
    template_name = 'django_shop/cart.html'
    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = user.customer

        if not customer.cart_exists():
            ShoppingCart.objects.create(customer=user.customer, created=timezone.now())

        context['customer'] = customer
        return context


class CustomerCreateView(CreateView):
    model = Customer
    success_url = reverse_lazy('index')
    fields = ('first_name', 'last_name', 'address', 'phone', 'billing_address')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CustomerCreateView, self).form_valid(form)


class AddToCartSuccess(TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'