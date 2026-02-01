"""
Django settings for MonPanierLocal project.

This module contains all Django settings for the MonPanierLocal application.
Settings are loaded from environment variables with sensible defaults for development.

Security considerations:
- SECRET_KEY must be set in production (never use default)
- DEBUG must be False in production
- ALLOWED_HOSTS must be configured for production domains
- SSL/TLS should be enabled in production
"""
from pathlib import Path
from datetime import timedelta
import os
from typing import Any, Callable, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
# Charger le .env depuis la racine du projet (2 niveaux au-dessus de backend/config/)
PROJECT_ROOT = BASE_DIR.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# Charger le .env avec python-dotenv
if ENV_FILE.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)


def config(key: str, default: Optional[str] = None, cast: Optional[Callable[[str], Any]] = None) -> Any:
    """
    Helper function to get configuration from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if key is not found
        cast: Function to cast the value (bool, int, lambda, etc.)
    
    Returns:
        Configuration value, optionally cast to specified type
    
    Example:
        >>> config('DEBUG', default='False', cast=bool)
        False
        >>> config('PORT', default='8000', cast=int)
        8000
    """
    value = os.getenv(key, default)
    if value is None:
        return default
    if cast:
        if cast == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif callable(cast):
            return cast(value)
    return value


# SECURITY WARNING: keep the secret key used in production secret!
# In production, this MUST be set via environment variable
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default='False', cast=bool)

# Hosts/domain names that this Django site can serve
# In production, this MUST be set to your actual domain(s)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'whitenoise.runserver_nostatic',
    'apps.auth',
    'apps.producers',
    'apps.products',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='monpanierlocal'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            # Performance optimizations
            'options': '-c statement_timeout=30000',  # 30 seconds
        },
        # Connection pooling settings
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),  # 10 minutes
    }
}

# Redis Cache Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CACHE_TTL = config('CACHE_TTL', default=300, cast=int)  # 5 minutes par défaut

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'mpl',  # MonPanierLocal
        'TIMEOUT': CACHE_TTL,
    },
    # Cache séparé pour les sessions (plus longue durée)
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL.replace('/0', '/1') if '/0' in REDIS_URL else REDIS_URL + '/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'mpl_session',
        'TIMEOUT': 86400,  # 24 heures
    },
    # Cache séparé pour le rate limiting
    'ratelimit': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL.replace('/0', '/2') if '/0' in REDIS_URL else REDIS_URL + '/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'mpl_rl',
        'TIMEOUT': 3600,  # 1 heure
    },
}

# Utiliser Redis pour les sessions Django
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Cache keys pour les différentes ressources
CACHE_KEYS = {
    'producers_list': 'producers:list:{category}:{search}:{page}',
    'producers_nearby': 'producers:nearby:{lat}:{lng}:{radius}:{page}',
    'producer_detail': 'producer:detail:{id}',
    'categories_list': 'categories:list',
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE_MB', default=10, cast=int) * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
ALLOWED_IMAGE_EXTENSIONS = config('ALLOWED_IMAGE_EXTENSIONS', default='jpg,jpeg,png,webp', cast=lambda v: [s.strip() for s in v.split(',')])

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'custom_auth.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'config.throttling.RedisAnonRateThrottle',
        'config.throttling.RedisUserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/hour',
        'user': '2000/hour',
        'burst_anon': '20/minute',
        'burst_user': '100/minute',
    },
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_ACCESS_TOKEN_LIFETIME_HOURS', default=1, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
# These settings are critical for production security

# SSL/TLS configuration - enable only if SSL is configured
USE_SSL = config('USE_SSL', default='False', cast=bool)

if not DEBUG:
    # Production security settings
    if USE_SSL:
        # Force HTTPS in production when SSL is enabled
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_HSTS_SECONDS = 31536000  # 1 year
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
    else:
        # Warning: Running without SSL in production is insecure
        SECURE_SSL_REDIRECT = False
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
    
    # Additional security headers for production
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
else:
    # Development settings - less strict
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Security headers (always active)
SECURE_BROWSER_XSS_FILTER = True  # Deprecated but harmless
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
X_CONTENT_TYPE_OPTIONS = 'nosniff'
REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Production-ready logging with file rotation and structured output
LOG_LEVEL = config('LOG_LEVEL', default='INFO' if not DEBUG else 'DEBUG')
LOG_DIR = BASE_DIR / 'logs'
# Try to create log directory, but don't fail if permissions are insufficient
try:
    LOG_DIR.mkdir(exist_ok=True)
    # Test write permissions
    test_file = LOG_DIR / '.test_write'
    test_file.touch()
    test_file.unlink()
    LOG_DIR_WRITABLE = True
except (OSError, PermissionError):
    LOG_DIR_WRITABLE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        # JSON formatter (optional, requires pythonjsonlogger package)
        # Uncomment and install pythonjsonlogger to use:
        # 'json': {
        #     '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        #     'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        # },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',  # Use 'json' if pythonjsonlogger is installed
            'level': LOG_LEVEL,
        },
    },
    'root': {
        'handlers': (
            ['console', 'file', 'error_file'] 
            if (not DEBUG and LOG_DIR_WRITABLE) 
            else ['console']
        ),
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': (
                ['console', 'file', 'error_file'] 
                if (not DEBUG and LOG_DIR_WRITABLE) 
                else ['console']
            ),
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'] if (not DEBUG and LOG_DIR_WRITABLE) else ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file'] if (not DEBUG and LOG_DIR_WRITABLE) else ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': (
                ['console', 'file'] 
                if (not DEBUG and LOG_DIR_WRITABLE) 
                else ['console']
            ),
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Add file handlers only if log directory is writable
if LOG_DIR_WRITABLE and not DEBUG:
    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(LOG_DIR / 'django.log'),
        'maxBytes': 1024 * 1024 * 10,  # 10 MB
        'backupCount': 5,
        'formatter': 'verbose',
        'level': 'INFO',
        'filters': ['require_debug_false'],
    }
    LOGGING['handlers']['error_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(LOG_DIR / 'django_errors.log'),
        'maxBytes': 1024 * 1024 * 10,  # 10 MB
        'backupCount': 5,
        'formatter': 'verbose',
        'level': 'ERROR',
    }

