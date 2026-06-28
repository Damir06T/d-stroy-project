# D-Stroy/settings.py

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _ 

BASE_DIR = Path(__file__).resolve().parent.parent

# ВАЖНО: Замените на свой ключ в реальном проекте!
SECRET_KEY = 'django-insecure-z*5-1p*s_2t6_53i66@6p_6*b53d(i51m7c66(6g6)51^d' 

DEBUG = True

ALLOWED_HOSTS = []


# Регистрация приложений
INSTALLED_APPS = [
    'daphne', # <--- ASGI-сервер (Первый!)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Наши приложения
    'modeltranslation',
    'store',
    'users',
    'rest_framework',
    'import_export',
    
    # <--- НОВЫЕ ПРИЛОЖЕНИЯ ДЛЯ ЧАТА
    'channels',
    'chat',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # !!! ОТКЛЮЧЕНО ВРЕМЕННО ДЛЯ РАБОТЫ ЧАТА !!!
    #'users.middleware.SessionActivityMiddleware', 
]

ROOT_URLCONF = 'D-Stroy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'D-Stroy.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # ... 
]

# --- НАСТРОЙКИ ЯЗЫКА И ВРЕМЕНИ (i18n) ---
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Atyrau'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ru', _('Русский')),
    ('en', _('English')),
    ('kk', _('Қазақша')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Настройки статических файлов
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# Настройки аутентификации
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# --- E-mail (Тестовый режим для разработки) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Все настройки Mail.ru мы удалили, чтобы сайт работал быстро и локально

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Настройки Медиа ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' 

# --- DJANGO REST FRAMEWORK (DRF) ---
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5, 
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ]
}

# ----------------------------------------------------
# <--- НОВЫЕ НАСТРОЙКИ CHANNELS (ASGI)
# ----------------------------------------------------

# Главное ASGI-приложение
ASGI_APPLICATION = 'D-Stroy.asgi.application'

# Настройка Channel Layers
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# !!! ВАЖНО: РАЗРЕШАЕМ ОТОБРАЖЕНИЕ САЙТА В IFRAME (ДЛЯ ЧАТА) !!!
X_FRAME_OPTIONS = 'SAMEORIGIN'