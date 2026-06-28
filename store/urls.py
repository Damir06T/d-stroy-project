# store/urls.py

from django.urls import path
from . import views

app_name = 'store' 

urlpatterns = [
    # ИЗМЕНЕНИЕ ЗДЕСЬ: поменяли name='catalog' на name='catalog'
    # Теперь ссылка {% url 'store:catalog' %} в HTML заработает
    path('', views.catalog, name='catalog'), 
    
    # Остальные пути оставляем как есть
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('<slug:slug>/', views.product_detail, name='product_detail'), 
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    
]