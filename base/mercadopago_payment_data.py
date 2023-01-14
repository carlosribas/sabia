ID_SEPARATOR = '&'


class MercadoPagoPaymentData:

    def __init__(self, payment_data):
        self.payment_data = payment_data

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
