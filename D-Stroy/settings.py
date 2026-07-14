# D-Stroy/settings.py

from pathlib import Path
import os
import dj_database_url  # Не забудь про этот пакет (есть в твоем requirements.txt)
from django.utils.translation import gettext_lazy as _ 

BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТЬ (Берем из переменных окружения Render) ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-super-secret-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Разрешаем доступ с локалхоста и любого адреса на Render
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://d-stroy-project.onrender.com']

# --- ПРИЛОЖЕНИЯ ---
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'modeltranslation',
    'store',
    'users',
    'rest_framework',
    'import_export',
    
    'channels',
    'chat',
]

# --- MIDDLEWARE (Добавлен WhiteNoise для статики) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # ВАЖНО: для работы статики на Render
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

# --- БАЗА ДАННЫХ (Подключение через переменную DATABASE_URL) ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=True
    )
}

# --- ЯЗЫК И ВРЕМЯ ---
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

# --- СТАТИКА (Настройки для продакшена) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Важно для WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- МЕДИА ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' 

# --- НАСТРОЙКИ REST FRAMEWORK ---
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

# --- CHANNELS (ASGI) ---
ASGI_APPLICATION = 'D-Stroy.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

X_FRAME_OPTIONS = 'SAMEORIGIN'