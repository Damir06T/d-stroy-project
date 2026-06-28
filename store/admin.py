# store/admin.py

from django.contrib import admin
from .models import Category, Product, Cart, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Добавили новые поля в отображение админки (вес и площадь)
    list_display = ['name', 'category', 'price', 'coverage_area', 'weight', 'stock', 'available']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available', 'coverage_area', 'weight']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Cart)
admin.site.register(CartItem)