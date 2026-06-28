# chat/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

@login_required
def support_chat(request):
    """Чат для покупателя"""
    room_name = f'support_{request.user.id}'
    
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': request.user.username,
        # Покупатель видит, что общается с поддержкой
        'chat_title': 'Служба поддержки', 
    })

@login_required
def admin_join_chat(request, user_id):
    """Чат для админа (вход в комнату покупателя)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Доступ запрещен.")
    
    # Получаем объект пользователя-покупателя, чтобы узнать его имя
    target_user = get_object_or_404(User, id=user_id)
    room_name = f'support_{user_id}'
    
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': request.user.username,
        # Админ видит имя конкретного покупателя
        'chat_title': f'Чат с пользователем: {target_user.username}',
    })