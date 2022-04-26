'''Use this for production'''

from .base import *

DEBUG = False
ALLOWED_HOSTS += ['']
WSGI_APPLICATION = 'home.wsgi.prod.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STRIPE_PUBLISH_KEY = 'pk_test_fNvM4Ol4vGCCBEXfhtkVu91v00qKo5oSrQ'
STRIPE_SECRET_KEY = 'sk_test_OOiz0ROEj2hZXhhthAzEOQut004g4pydoC'

CORS_ORIGIN_ALLOW_ALL = True
