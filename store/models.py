# store/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal 

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    
    # --- НОВЫЕ ПОЛЯ ДЛЯ СТРОЙМАТЕРИАЛОВ ---
    coverage_area = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Площадь покрытия 1 упаковки (м²)", help_text="Для работы калькулятора. Например: 1.5 для кафеля. Оставьте 0, если это штучный товар.")
    weight = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, verbose_name="Вес 1 упаковки (кг)", help_text="Для расчета доставки (тяжелее 1500 кг - доставка дороже).")
    # --------------------------------------
    
    stock = models.IntegerField(default=0, verbose_name="Наличие (кол-во упаковок)")
    available = models.BooleanField(default=True, verbose_name="В продаже")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', args=[self.slug])
    
    def get_bonus_points(self):
        return int(self.price * Decimal('0.05'))

    @property
    def total_stock(self):
        """Возвращает общее количество (размеры удалены)"""
        return self.stock


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
        
    def get_total_weight(self):
        """Новая функция: считает общий вес всей корзины для доставки"""
        return sum(item.get_total_weight() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Поле size полностью удалено (покупаем штуки/упаковки)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество упаковок")

    def __str__(self):
        return f'{self.quantity} упак. x {self.product.name}'
        
    def get_total_price(self):
        return self.product.price * self.quantity
        
    def get_total_weight(self):
        """Новая функция: считает вес данной позиции"""
        return self.product.weight * self.quantity