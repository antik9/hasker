"""
Django settings for hasker project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import datetime
import os
import sys

import django_heroku
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&&%iyvjl1xcf_6-e_g9+i#yo=y%hkg!cv5_^*vfolu@q2f)pkb'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv('DJANGO_ENV') != 'prod'

# DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'web', 'web:8000', 
        'https://morning-escarpment-46930.herokuapp.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'questions.apps.QuestionsConfig',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'hasker.urls'

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

WSGI_APPLICATION = 'hasker.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if os.getenv('DOCKER_CONTAINER'):
    POSTGRES_HOST = 'db'
else:
    POSTGRES_HOST = '127.0.0.1'

# POSTGRES_HOST = '127.0.0.1'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'hasker',
#         'USER': 'admin',
#         'PASSWORD': 'admin',
#         'HOST': POSTGRES_HOST,
#         'PORT': 5432,
#     },
# }

db_from_env = dj_database_url.config(conn_max_age=500, ssl_require=True)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Default routes

LOGIN_REDIRECT_URL = '/'
BASE_URL = 'localhost:8000'

# Configuration of email service

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = None  # Add your account
EMAIL_HOST_PASSWORD = None  # Add your password
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Number of batches for paginator for different sections of site

BATCH_ON_PAGE = 8
SEARCH_BATCH = 8
ANSWERS_BATCH = 8
TRENDING_BATCH = 5

# Logging configuration

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'strm': sys.stdout,
            },
        },
    }

# REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

# JWT

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1)
}

django_heroku.settings(locals())

