# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # ИМПОРТ ВСТРОЕННЫХ ВЬЮХ
from . import views

urlpatterns = [
    # 1. Основные страницы (Login, Register, Logout)
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # 2. Профиль
    path('profile/', views.profile, name='profile'),
    
    # 3. СМЕНА ПАРОЛЯ (ВОТ ЧЕГО НЕ ХВАТАЛО!)
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change_form.html', # Сейчас создадим этот шаблон
        success_url='/profile/' # После успеха возвращаем в профиль
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # 4. Смена языка (из views.py)
    path('set-language/', views.set_user_language, name='set_language'),
]