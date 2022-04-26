'''Use this for development'''

from .base import *
ALLOWED_HOSTS += ['*']
DEBUG = True

WSGI_APPLICATION = 'home.wsgi.dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)
CSRF_TRUSTED_ORIGINS = ['localhost:3000']

STRIPE_PUBLISH_KEY = 'pk_test_fNvM4Ol4vGCCBEXfhtkVu91v00qKo5oSrQ'
STRIPE_SECRET_KEY = 'sk_test_OOiz0ROEj2hZXhhthAzEOQut004g4pydoC'



