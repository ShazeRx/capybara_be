import os

import dj_database_url
from dotenv import load_dotenv

load_dotenv()
DEBUG = False

ALLOWED_HOSTS = [os.environ.get('BASE_URL')]

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
