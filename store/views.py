# store/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator
from django.http import JsonResponse

# DRF импорты
from rest_framework import viewsets
from rest_framework.permissions import AllowAny 
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, Category, Cart, CartItem
from .serializers import ProductSerializer

# --- Вспомогательная функция ---
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

# --- 1. КАТАЛОГ (С Пагинацией, Сортировкой и Поиском) ---
def catalog(request):
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    sort_param = request.GET.get('sort')
    
    context = {
        'categories': categories,
        'query': search_query,
        'current_category': None,
        'grouped_products': None,
        'products': None,
        'current_sort': sort_param,
    }

    # 1. Базовая выборка
    if search_query:
        products = Product.objects.filter(name__icontains=search_query, available=True)
        context['is_search'] = True
        
    elif category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=current_category, available=True)
        context['current_category'] = current_category
        
    elif sort_param:
        products = Product.objects.filter(available=True)
        
    else:
        # Полки (Главная страница каталога)
        grouped_products = []
        for cat in categories:
            prods = Product.objects.filter(category=cat, available=True)[:4] 
            if prods.exists():
                grouped_products.append({'category': cat, 'products': prods})
        context['grouped_products'] = grouped_products
        products = None 

    # 2. Сортировка и Пагинация
    if products:
        if sort_param == 'price_asc':
            products = products.order_by('price')
        elif sort_param == 'price_desc':
            products = products.order_by('-price')
        else:
            products = products.order_by('-created')

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['products'] = page_obj

    return render(request, 'store/catalog.html', context)


# --- 2. Детальная страница (С Историей) ---
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # История просмотров
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if product.id in recently_viewed_ids:
        recently_viewed_ids.remove(product.id)
    recently_viewed_ids.insert(0, product.id)
    if len(recently_viewed_ids) > 5:
        recently_viewed_ids.pop()
    request.session['recently_viewed'] = recently_viewed_ids
    
    recent_products = Product.objects.filter(id__in=recently_viewed_ids).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'recently_viewed': recent_products
    })


# --- 3. Добавить в корзину (С УЧЕТОМ УМНОГО КАЛЬКУЛЯТОРА) ---
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request.user)
    
    # Читаем количество, которое передал пользователь или Умный калькулятор
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
    else:
        quantity = 1
    
    # Создаем или находим запись в корзине
    item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product
    )
    
    if not created:
        item.quantity += quantity
        item.save()
        messages.success(request, f'Количество "{product.name}" увеличено на {quantity} упак.')
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, f'"{product.name}" ({quantity} упак.) добавлен в корзину.')
        
    # Возвращаем пользователя туда, откуда он нажал кнопку
    return redirect(request.META.get('HTTP_REFERER', 'store:catalog'))


# --- 4. Удалить из корзины ---
@login_required
def cart_remove(request, product_id):
    cart = get_or_create_cart(request.user)
    product = get_object_or_404(Product, id=product_id)
    
    items = CartItem.objects.filter(cart=cart, product=product)
    
    if items.exists():
        item = items.first()
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            messages.info(request, f'Количество уменьшено.')
        else:
            item.delete()
            messages.warning(request, f'Товар удален из корзины.')
            
    return redirect(request.META.get('HTTP_REFERER', 'store:cart_detail'))


# --- 5. Просмотр корзины ---
@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.all()
    total_price = cart.get_total_price()
    total_items = items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    return render(request, 'store/cart_detail.html', {
        'cart': cart, 'items': items, 'total_price': total_price, 'total_items': total_items
    })


# --- 6. Оформление заказа ---
@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    if cart.items.count() == 0:
        return redirect('store:catalog')
    return render(request, 'store/checkout.html', {'cart': cart, 'total_price': cart.get_total_price()})


# --- 7. API ЖИВОГО ПОИСКА ---
def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) > 1:
        products = Product.objects.filter(name__icontains=query, available=True)[:5]
        results = []
        for p in products:
            results.append({
                'name': p.name,
                'url': p.get_absolute_url(),
                'price': str(p.price),
                'image': p.image.url if p.image else None
            })
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)


# --- DRF API ---
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created', 'stock']
    ordering = ['-created']