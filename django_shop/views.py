from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin

from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem, OrderStatus, OrderHistoryKey)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .mixins import CustomerRequiredMixin
from .forms import QuantityForm, ProductQuantityForm, ProductListViewForm
from django.http import Http404
from .tasks import send_order_email
from django.core import serializers


class ProductList(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'django_shop/product_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductList, self).get_context_data()
        context['form'] = QuantityForm()
        return context


class ProductDetails(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetails, self).get_context_data()
        context['form'] = QuantityForm(initial={'product_id': self.get_object().pk})
        return context


class ProductDetailView(LoginRequiredMixin, CustomerRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = ProductDetails.as_view()
        return view(request, *args, **kwargs)


class ProductListView(LoginRequiredMixin, CustomerRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = ProductList.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductListViewForm.as_view()
        return view(request, *args, **kwargs)


class CartView(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'django_shop/cart.html'
    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = user.customer

        if not customer.cart_exists():
            ShoppingCart.objects.create(customer=user.customer, created=timezone.now())

        checkout_available = True
        cart_items = customer.shopping_cart.items.all()
        for item in cart_items:
            if item.product.get_stock() < item.quantity:
                checkout_available = False

        context['checkout_available']=checkout_available
        context['customer'] = customer
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    success_url = reverse_lazy('index')
    fields = ('first_name', 'last_name', 'address', 'phone', 'billing_address')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CustomerCreateView, self).form_valid(form)


class AddToCartView(LoginRequiredMixin, CustomerRequiredMixin, View):
    success_url = reverse_lazy('django_shop:add_success')
    form_class = QuantityForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = self.request.user
            product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
            quantity = form.cleaned_data['quantity']

            if not user.customer.cart_exists():
                ShoppingCart.objects.create(customer=user.customer)

            cart = user.customer.shopping_cart
            item = cart.items.filter(product_id__exact=product.pk)

            if cart.items.count() == 0:
                cart.created = timezone.now()
            if not item:
                LineItem.objects.create(price=product.product_detail.price, product=product, cart=cart,
                                        quantity=quantity)
            else:
                item.update(quantity=F('quantity') + quantity)
            return HttpResponseRedirect(self.success_url)
        raise Http404

    def get(self, request, *args, **kwargs):
        raise Http404


class CheckoutView(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'django_shop/checkout.html'

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data()
        context['customer'] = self.request.user.customer
        return context


class CheckoutEndpoint(LoginRequiredMixin,CustomerRequiredMixin, View):
    success_url = reverse_lazy('django_shop:order_list')
    fail_url = reverse_lazy('django_shop:checkout_error')

    def get(self, request, *args, **kwargs):
        return HttpResponse('<div class="jumbotron"><h1>NOT ALLOWED</h1></div>')

    def post(self, request, *args, **kwargs):
        customer = self.request.user.customer
        items = customer.shopping_cart.items

        for item in items.all():
            if item.product.get_stock() < item.quantity:
                return HttpResponseRedirect(self.fail_url)

        order = Order.objects.create(customer=customer,
                                     ordered=timezone.now(),
                                     ship_to=customer.address,
                                     status=OrderStatus.Pending)
        if not items:
            raise Http404

        items.update(order=order, cart=None)
        for item in order.items.all():
            OrderHistoryItem.objects.create(order=order,
                                            product_name=item.product.name,
                                            price=item.product.product_detail.price,
                                            quantity=item.quantity)
            keys = item.product.keys.all()[:item.quantity]
            for key in keys:
                OrderHistoryKey.objects.create(key=key.key)
               # key.delete()

        send_order_email.delay(template='django_shop/checkout_email.html',
                               user_pk=self.request.user.pk,
                               order_pk=order.pk,
                               customer_pk=customer.pk)

        return HttpResponseRedirect(self.success_url)


class OrderListView(LoginRequiredMixin,CustomerRequiredMixin,ListView):
    model = Order
    template_name = 'django_shop/order_list.html'


class AddToCartSuccess(TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'


class CheckoutError(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'django_shop/checkout_error.html'


class ReserveView(View):
    def get(self, request, *args, **kwargs):
        OrderHistoryKey.objects.all().delete()
        return HttpResponse("Success")