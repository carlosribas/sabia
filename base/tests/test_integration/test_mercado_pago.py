from http import HTTPStatus

from django.test import TestCase

from base.mercado_pago import MercadoPago


class TestMercadoPago(TestCase):

    def test_mercadopago_generates_right_preference(self):
        mercadopago = MercadoPago()
        config = {'title': 'Example Course', 'unit_price': 100, 'installments': 1}
        preference = mercadopago.get_preference(config)

        self.assertEqual(preference['status'], HTTPStatus.CREATED)
        self.assertEqual(preference['response']['items'][0]['title'], 'Example Course')
        self.assertEqual(preference['response']['items'][0]['unit_price'], 100)
        self.assertEqual(preference['response']['payment_methods']['installments'], 1)
