from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from .mixins import CustomerRedirectMixin
from .models import Customer, ShoppingCart, LineItem, Product
from django.db.models import F


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=10)


class ProductQuantityForm(LoginRequiredMixin, SingleObjectMixin, CustomerRedirectMixin, FormView):
    template_name = 'django_shop/product_detail.html'
    login_url = reverse_lazy('django_users:login')
    success_url = reverse_lazy('django_shop:add_success')
    model = Product
    form_class = QuantityForm

    def form_valid(self, form):
        user = self.request.user
        product = self.get_object()
        quantity = form.cleaned_data['quantity']

        if not user.customer.cart_exists():
            ShoppingCart.objects.create(customer=user.customer)

        cart = user.customer.shopping_cart
        item = cart.items.filter(product_id__exact=product.pk)

        if cart.items.count() == 0:
            cart.created = timezone.now()
        if not item:
            LineItem.objects.create(price=product.product_detail.price, product=product, cart=cart, quantity=quantity)
        else:
            item.update(quantity=F('quantity') + quantity)

        return super(ProductQuantityForm, self).form_valid(form)

