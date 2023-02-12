import requests
from django.conf import settings

END_POINT = 'https://api.mercadopago.com/v1/payments/'
FAILURE_STATUS = 'failure'
PENDING_STATUS = 'pending'
SUCCESS_STATUS = 'approved'
IN_PROCESS_STATUS = 'in_process'
REJECTED_STATUS = 'rejected'


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
        response = requests.get(url=self.endpoint, headers=self.headers)
        if response.ok:
            self.payment_data = response.json()
            self.payment_not_found_ = self.payment_data['status'] == 404
            return self.payment_data
        else:
            return None

