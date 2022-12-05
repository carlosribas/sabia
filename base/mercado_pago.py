import mercadopago
from django.conf import settings
from django.urls import reverse


class MercadoPago:

    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    def get_preference(self, config):
        preference_data = self.set_preference_data(config)
        preference = self.sdk.preference().create(preference_data)
        # TODO: treat errors!

        return preference

    @staticmethod
    def set_preference_data(config):
        return {
            'items': [
                {
                    'id': config['id'],
                    'title': config['title'],
                    'quantity': 1,
                    'unit_price': config['unit_price'],
                },
            ],
            'payer': {'email': config['payer_email']},
            'payment_methods': {
                'installments': config['installments']
            },
            'back_urls': {
                'success': settings.BASE_URL + reverse('course_paid'),
                'failure': settings.BASE_URL + reverse('course_paid'),
                'pending': settings.BASE_URL + reverse('course_paid'),
            },
        }
