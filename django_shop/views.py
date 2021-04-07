from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin


class ProductListView(LoginRequiredMixin,ListView):
    model = Product
    paginate_by = 10
    template_name = 'django_shop/product_list.html'


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'django_shop/product_detail.html'
    login_url = reverse_lazy('django_users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock'] = len(Key.objects.filter(product_id=self.get_object().pk))
        return context


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'django_shop/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['customer'] = Customer.objects.filter(user_id__exact=user.id).get()

        product_queryset = LineItem.objects.filter(cart__customer__user_id=user.id)

        total = 0
        for product in product_queryset:
            total += product.price*product.quantity
        context['total_price'] = total
        context['product_lineitem_list'] = product_queryset
        return context

