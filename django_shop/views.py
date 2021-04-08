from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 10
    template_name = 'django_shop/product_list.html'


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'django_shop/product_detail.html'
    login_url = reverse_lazy('django_users:login')


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'django_shop/cart.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = user.customer
        context['customer'] = customer

        if not customer.cart_exists():
            ShoppingCart.objects.create(created=timezone.now(),customer=customer)

        product_queryset = customer.shopping_cart.items.all()
        shopping_cart = user.customer.shopping_cart

        context['total_price'] = shopping_cart.get_total_cost()
        context['product_lineitem_list'] = product_queryset
        return context
