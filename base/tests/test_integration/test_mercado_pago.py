from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from base.mercado_pago import MercadoPago
from base.tests.test_views import USER_USERNAME, USER_EMAIL, USER_PWD
from userauth.models import CustomUser, VET


class TestMercadoPago(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=USER_USERNAME,
            email=USER_EMAIL,
            password=USER_PWD,
            academic_background=VET
        )
        self.client.login(username=USER_USERNAME, password=USER_PWD)

        self.mercadopago = MercadoPago()
        self.course_id = 3
        self.config = {
            'id': self.course_id, 'title': 'Example Course',
            'unit_price': 100, 'installments': 1, 'payer_email': self.user.email
        }

    def test_mercadopago_creates_preference(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['status'], HTTPStatus.CREATED)

    def test_mercadopago_generates_right_preference(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(
            preference['response']['items'][0]['id'], str(self.course_id))
        self.assertEqual(
            preference['response']['items'][0]['title'], 'Example Course')
        self.assertEqual(preference['response']['items'][0]['unit_price'], 100)
        self.assertEqual(
            preference['response']['payment_methods']['installments'], 1)
        self.assertEqual(preference['response']['payer']['email'],
                         self.config['payer_email'])

    def test_mercadopago_generates_right_preference_back_urls(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['response']['back_urls']['success'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(preference['response']['back_urls']['failure'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(preference['response']['back_urls']['pending'],
                         settings.BASE_URL + reverse('course_paid'))

    def test_mercadopago_generates_right_preference_coupon_back_urls(self):
        coupon_code = 'A123'
        preference = self.mercadopago.get_preference(self.config, coupon_code)

        self.assertEqual(preference['response']['back_urls']['success'],
                         settings.BASE_URL
                         + reverse('course_paid_coupon_applied', args=(coupon_code,)))
        self.assertEqual(preference['response']['back_urls']['failure'],
                         settings.BASE_URL
                         + reverse('course_paid_coupon_applied', args=(coupon_code,)))
        self.assertEqual(preference['response']['back_urls']['pending'],
                         settings.BASE_URL
                         + reverse('course_paid_coupon_applied', args=(coupon_code,)))
