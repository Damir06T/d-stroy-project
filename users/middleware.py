# users/middleware.py

import datetime
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils.translation import get_language # Для получения текущего языка
from django.contrib import messages

logger = logging.getLogger(__name__)

# Пороговое значение бездействия (15 минут * 60 секунд = 900 секунд)
SESSION_TIMEOUT_SECONDS = 15 * 60 

# Меняем класс, чтобы он соответствовал всем требованиям задания
class SessionActivityMiddleware(MiddlewareMixin):
    """
    Middleware, который выполняет все требования задания:
    1. Фиксирует запросы (логирование).
    2. Добавляет IP-адрес и текущее время в request.
    3. Отслеживает сессии (счетчик посещений, последняя страница, язык).
    4. Проверяет активность и выполняет автовыход.
    """
    
    # Мы используем __call__ для совместимости с Django, 
    # а всю логику разместим в process_request для чистоты
    def __call__(self, request):
        response = self.process_request(request)
        if response is None:
            response = self.get_response(request)
        return response

    def process_request(self, request):
        
        # 1. Добавляем информацию в request (текущее время, IP) (Требование 2.2)
        request.user_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        request.current_time = timezone.now()
        
        # 1.1. Фиксируем входящий запрос (Логирование) (Требование 2.1)
        # Пропускаем запросы к статике, чтобы не засорять лог
        is_static = request.path.startswith(settings.STATIC_URL) or request.path == '/favicon.ico'
        if not is_static:
            logger.info(
                f"[{request.current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Request: {request.method} {request.path} (IP: {request.user_ip})"
            )
        
        # ----------------------------------------------------
        # 2. Работа с сессиями (Требование 1)
        # ----------------------------------------------------
        
        # Счетчик посещений (п. 1.1)
        current_count = request.session.get('visit_count', 0)
        if not is_static:
             # Увеличиваем счетчик только при реальном обращении к странице
             request.session['visit_count'] = current_count + 1
        
        # Последняя открытая страница (п. 1.2)
        if not is_static and request.path != request.session.get('last_page'):
            request.session['last_page'] = request.path

        # Выбранная языковая настройка (п. 1.3 и i18n)
        current_language = get_language()
        request.session['selected_language'] = current_language
        request.current_language = current_language # Добавляем для вывода в шаблоне
        
        # ----------------------------------------------------
        # 3. Проверка активности пользователя (Автовыход) (Требование 2.3)
        # ----------------------------------------------------

        if request.user.is_authenticated:
            # Используем timestamp для надежного хранения
            last_activity_ts = request.session.get('last_activity_ts')
            
            if last_activity_ts:
                # Преобразование метки времени (timestamp) в объект datetime
                last_activity_dt = datetime.datetime.fromtimestamp(last_activity_ts, tz=datetime.timezone.utc)
                idle_time = (timezone.now() - last_activity_dt).total_seconds()

                if idle_time > SESSION_TIMEOUT_SECONDS:
                    # Автовыход
                    request.session.flush() # Очистка всей сессии (п. 1.4)
                    messages.warning(request, "Вы были автоматически выведены из системы из-за 15 минут бездействия.")
                    logger.warning(f"User {request.user.username} auto-logged out due to inactivity.")
                    
                    # Перенаправляем на страницу входа (Правильная реализация автовыхода)
                    return redirect(reverse('login'))
            
            # Обновляем время последней активности (только если это не статический файл)
            if not is_static:
                request.session['last_activity_ts'] = timezone.now().timestamp()
            
        # Обновление сессии (убеждаемся, что изменения сохраняются)
        request.session.modified = True 

        return None # Продолжаем выполнение запроса