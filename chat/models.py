# chat/models.py

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """Модель для хранения истории сообщений в чате."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(verbose_name="Текст сообщения")
    room = models.CharField(max_length=255, verbose_name="Название комнаты") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return f"[{self.room}] {self.author.username}: {self.text[:30]}..."
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        
# chat/models.py (ДОБАВИТЬ В КОНЕЦ)

class ChatDialog(User):
    """Виртуальная модель для отображения списка диалогов"""
    class Meta:
        proxy = True
        verbose_name = "Диалог с клиентом"
        verbose_name_plural = "Мои Диалоги (Inbox)"