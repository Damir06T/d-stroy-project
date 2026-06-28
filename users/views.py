# D-Stroy/users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import translation
from django.views.decorators.http import require_POST 
from django.http import HttpResponseRedirect 

# Импорты форм (VerifyCodeForm больше не нужен)
from .forms import CustomUserCreationForm, UserEditForm, UserProfileEditForm
from .models import LoginHistory, UserProfile
from .utils import get_client_ip


# --- 1. Регистрация Пользователя ---
def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, translation.gettext('Аккаунт успешно создан! Теперь войдите.')) 
            return redirect('login')
        else:
            messages.error(request, translation.gettext('Ошибка при регистрации. Проверьте введенные данные.')) 
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


# --- 2. Логин (ПРЯМОЙ ВХОД БЕЗ ПОЧТЫ) ---
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        request = self.request

        # 1. Авторизуем пользователя сразу
        auth_login(request, user)
        
        # 2. Сохраняем историю входа (твой старый функционал работает)
        ip = get_client_ip(request)
        LoginHistory.objects.create(user=user, ip_address=ip)
        
        # 3. Установка темы и ЯЗЫКА пользователя в сессии
        try:
            user_profile = user.userprofile
            request.session['user_theme'] = user_profile.theme
            request.session[settings.LANGUAGE_COOKIE_NAME] = user_profile.language 
        except:
            pass # Если профиля нет, не страшно
        
        messages.success(request, translation.gettext('Вход успешен! Добро пожаловать.'))
        return redirect('profile') 
    
    def form_invalid(self, form):
        messages.error(self.request, translation.gettext('Неверный логин или пароль.'))
        return super().form_invalid(form)


# --- 3. Страница Верификации Кода ВЫРЕЗАНА ПОЛНОСТЬЮ ---


# --- 4. Профиль и Настройки ---
@login_required
def profile(request):
    history = LoginHistory.objects.filter(user=request.user)[:5]
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        if 'update_user_info' in request.POST:
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = UserProfileEditForm(instance=user_profile)
            
            if user_form.is_valid():
                user_form.save()
                messages.success(request, translation.gettext('Основная информация успешно обновлена!'))
                return redirect('profile')
            else:
                 messages.error(request, translation.gettext('Ошибка при обновлении основной информации.'))
        
        elif 'update_settings' in request.POST:
            user_form = UserEditForm(instance=request.user)
            profile_form = UserProfileEditForm(request.POST, instance=user_profile)
            
            if profile_form.is_valid():
                profile = profile_form.save()
                request.session['user_theme'] = profile.theme
                new_language = profile.language
                translation.activate(new_language)
                request.session[settings.LANGUAGE_COOKIE_NAME] = new_language
                messages.success(request, translation.gettext('Настройки профиля успешно обновлены!'))
                return redirect('profile')
            else:
                 messages.error(request, translation.gettext('Ошибка при обновлении настроек.'))
        else:
             user_form = UserEditForm(instance=request.user)
             profile_form = UserProfileEditForm(instance=user_profile)

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileEditForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'history': history,
        'user_profile': user_profile,
    }
    return render(request, 'users/profile.html', context)


# --- 5. Выход ---
@login_required
def logout_view(request):
    request.session.flush()
    auth_logout(request)
    messages.info(request, translation.gettext("Вы успешно вышли из системы. До свидания!"))
    return redirect('home')


# --- 6. Кастомный переключатель языка ---
@require_POST
def set_user_language(request):
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    language = request.POST.get('language')

    if language and language in dict(settings.LANGUAGES):
        translation.activate(language)
        request.session[settings.LANGUAGE_COOKIE_NAME] = language
        
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
                if user_profile.language != language:
                    user_profile.language = language
                    user_profile.save()
            except UserProfile.DoesNotExist:
                pass

    response = HttpResponseRedirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response