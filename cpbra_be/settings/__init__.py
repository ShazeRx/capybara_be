from dotenv import load_dotenv

from .base import *

load_dotenv()

if os.environ['ENV'] == 'prod':
    from .prod import *
if os.environ['ENV'] == 'dev':
    from .dev import *
else:
    from .local import *
