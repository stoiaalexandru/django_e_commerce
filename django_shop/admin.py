from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Product)
admin.site.register(models.Order)
admin.site.register(models.Customer)
admin.site.register(models.Key)
admin.site.register(models.LineItem)
admin.site.register(models.ShoppingCart)
admin.site.register(models.Payment)
admin.site.register(models.ProductDetail)
admin.site.register(models.OrderHistoryItem)
