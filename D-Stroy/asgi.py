# D-Stroy/asgi.py

import os
from django.core.asgi import get_asgi_application

# 1. Сначала указываем настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'D-Stroy.settings')

# 2. Инициализируем Django HTTP приложение.
# ЭТО САМЫЙ ВАЖНЫЙ ШАГ: Он загружает настройки Django.
django_asgi_app = get_asgi_application()

# 3. ТОЛЬКО ТЕПЕРЬ импортируем Channels и твой чат
# Если сделать это раньше, будет ошибка ImproperlyConfigured
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

# 4. Собираем итоговое приложение
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})