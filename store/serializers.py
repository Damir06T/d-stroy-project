# store/serializers.py (ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ)

from rest_framework import serializers
from .models import Product 

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    Используем явный список полей, соответствующий models.py, 
    чтобы устранить ошибку FieldError.
    """
    class Meta:
        model = Product
        # !!! ЭТОТ СПИСОК УСТРАНЯЕТ ОШИБКУ 500 FieldError !!!
        fields = (
            'id',               # ID товара
            'category',         # Связанная категория
            'name',             # Название
            'slug',             # SLUG
            'description',      # Описание
            'price',            # Цена
            'stock',            # Наличие
            'available',        # В продаже
            'image',            # Изображение
            'created',          # Дата создания (только для чтения)
            'updated',          # Дата обновления (только для чтения)
        )