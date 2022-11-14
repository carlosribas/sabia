import mercadopago
from django.conf import settings


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
                    'title': config['title'],
                    'quantity': 1,
                    'unit_price': config['unit_price']
                },
            ],
            'payment_methods': {
                'installments': config['installments']
            },
        }
