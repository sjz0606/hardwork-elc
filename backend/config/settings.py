import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def _royxat(nom, standart=''):
    return [x.strip() for x in os.getenv(nom, standart).split(',') if x.strip()]


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-kalit')
DEBUG = os.getenv('DEBUG', '0') == '1'
ALLOWED_HOSTS = _royxat('ALLOWED_HOSTS', '127.0.0.1,localhost')
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS if h not in ('127.0.0.1', 'localhost')]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_CHAT_IDS = [int(x) for x in _royxat('ADMIN_CHAT_IDS') if x.lstrip('-').isdigit()]
CORS_ORIGINS = _royxat('CORS_ORIGINS')
SITE_URL = os.getenv('SITE_URL', '')                # https://hardwork.osonhujjat.uz
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')    # Telegram webhook maxfiy kaliti

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'maktab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'config.sayt.SaytMiddleware',  # WhiteNoise + statik sayt (index.html, css, js, media)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Statik sayt repo ildizida (backend/ ning bir pog'ona yuqorisida)
SAYT_ILDIZ = BASE_DIR.parent
WHITENOISE_INDEX_FILE = True

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Bot holati (login/ariza qadamlari) bazada — webhookda jarayonlar o'rtasida saqlanadi
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.db.DatabaseCache', 'LOCATION': 'kesh'}}

LOGGING = {
    'version': 1, 'disable_existing_loggers': False,
    'handlers': {'konsol': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['konsol'], 'level': 'WARNING'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
