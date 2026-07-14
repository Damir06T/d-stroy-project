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

from .models import Product, Category, Cart, CartItem, Order, OrderItem
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


# --- 3. Добавить в корзину (С УЧЕТОМ УМНОГО КАЛЬКУЛЯТОРА И AJAX) ---
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request.user)
    
    # Читаем количество
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
    else:
        quantity = 1
    
    # Создаем или находим запись в корзине
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    # Если запрос пришел фоном (через AJAX) - отдаем JSON без перезагрузки
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'quantity': item.quantity,
            'item_total': str(item.get_total_price()),
            'cart_total': str(cart.get_total_price()),
            'total_items': sum(i.quantity for i in cart.items.all())
        })
        
    messages.success(request, f'Количество "{product.name}" обновлено.')
    return redirect(request.META.get('HTTP_REFERER', 'store:catalog'))


# --- 4. Удалить из корзины (С УЧЕТОМ AJAX) ---
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
            qty = item.quantity
            item_tot = item.get_total_price()
            removed = False
        else:
            item.delete()
            qty = 0
            item_tot = 0
            removed = True

        # Если запрос фоновый
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'quantity': qty,
                'item_total': str(item_tot),
                'cart_total': str(cart.get_total_price()),
                'total_items': sum(i.quantity for i in cart.items.all()),
                'removed': removed
            })
            
        messages.info(request, f'Корзина обновлена.')
            
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
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('store:catalog')

    total_price = cart.get_total_price()

    if request.method == 'POST':
        # Получаем данные из формы
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Создаем заказ в БД
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_amount=total_price
        )

        # Переносим товары из корзины в заказ (чтобы зафиксировать цены)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

        # Очищаем корзину после успешного оформления
        cart.items.all().delete()

        # Перенаправляем на страницу успеха
        return redirect('store:order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart': cart, 'total_price': total_price})


# --- 7. Успешное оформление заказа ---
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Формируем текст для WhatsApp
    whatsapp_text = f"Здравствуйте! Я хочу подтвердить заказ #{order.id} на сумму {order.total_amount} ₸. Мой адрес: {order.address}."
    
    return render(request, 'store/order_success.html', {
        'order': order,
        'whatsapp_text': whatsapp_text
    })


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