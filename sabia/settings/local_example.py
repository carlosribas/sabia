SECRET_KEY = 'your_secret_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sabia',
        'USER': 'sabia',
        'PASSWORD': 'sabia',
        'HOST': 'db',
    }
}

BASE_URL = 'http://localhost:8000'

EMAIL_HOST = 'your.host.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email@example.com'
EMAIL_HOST_PASSWORD = 'password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# reCaptcha settings
RECAPTCHA_PUBLIC_KEY = 'reCaptcha_public_key'
RECAPTCHA_PRIVATE_KEY = 'reCaptcha_private_key'
# enable no captcha
NOCAPTCHA = True

# Mercado Pago credentials
MERCADO_PAGO_PUBLIC_KEY = ''
MERCADO_PAGO_ACCESS_TOKEN = ''

# Token for Mercado Pago webhook endpoint
# Choose one very long and with a mix of alfanumeric chars and with special chars
MERCADO_PAGO_WEBHOOK_TOKEN = ''
