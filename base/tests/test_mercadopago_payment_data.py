from django.test import TestCase

from base.mercadopago_payment_data import MercadoPagoPaymentData, ID_SEPARATOR
from base.tests.test_mercado_pago_api import api_get_payment_mock


class TestMercadoPagoPaymentData(TestCase):

    def setUp(self):
        self.payment_data = api_get_payment_mock()
        self.mp_payment_data = MercadoPagoPaymentData(self.payment_data)

    def test_get_payment_id(self):
        self.assertEqual(self.mp_payment_data.get_payment_id(), 1310422398)

    def test_get_course_id(self):
        self.assertEqual(self.mp_payment_data.get_course_id(), '123')

    def test_get_payer_email_without_coupon_in_id(self):
        self.assertEqual(self.mp_payment_data.get_payer_email(), 'user@example.com')

    def test_get_payer_email_when_coupon_isnt_in_id_and_email_has_ID_SEPARATOR_chars(self):
        course_id = '123'
        payer_email = 'user' + ID_SEPARATOR + 'abc@example.co'
        self.payment_data['additional_info']['items'][0]['id'] = \
            course_id + ID_SEPARATOR + payer_email + ID_SEPARATOR
        self.assertEqual(self.mp_payment_data.get_payer_email(), payer_email)

    def test_get_payer_email_with_coupon_in_id(self):
        self.payment_data['additional_info']['items'][0]['id'] += 'COUPON_CODE'
        self.assertEqual(self.mp_payment_data.get_payer_email(), 'user@example.com')

    def test_get_payment_status(self):
        self.assertEqual(self.mp_payment_data.get_payment_status(), 'approved')

    def test_coupon_used_should_return_false(self):
        self.assertEqual(self.mp_payment_data.coupon_used(), False)

    def test_coupon_used_should_return_true(self):
        self.payment_data['additional_info']['items'][0]['id'] += 'COUPON_CODE'
        self.assertEqual(self.mp_payment_data.coupon_used(), True)

    def test_get_coupon(self):
        coupon_code = 'COUPON_CODE'
        self.payment_data['additional_info']['items'][0]['id'] += ID_SEPARATOR + coupon_code
        self.assertEqual(self.mp_payment_data.get_coupon(), coupon_code)
