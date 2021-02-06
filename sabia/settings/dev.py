import socket

from .base import *

# Gateway IP of the docker container
ip = socket.gethostbyname(socket.gethostname())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-sw(#_=0oy36fh3#ebxj@==67jn%cwtvx^60ya@!b7@2rkumk)'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# reCaptcha settings
RECAPTCHA_PUBLIC_KEY = 'dev_fake_public_key'
RECAPTCHA_PRIVATE_KEY = 'dev_fake_private_key'

# enable no captcha
NOCAPTCHA = True

INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar',
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ["127.0.0.1", ip[:-1] + '1']

try:
    from .local import *
except ImportError:
    pass
