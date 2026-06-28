# chat/urls.py

from django.urls import path
from . import views

app_name = 'chat' 

urlpatterns = [
    # Обычный вход (для покупателя) -> http://127.0.0.1:8000/chat/
    path('', views.support_chat, name='support_chat'),
    
    # Вход для АДМИНА (чтобы ответить) -> http://127.0.0.1:8000/chat/admin/ID_ПОЛЬЗОВАТЕЛЯ/
    path('admin/<int:user_id>/', views.admin_join_chat, name='admin_join_chat'),
]