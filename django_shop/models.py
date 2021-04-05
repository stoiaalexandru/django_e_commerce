from django.db import models
from django_users.models import CustomUser
from enum import Enum
# Create your models here.


class OrderStatus(models.TextChoices):
    New = "New"
    Hold = "Hold"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Closed = "Closed"


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=512)
    phone = models.CharField(max_length=15)
    billing_address = models.CharField(max_length=256)


class Product(models.Model):
    name = models.CharField(max_length=256)
    supplier = models.CharField(max_length=256)


class ShoppingCart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created = models.DateField()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ordered = models.DateField()
    shipped = models.DateField()
    ship_to = models.CharField(max_length=500)
    status = models.CharField(max_length=256,choices=OrderStatus.choices, default=OrderStatus.New)


class LineItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.RESTRICT)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    paid = models.DateField()
    total = models.FloatField()
    details = models.CharField(max_length=500)

