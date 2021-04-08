from django.db import models
from django_users.models import CustomUser
from django.core.validators import MinValueValidator
from django.db.migrations.operations import RunSQL
# Create your models here.


class OrderStatus(models.TextChoices):
    New = "New"
    Hold = "Hold"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Closed = "Closed"


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="customer")
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    address = models.CharField(max_length=512, null=False, blank=False)
    phone = models.CharField(max_length=15, null=False, blank=False)
    billing_address = models.CharField(max_length=256)

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.get_full_name()


class Product(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    supplier = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='shopping_cart')
    created = models.DateField()

    def __str__(self):
        return self.customer.get_full_name() + "'s Shopping Cart"


class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
    ordered = models.DateField()
    shipped = models.DateField(blank=True, null=True)
    ship_to = models.CharField(max_length=500)
    status = models.CharField(max_length=256,choices=OrderStatus.choices, default=OrderStatus.New)

    def __str__(self):
        return self.customer.get_full_name() + " order " + str(self.pk)


class LineItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.RESTRICT, blank=True, null=True, related_name="items")
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, blank=True, null=True,related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)

    def get_total_cost(self):
        return self.quantity*self.price


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    paid = models.DateField()
    total = models.FloatField(null=False, blank=False)
    details = models.CharField(max_length=500)


class Key(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='keys')
    key = models.CharField(max_length=64)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name + " key"


class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="product_detail")
    price = models.FloatField(default=0, validators=([MinValueValidator(0)]))
    quantity = models.IntegerField(
        default=0,
        validators=([MinValueValidator(0)]))

    def __str__(self):
        return self.product.name + " details"


class OrderHistoryItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history_list')
    product_name = models.CharField(max_length=256)
    price = models.FloatField(default=0, validators=([MinValueValidator(0)]))
    quantity = models.IntegerField(default=0, validators=([MinValueValidator(0)]))