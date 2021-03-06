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
from .tasks import send_order_email, send_order_history_single_email, send_order_history_all_email
from datetime import timedelta
from .dbsettings import HistoryEmailOptions


class ProductList(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'django_shop/product_list.html'
    login_url = reverse_lazy('django_users:login')

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
    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

    def get(self, request, *args, **kwargs):
        view = ProductDetails.as_view()
        return view(request, *args, **kwargs)


class ProductListView(LoginRequiredMixin, CustomerRequiredMixin, View):

    login_url = reverse_lazy('django_users:login')
    redirect_url = reverse_lazy('django_shop:customer_create')

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
    login_url = reverse_lazy('django_users:login')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CustomerCreateView, self).form_valid(form)


class AddToCartView(LoginRequiredMixin, CustomerRequiredMixin, View):
    redirect_url = reverse_lazy('django_shop:customer_create')
    success_url = reverse_lazy('django_shop:add_success')
    form_class = QuantityForm
    login_url = reverse_lazy('django_users:login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = self.request.user
            product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
            quantity = form.cleaned_data['quantity']

            if not user.customer.cart_exists():
                ShoppingCart.objects.create(customer=user.customer,created=timezone.now())

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
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data()
        context['customer'] = self.request.user.customer
        return context


class CheckoutEndpoint(LoginRequiredMixin,CustomerRequiredMixin, View):
    success_url = reverse_lazy('django_shop:order_list')
    fail_url = reverse_lazy('django_shop:checkout_error')
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')

    def get(self, request, *args, **kwargs):
        return HttpResponse('<div class="jumbotron"><h1>NOT ALLOWED</h1></div>')

    def post(self, request, *args, **kwargs):
        customer = self.request.user.customer
        cart = customer.shopping_cart
        items = cart.items.all()

        for item in items:
            if item.product.get_stock() < item.quantity:
                return HttpResponseRedirect(self.fail_url)

        order = Order.objects.create(customer=customer,
                                     ordered=timezone.now(),
                                     ship_to=customer.address,
                                     status=OrderStatus.Pending)
        if len(items) == 0:
            raise Http404

        for item in items:
            item.order = order
            item.cart = None
            item.save()

            history_item = OrderHistoryItem.objects.create(order=order,
                                            product_name=item.product.name,
                                            price=item.product.product_detail.price,
                                            quantity=item.quantity)
            keys = item.product.keys.all()[:item.quantity]
            for key in keys:
                OrderHistoryKey.objects.create(order_item=history_item, key=key.key)
               # key.delete()

        send_order_email.delay(template='django_shop/checkout_email.html',
                               order_pk=order.pk)

        return HttpResponseRedirect(self.success_url)


class OrderListView(LoginRequiredMixin,CustomerRequiredMixin,ListView):
    model = Order
    template_name = 'django_shop/order_list.html'
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')


class OrderDetailView(LoginRequiredMixin,CustomerRequiredMixin,DetailView):
    model = Order
    template_name = 'django_shop/order_detail.html'
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')


class AddToCartSuccess(TemplateView):
    template_name = 'django_shop/add_to_cart_success.html'


class CheckoutError(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'django_shop/checkout_error.html'
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')


class SendHistorySuccessView(TemplateView):
    template_name = 'django_shop/send_history_success.html'
    fail_url = reverse_lazy('django_shop:history_email_fail')


class SendHistoryEmailFailView(LoginRequiredMixin,CustomerRequiredMixin,TemplateView):
    template_name = 'django_shop/send_history_fail.html'
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')

    def get_context_data(self, **kwargs):
        context = super(SendHistoryEmailFailView, self).get_context_data()
        customer = self.request.user.customer
        mail_options = HistoryEmailOptions()
        minutes, seconds =\
            divmod((mail_options.resend_delay_all-(timezone.now()-customer.email_requested)).total_seconds(), 60)
        context['time_remaining'] = "{}:{}".format(int(minutes),int(seconds))

        return context


class SendHistoryAllEmailEndpoint(LoginRequiredMixin, CustomerRequiredMixin, View):
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')
    success_url = reverse_lazy('django_shop:history_email_success')
    fail_url = reverse_lazy('django_shop:history_email_fail')
    mail_template = 'django_shop/order_history_email_all.html'

    def get(self, request, *args, **kwargs):
        customer = self.request.user.customer
        email_request_date = self.request.user.customer.email_requested
        mail_options = HistoryEmailOptions()
        if email_request_date is None or (email_request_date + mail_options.resend_delay_all < timezone.now()):
            send_order_history_all_email.delay(self.mail_template, self.request.user.customer.pk)
            customer.email_requested = timezone.now()
            customer.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(self.fail_url)


class SendHistorySingleEmailEndpoint(LoginRequiredMixin, CustomerRequiredMixin, View):
    redirect_url = reverse_lazy('django_shop:customer_create')
    login_url = reverse_lazy('django_users:login')
    success_url = reverse_lazy('django_shop:history_email_success')
    fail_url = reverse_lazy('django_shop:history_email_fail')
    mail_template = 'django_shop/order_history_email_single.html'

    def get(self, request, *args, **kwargs):
        ## ToDo: add time validation
        pk = kwargs['pk']
        order = Order.objects.filter(pk=pk).get()
        if order:
            send_order_history_single_email.delay(self.mail_template, pk)
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(self.fail_url)