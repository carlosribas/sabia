import socket
import sys
import logging

from .base import *

# Gateway IP of the docker container
ip = socket.gethostbyname(socket.gethostname())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-sw(#_=0oy36fh3#ebxj@==67jn%cwtvx^60ya@!b7@2rkumk)'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# Changed to run tests on github
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# reCaptcha settings
RECAPTCHA_PUBLIC_KEY = 'dev_fake_public_key'
RECAPTCHA_PRIVATE_KEY = 'dev_fake_private_key'

# enable no captcha
NOCAPTCHA = True

# INSTALLED_APPS = INSTALLED_APPS + [
#     'debug_toolbar',
# ]
#
# MIDDLEWARE = MIDDLEWARE + [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

INTERNAL_IPS = ["127.0.0.1", ip[:-1] + '1']

try:
    from .local import *
except ImportError:
    # Database used to run tests on github
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'sabia',
            'USER': 'sabia',
            'PASSWORD': 'sabia',
            'HOST': 'localhost',
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': './log/log_file.log',
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'base': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
    },
}
# Disable logging when testing
# TODO: maybe a better way.
#  See: https://betterstack.com/community/questions/how-to-disable-logging-while-running-django-unit-tests/ 
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

