from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from base.mercado_pago import MercadoPago


class TestMercadoPago(TestCase):

    def setUp(self):
        mercadopago = MercadoPago()
        self.course_id = 3
        config = {'id': self.course_id, 'title': 'Example Course', 'unit_price': 100,
                  'installments': 1}
        self.preference = mercadopago.get_preference(config)

    def test_mercadopago_creates_preference(self):
        self.assertEqual(self.preference['status'], HTTPStatus.CREATED)

    def test_mercadopago_generates_right_preference(self):
        self.assertEqual(
            self.preference['response']['items'][0]['id'], str(self.course_id))
        self.assertEqual(
            self.preference['response']['items'][0]['title'], 'Example Course')
        self.assertEqual(self.preference['response']['items'][0]['unit_price'], 100)
        self.assertEqual(
            self.preference['response']['payment_methods']['installments'], 1)

    def test_mercadopago_generates_right_preference_back_urls(self):
        self.assertEqual(self.preference['response']['back_urls']['success'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(self.preference['response']['back_urls']['failure'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(self.preference['response']['back_urls']['pending'],
                         settings.BASE_URL + reverse('course_paid'))
