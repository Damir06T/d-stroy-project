# users/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile # Важно: импортируем нашу модель профиля

# --- 1. Форма регистрации (должна быть у тебя уже) ---
class CustomUserCreationForm(UserCreationForm):
    # Здесь ты можешь добавить свои поля, если они есть
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


# --- 2. Форма верификации (должна быть у тебя уже) ---
class VerifyCodeForm(forms.Form):
    code = forms.CharField(
        label='Код из Email',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Введите 6-значный код', 'class': 'form-control'})
    )

# --- 3. ФОРМА ДЛЯ РЕДАКТИРОВАНИЯ ОСНОВНЫХ ДАННЫХ (НОВАЯ) ---
class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# --- 4. ФОРМА ДЛЯ РЕДАКТИРОВАНИЯ ПРОФИЛЯ/АВАТАРА (ОБНОВЛЕННАЯ) ---
# Переименуем UserProfileForm, чтобы избежать конфликта в views.py
class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # Добавляем avatar в список полей
        fields = ['theme', 'language', ] 
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
        }
# УДАЛИ старый класс UserProfileForm, если он у тебя был.