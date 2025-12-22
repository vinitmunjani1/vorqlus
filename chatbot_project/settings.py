"""
Django settings for chatbot_project project.
Configured for Railway deployment with PostgreSQL.
"""

from pathlib import Path
import os

# Try to import decouple, fallback to os.environ if not available
try:
    from decouple import config
    def get_env(key, default=None, cast=None):
        if cast is bool:
            return config(key, default=default, cast=bool)
        return config(key, default=default)
except ImportError:
    # Fallback to os.environ if decouple is not installed
    def get_env(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast is bool:
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', '1', 'yes', 'on') if value else False
        return value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env('DEBUG', default=True, cast=bool)

# Allowed hosts - Railway provides RAILWAY_PUBLIC_DOMAIN
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Add Railway domain if available
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# Add custom domain if provided
CUSTOM_DOMAIN = get_env('CUSTOM_DOMAIN', default='')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Allow all hosts if specified (safe fallback for some environments)
if get_env('ALLOW_ALL_HOSTS', default=True, cast=bool):
    ALLOWED_HOSTS = ['*']
    
    
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chatbot_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'chatbot_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Check for DATABASE_URL (Railway provides this)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Use PostgreSQL on Railway
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional locations of static files (for development)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Whitenoise configuration for serving static files in production
# Using CompressedStaticFilesStorage prevents errors if referenced static files are missing
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Together AI Configuration
TOGETHER_API_KEY = get_env('TOGETHER_API_KEY', default='')
TOGETHER_MODEL_NAME = get_env('TOGETHER_MODEL_NAME', default='openai/gpt-oss-120b')#default='meta-llama/Llama-3.3-70B-Instruct-Turbo')
ROLES_JSON_FILE = BASE_DIR / 'AI_Role_Player_System_Prompts_Formatted.json'

# Supermemory Configuration
SUPERMEMORY_API_KEY = get_env('SUPERMEMORY_API_KEY', default='')
SUPERMEMORY_ENABLED = get_env('SUPERMEMORY_ENABLED', default=True, cast=bool)
SUPERMEMORY_NAMESPACE = get_env('SUPERMEMORY_NAMESPACE', default='production' if RAILWAY_PUBLIC_DOMAIN else 'local')

# CSRF Trusted Origins for Railway
CSRF_TRUSTED_ORIGINS = ['https://vorqlus.up.railway.app']

if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')

if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')

# Security settings for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
