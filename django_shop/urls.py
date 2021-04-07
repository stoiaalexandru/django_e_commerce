from django.urls import path
from . import views
app_name = 'django_shop'

urlpatterns = [
    path('productlist/', views.ProductListView.as_view(), name='product_list'),
    path('productdetail/<pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/',views.CartView.as_view(), name='cart')
]