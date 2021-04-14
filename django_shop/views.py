from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, FormView, ListView, DetailView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin

from .models import (Customer, Product, ProductDetail, Order, ShoppingCart,
                     LineItem, Payment, Key, OrderHistoryItem)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .mixins import CustomerRedirectMixin
from .forms import QuantityForm, ProductQuantityForm, ProductListViewForm
from django.http import Http404


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


class ProductDetailView(LoginRequiredMixin, CustomerRedirectMixin, View):

    def get(self, request, *args, **kwargs):
        view = ProductDetails.as_view()
        return view(request, *args, **kwargs)


class ProductListView(LoginRequiredMixin, CustomerRedirectMixin, View):

    def get(self, request, *args, **kwargs):
        view = ProductList.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductListViewForm.as_view()
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


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    success_url = reverse_lazy('index')
    fields = ('first_name', 'last_name', 'address', 'phone', 'billing_address')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CustomerCreateView, self).form_valid(form)


class AddToCartView(LoginRequiredMixin, CustomerRedirectMixin, View):
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


class AddToCartSuccess(TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'

