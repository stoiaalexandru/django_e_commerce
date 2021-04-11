from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import HttpResponse


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
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
        cart = customer.get_or_create_cart()

        product_queryset = cart.items.all()

        context['total_price'] = cart.get_total_cost()
        context['product_lineitem_list'] = product_queryset
        return context


class AddToCartView(LoginRequiredMixin, TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'

    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=self.kwargs['pk']).get()
        if product:
            cart = self.request.user.customer.get_or_create_cart()

            item = product.exists_in_cart(cart).get()

            if item is not None:
                item.quantity += 1
            else:
                item = LineItem(price=product.product_detail.price,product=product, cart=cart)

            item.save()
        else:
            return HttpResponse("Something didn't work out, please try again !")
        return super(AddToCartView, self).get(request, *args, **kwargs)
