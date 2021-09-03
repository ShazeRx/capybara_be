"""
Settings for dev environment
"""
import os

import dj_database_url
from dotenv import load_dotenv

load_dotenv()
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_URL'))],
        },
    },
}
AUTH_PASSWORD_VALIDATORS = []
