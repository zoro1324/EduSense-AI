from datetime import timedelta
from pathlib import Path

from decouple import Config, RepositoryEnv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / ".env"
config = Config(RepositoryEnv(ENV_PATH))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = ["*"]


# Application definition

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
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

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

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='edusense_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'api.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOWED_ORIGINS = [config('FRONTEND_URL', default='http://localhost:5173')]
CORS_ALLOW_CREDENTIALS = True

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM', default='whatsapp:+14155238886')
TWILIO_SMS_FROM = config('TWILIO_SMS_FROM', default='')
GROQ_API_KEY = config('GROQ_API_KEY', default='')
ADMIN_PHONE = config('ADMIN_PHONE', default='')
SCHOOL_NAME = config('SCHOOL_NAME', default='Your School Name')
ESP32_DEVICE_TOKEN = config('ESP32_DEVICE_TOKEN', default='')
ESP32_FACE_MATCH_THRESHOLD = config('ESP32_FACE_MATCH_THRESHOLD', cast=float, default=0.6)
ESP32_DEFAULT_PERIOD = config('ESP32_DEFAULT_PERIOD', cast=int, default=1)

ENGAGEMENT_MONITOR_AUTOSTART = config('ENGAGEMENT_MONITOR_AUTOSTART', cast=bool, default=True)
ENGAGEMENT_MONITOR_ENABLED = config('ENGAGEMENT_MONITOR_ENABLED', cast=bool, default=True)
ENGAGEMENT_CAMERA_SOURCE = config('ENGAGEMENT_CAMERA_SOURCE', default='')
ENGAGEMENT_WEBCAM_INDEX = config('ENGAGEMENT_WEBCAM_INDEX', cast=int, default=0)
ENGAGEMENT_WEBCAM_FALLBACK = config('ENGAGEMENT_WEBCAM_FALLBACK', cast=bool, default=True)
ENGAGEMENT_MODEL_PATH = config(
    'ENGAGEMENT_MODEL_PATH',
    default=str((BASE_DIR.parent / 'models' / 'engagements' / 'yolov8n-pose.pt').resolve()),
)
ENGAGEMENT_CONF_THRESHOLD = config('ENGAGEMENT_CONF_THRESHOLD', cast=float, default=0.3)
ENGAGEMENT_IMAGE_SIZE = config('ENGAGEMENT_IMAGE_SIZE', cast=int, default=640)
ENGAGEMENT_LOG_INTERVAL_SECONDS = config('ENGAGEMENT_LOG_INTERVAL_SECONDS', cast=int, default=10)
ENGAGEMENT_RECONNECT_DELAY_SECONDS = config('ENGAGEMENT_RECONNECT_DELAY_SECONDS', cast=float, default=2.0)
ENGAGEMENT_MAX_FPS = config('ENGAGEMENT_MAX_FPS', cast=int, default=0)
ENGAGEMENT_SHOW_WINDOW = config('ENGAGEMENT_SHOW_WINDOW', cast=bool, default=False)
ENGAGEMENT_WINDOW_TITLE = config('ENGAGEMENT_WINDOW_TITLE', default='Classroom Engagement Monitor')
ENGAGEMENT_CLASS_NAME = config('ENGAGEMENT_CLASS_NAME', default='Classroom A')
ENGAGEMENT_PERIOD = config('ENGAGEMENT_PERIOD', cast=int, default=1)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
