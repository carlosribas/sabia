import requests
from django.conf import settings

END_POINT = 'https://api.mercadopago.com/v1/payments/'
FAILURE_STATUS = 'failure'
PENDING_STATUS = 'pending'
SUCCESS_STATUS = 'approved'
IN_PROCESS_STATUS = 'in_process'
ID_SEPARATOR = '&'


class MercadoPagoAPI:
    """Method fetch_payment_data initializes the payment_data property with payment
    data fetched from the API. Call it before the other methods."""

    def __init__(self, payment_id):
        self.endpoint = END_POINT + payment_id
        self.headers = {'Authorization': 'Bearer ' + settings.MERCADO_PAGO_ACCESS_TOKEN}
        self.payment_data = None
        self.payment_not_found_ = None

    def payment_not_found(self):
        return self.payment_not_found_

    def fetch_payment_data(self):
        # TODO: treat http request errors
        self.payment_data = requests.get(url=self.endpoint, headers=self.headers).json()
        self.payment_not_found_ = self.payment_data['status'] == 404

        return self.payment_data

    def get_payment_id(self):
        return self.payment_data['id']

    def get_course_id(self):
        item_id = self.payment_data['additional_info']['items'][0]['id']
        course_id = item_id.split(ID_SEPARATOR)[0]
        return course_id

    def get_payer_email(self):
        item_id = self.payment_data['additional_info']['items'][0]['id']
        email = ID_SEPARATOR.join(item_id.split(ID_SEPARATOR)[1:-1])

        return email

    def get_payment_status(self):
        return self.payment_data['status']

    def coupon_used(self):
        item_id = self.payment_data['additional_info']['items'][0]['id']
        return item_id[-1] != ID_SEPARATOR

    def get_coupon(self):
        if self.coupon_used():
            item_id = self.payment_data['additional_info']['items'][0]['id']
            return item_id.split(ID_SEPARATOR)[-1]
