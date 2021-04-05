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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=512)
    phone = models.CharField(max_length=15)
    billing_address = models.CharField(max_length=256)

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.get_full_name()


class Product(models.Model):
    name = models.CharField(max_length=256)
    supplier = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created = models.DateField()

    def __str__(self):
        return self.customer.get_full_name() + "'s Shopping Cart"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ordered = models.DateField()
    shipped = models.DateField(blank=True, null=True)
    ship_to = models.CharField(max_length=500)
    status = models.CharField(max_length=256,choices=OrderStatus.choices, default=OrderStatus.New)

    def __str__(self):
        return self.customer.get_full_name() + " order " + str(self.pk)


class LineItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.RESTRICT, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    paid = models.DateField()
    total = models.FloatField()
    details = models.CharField(max_length=500)


class Key(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name + " key"


class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    price = models.FloatField(default=0, validators=([MinValueValidator(0)]))
    quantity = models.IntegerField(
        default=0,
        validators=([MinValueValidator(0)]))

    def __str__(self):
        return self.product.name + " details"


class OrderHistoryItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=256)
    price = models.FloatField(default=0, validators=([MinValueValidator(0)]))
    quantity = models.IntegerField(default=0, validators=([MinValueValidator(0)]))