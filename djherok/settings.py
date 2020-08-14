"""
Django settings for djherok project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '^+2aug4bly'
SECRET_KEY = os.environ['SECRET_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
DEBUG = True
# DEBUG = bool( os.environ.get('DJANGO_DEBUG', True) )

# DEBUG_PROPAGATE_EXCEPTIONS = True

# TASTYPIE_FULL_DEBUG = True
# SECURE_SSL_REDIRECT = True

EMAIL_HOST = 'smtp.bk.ru'
EMAIL_HOST_USER = 'si.recruit@bk.ru'
DEFAULT_FROM_EMAIL = 'si.recruit@bk.ru'
EMAIL_HOST_PASSWORD = os.environ['Si_EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587
# EMAIL_PORT = 465
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True


ALLOWED_HOSTS = ['djherok.herokuapp.com',
                 '127.0.0.1',
                 '.ngrok.io',
                 '.localhost.run',
                 '192.168.0.3',
                 'localhost',
                 # 'g62.dlinkddns.com',
                 # '178.204.133.11',
                 # '0.0.0.0',
                 ]

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'si.apps.SiConfig',
    'weatherBot.apps.WeatherBotConfig',
    'bitr24.apps.Bitr24Config',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djherok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'djherok.wsgi.application'

FIXTURE_DIRS = (
   # '/path/to/myapp/fixtures/',
   os.path.join(BASE_DIR, 'fixtures'),
)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'TIME_ZONE': 'Europe/Moscow',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'djherok_bd',
        'NAME': os.environ['DB_NAME'],
        # 'USER': 'djherok_user',
        'USER': os.environ['DB_USER'],
        # 'PASSWORD': 'passw..psql..',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
        # 'HOST' : '127.0.0.1',
        # 'PORT' : '5432',
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Moscow'
USE_TZ = True

USE_I18N = True

USE_L10N = True

# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# STATIC_ROOT = "/home/marat/PycharmProjects/djherok/static/"
STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'bitr24/static'),
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'si/static'),
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

