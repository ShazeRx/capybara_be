"""
Settings for local environment environment
"""
import os

from dotenv import load_dotenv

load_dotenv()
DEBUG = True
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_URL'),
        'PORT': '5432',
    }
}
CHANNEL_LAYERS = {
    'default':
    {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
AUTH_PASSWORD_VALIDATORS = []