# chat/admin.py (ЗАМЕНИТЬ ПОЛНОСТЬЮ)

from django.contrib import admin
from .models import Message, ChatDialog
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Max, Count

# 1. СТАРЫЙ СПИСОК (ВСЕ СООБЩЕНИЯ)
# Оставим его, он полезен для архива
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'room', 'short_text', 'created_at')
    list_filter = ('room', 'created_at')
    search_fields = ('author__username', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('author', 'room', 'text', 'created_at')

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Сообщение'


# 2. НОВЫЙ СПИСОК (КАК В ИНСТАГРАМЕ - ПО ЛЮДЯМ)
@admin.register(ChatDialog)
class ChatDialogAdmin(admin.ModelAdmin):
    # Показываем: Имя, Email, Последний раз был в сети, КНОПКА
    list_display = ('username', 'email', 'last_message_date', 'open_chat_button')
    
    # Убираем кнопку "Добавить", так как пользователей мы тут не создаем
    def has_add_permission(self, request):
        return False
    
    # Убираем кнопку "Удалить", чтобы случайно не удалить юзера
    def has_delete_permission(self, request, obj=None):
        return False

    # ГЛАВНАЯ МАГИЯ: Фильтруем список
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 1. Оставляем только тех, кто писал сообщения в комнаты support_
        # 2. distinct() убирает дубликаты (чтобы юзер не появлялся 7 раз)
        qs = qs.filter(messages__room__startswith='support_').distinct()
        
        # Оптимизация: подгружаем дату последнего сообщения
        qs = qs.annotate(latest_msg=Max('messages__created_at')).order_by('-latest_msg')
        return qs

    # Колонка: Дата последнего сообщения
    def last_message_date(self, obj):
        return obj.latest_msg
    last_message_date.short_description = 'Последнее сообщение'
    last_message_date.admin_order_field = 'latest_msg'

    # КНОПКА: Открыть чат
    def open_chat_button(self, obj):
        # Ссылка на нашу функцию admin_join_chat
        url = reverse('chat:admin_join_chat', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" class="button" style="background-color: #007bff; color: white; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-weight: bold;">💬 Открыть переписку</a>',
            url
        )
    open_chat_button.short_description = 'Действие'