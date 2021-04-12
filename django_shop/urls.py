from django.urls import path
from . import views

app_name = 'django_shop'

urlpatterns = [
    path('productlist/', views.ProductListView.as_view(), name='product_list'),
    path('productdetail/<pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add/success', views.AddToCartSuccess.as_view(), name='add_success'),
    path('customer/create', views.CustomerCreateView.as_view(), name='customer_create'),
    path('add/<pk>/', views.AddToCartView.as_view(), name='add_to_cart')
]
