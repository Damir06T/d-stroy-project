# store/urls.py

from django.urls import path
from . import views

app_name = 'store' 

urlpatterns = [
    # 1. Главная страница каталога
    path('', views.catalog, name='catalog'), 
    
    # 2. Конкретные страницы (должны быть ВЫШЕ slug)
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    
    # 3. Динамические пути со slug (ВСЕГДА В САМОМ НИЗУ)
    path('<slug:slug>/', views.product_detail, name='product_detail'), 
]