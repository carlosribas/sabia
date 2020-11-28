from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-sw(#_=0oy36fh3#ebxj@==67jn%cwtvx^60ya@!b7@2rkumk)'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar',
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

try:
    from .local import *
except ImportError:
    pass
