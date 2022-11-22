import requests
from django.conf import settings

END_POINT = 'https://api.mercadopago.com/v1/payments/'
# TODO: see Bidx1 for defining constants
FAILURE_STATUS = 'failure'
PENDING_STATUS = 'pending'
SUCCESS_STATUS = 'approved'


class MercadoPagoAPI:

    def __init__(self, payment_id):
        self.endpoint = END_POINT + payment_id
        self.headers = {'Authorization': 'Bearer ' + settings.MERCADO_PAGO_ACCESS_TOKEN}

    def get_payment_data(self):
        # TODO: treat errors
        response_body = requests.get(url=self.endpoint, headers=self.headers).json()
        return response_body

    def get_course_id(self):
        payment_data = self.get_payment_data()
        return payment_data['additional_info']['items'][0]['id']
