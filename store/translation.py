# store/translation.py

from modeltranslation.translator import translator, TranslationOptions
from .models import Product, Category

# Настройки перевода для модели Category
class CategoryTranslationOptions(TranslationOptions):
    # Перечисляем поля, которые нужно переводить
    fields = ('name',)

# Настройки перевода для модели Product (Кроссовки)
class ProductTranslationOptions(TranslationOptions):
    # Перечисляем поля, которые нужно переводить
    fields = ('name', 'description')

# Регистрируем модели и их опции перевода
translator.register(Category, CategoryTranslationOptions)
translator.register(Product, ProductTranslationOptions)