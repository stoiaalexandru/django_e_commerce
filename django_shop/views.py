from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.utils import timezone
from django.http import HttpResponse
from .mixins import CustomerRedirectMixin
from .forms import CustomerCreationForm

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'django_shop/product_list.html'


class ProductDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Product
    template_name = 'django_shop/product_detail.html'
    login_url = reverse_lazy('django_users:login')


class CartView(LoginRequiredMixin, CustomerRedirectMixin, TemplateView):
    template_name = 'django_shop/cart.html'
    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = user.customer

        if not customer.cart_exists():
            ShoppingCart.objects.create(customer=user.customer,created=timezone.now())

        context['customer'] = customer
        cart = customer.shopping_cart
        product_queryset = cart.items.all()
        context['product_lineitem_list'] = product_queryset
        return context


class AddToCartView(LoginRequiredMixin, CustomerRedirectMixin, TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'
    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

    def get(self, request, *args, **kwargs):
        user = self.request.user
        product = Product.objects.filter(pk=self.kwargs['pk']).get()
        if product:
            if user.customer.shopping_cart is None:
                ShoppingCart.objects.create(customer=user.customer)
            cart = user.customer.shopping_cart
            item = cart.items.filter(product_id__exact=product.pk)
            if cart.items.count() == 0:
                cart.created = timezone.now()
            if not item:
                item = LineItem(price=product.product_detail.price, product=product, cart=cart)
            else:
                item = item.get()
                item.quantity += 1

            item.save()
        else:
            return HttpResponse("Something didn't work out, please try again !")
        return super(AddToCartView, self).get(request, *args, **kwargs)


class CustomerCreateView(CreateView):
    model = Customer
    success_url = reverse_lazy('index')
    fields = ('first_name', 'last_name', 'address', 'phone', 'billing_address')

    def form_valid(self, form):
        # data = form.cleaned_data
        # Customer.objects.create(first_name=data['first_name'],
        #                         last_name=data['last_name'],
        #                         address=data['address'],
        #                         billing_address=data['billing_address'],
        #                         phone=data['phone'],
        #                         user=self.request.user
        #                         )
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CustomerCreateView, self).form_valid(form)
