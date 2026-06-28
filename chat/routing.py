# chat/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Маршрут для WebSocket-соединения с динамическим именем комнаты
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]