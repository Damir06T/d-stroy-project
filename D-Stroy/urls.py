# D-Stroy/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings 
from django.conf.urls.static import static 
from django.conf.urls.i18n import i18n_patterns 
from django.views.static import serve # Добавь этот импорт
from django.urls import re_path       # И этот

# Импорты для хака создания админа
from django.contrib.auth.models import User
from django.http import HttpResponse

# Импорт функции переключения языка
from users.views import set_user_language

# ===============================================
# --- ДОБАВЛЕНИЕ DJANGO REST FRAMEWORK (DRF) ---
# ===============================================
from rest_framework.routers import DefaultRouter
from store.views import ProductViewSet 

# 1. Настройка Роутера
router = DefaultRouter()

# 2. Регистрируем ViewSet: 
router.register(r'products', ProductViewSet) 
# ===============================================

# --- ХАК ДЛЯ СОЗДАНИЯ АДМИНА ---
def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
        return HttpResponse('Админ сәтті құрылды! Логин: admin, Пароль: admin12345')
    return HttpResponse('Админ базада бар, қайта құрудың қажеті жоқ!')


# URL-адреса, которые НЕ получают префикс языка
urlpatterns = [
    # Исправление: Перехватываем стандартный URL setlang нашей кастомной функцией
    path('i18n/setlang/', set_user_language, name='set_language'), 
    
    path('admin/', admin.site.urls),
    
    # Ссылка для создания админа
    path('create-admin/', create_admin), 

    # DRF API Маршруты
    path('api/', include(router.urls)), 
    
    # Подключаем стандартный API Login/Logout
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
]


# Основные URL-адреса, обернутые в i18n_patterns
urlpatterns += i18n_patterns(
    
    path('', TemplateView.as_view(template_name='base_home.html'), name='home'), 
    path('', include('users.urls')), 
    path('store/', include('store.urls')), 
    
    # Маршрут для чата
    path('chat/', include('chat.urls')), 
    
    prefix_default_language=False
)


# Блок для отдачи медиа-файлов локально (в режиме DEBUG=True)
# Замени блок if settings.DEBUG на этот код
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]