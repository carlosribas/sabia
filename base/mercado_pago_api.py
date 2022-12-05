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
        self.payment_data = None

    # TODO: change to fetch_payment_data
    def get_payment_data(self):
        # TODO: treat errors
        self.payment_data = requests.get(url=self.endpoint, headers=self.headers).json()
        return self.payment_data

    def get_payment_id(self):
        return self.payment_data['id']

    def get_course_id(self):
        # TODO: try catch or if to get payment data first (for this and the others)
        item_id = self.payment_data['additional_info']['items'][0]['id']
        course_id = item_id.split('&')[0]
        return course_id

    def get_payer_email(self):
        item_id = self.payment_data['additional_info']['items'][0]['id']
        email = '&'.join(item_id.split('&')[1:-1])

        return email

    def get_payment_status(self):
        return self.payment_data['status']

    def coupon_used(self):
        item_id = self.payment_data['additional_info']['items'][0]['id']
        return item_id[-1] != '&'

    def get_coupon(self):
        if self.coupon_used():
            item_id = self.payment_data['additional_info']['items'][0]['id']
            return item_id.split('&')[-1]
