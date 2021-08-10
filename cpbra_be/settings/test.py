from dotenv import load_dotenv

load_dotenv()
from .base import *
SECRET_KEY = 'secret'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }
}
CHANNEL_LAYERS = {'default':
    {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
