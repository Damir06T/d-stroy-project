# D-Stroy/settings.py

from pathlib import Path
import os
import dj_database_url
from django.utils.translation import gettext_lazy as _ 

BASE_DIR = Path(__file__).resolve().parent.parent

# Используем переменные окружения для безопасности
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-z*5-1p*s_2t6_53i66@6p_6*b53d(i51m7c66(6g6)51^d')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'd-stroy-project.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://d-stroy-project.onrender.com']

# Регистрация приложений
INSTALLED_APPS = [
    'daphne',
    'cloudinary_storage', # ВАЖНО: Должен быть ПЕРЕД django.contrib.staticfiles
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary', # Библиотека Cloudinary
    
    'modeltranslation',
    'store',
    'users',
    'rest_framework',
    'import_export',
    'channels',
    'chat',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Для статики
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# База данных для Render (PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)
}

# --- НАСТРОЙКИ CLOUDINARY ---
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Статика
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Язык и время
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Atyrau'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ru', _('Русский')),
    ('en', _('English')),
    ('kk', _('Қазақша')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# Аутентификация
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
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
}

# ASGI
ASGI_APPLICATION = 'D-Stroy.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
X_FRAME_OPTIONS = 'SAMEORIGIN'