import os

import vcr

from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from base.mercado_pago import MercadoPago
from userauth.models import CustomUser, VET

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


def preference_mock(config):
    return {
        "status": 201,
        "response": {
            "additional_info": "",
            "auto_return": "",
            "back_urls": {
                "failure": "http://localhost:8000/cursos/finalizado",
                "pending": "http://localhost:8000/cursos/finalizado",
                "success": "http://localhost:8000/cursos/finalizado",
            },
            "binary_mode": False,
            "client_id": "6226796596410548",
            "collector_id": 269058111,
            "coupon_code": None,
            "coupon_labels": None,
            "date_created": "2022-11-24T15:17:26.380-04:00",
            "date_of_expiration": None,
            "expiration_date_from": None,
            "expiration_date_to": None,
            "expires": False,
            "external_reference": "",
            "id": "269058111-c3b7b790-38a7-493a-b43d-151b9b4e9f6a",
            "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=269058111-c3b7b790-38a7-493a-b43d-151b9b4e9f6a",
            "internal_metadata": None,
            "items": [
                {
                    "id": config['id'],
                    "category_id": "",
                    "currency_id": "BRL",
                    "description": "",
                    "title": "course 03",
                    "quantity": 1,
                    "unit_price": config['unit_price'],
                }
            ],
            "marketplace": "NONE",
            "marketplace_fee": 0,
            "metadata": {},
            "notification_url": None,
            "operation_type": "regular_payment",
            "payer": {
                "phone": {"area_code": "", "number": ""},
                "address": {"zip_code": "", "street_name": "", "street_number": None},
                "email": config['payer_email'],
                "identification": {"number": "", "type": ""},
                "name": "",
                "surname": "",
                "date_created": None,
                "last_purchase": None,
            },
            "payment_methods": {
                "default_card_id": None,
                "default_payment_method_id": None,
                "excluded_payment_methods": [{"id": ""}],
                "excluded_payment_types": [{"id": ""}],
                "installments": config['installments'],
                "default_installments": None,
            },
            "processing_modes": None,
            "product_id": None,
            "redirect_urls": {"failure": "", "pending": "", "success": ""},
            "sandbox_init_point": "https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=269058111-c3b7b790-38a7-493a-b43d-151b9b4e9f6a",
            "site_id": "MLB",
            "shipments": {
                "default_shipping_method": None,
                "receiver_address": {
                    "zip_code": "",
                    "street_name": "",
                    "street_number": None,
                    "floor": "",
                    "apartment": "",
                    "city_name": None,
                    "state_name": None,
                    "country_name": None,
                },
            },
            "total_amount": None,
            "last_updated": None,
        },
    }


sabia_vcr = vcr.VCR(
    cassette_library_dir=os.path.dirname(os.path.abspath(__file__)) + '/cassettes',
    path_transformer=vcr.VCR.ensure_suffix('.yaml'))


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
            'id': str(self.course_id) + '&' + self.user.email + '&',
            'title': 'Example Course', 'unit_price': 100, 'installments': 1,
            'payer_email': self.user.email
        }

    @sabia_vcr.use_cassette()
    def test_mercadopago_creates_preference(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['status'], HTTPStatus.CREATED)

    @sabia_vcr.use_cassette()
    def test_mercadopago_generates_right_preference(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['response']['items'][0]['id'],
                         str(self.course_id) + '&' + self.user.email + '&')
        self.assertEqual(
            preference['response']['items'][0]['title'], 'Example Course')
        self.assertEqual(preference['response']['items'][0]['unit_price'], 100)
        self.assertEqual(
            preference['response']['payment_methods']['installments'], 1)
        self.assertEqual(preference['response']['payer']['email'],
                         self.config['payer_email'])

    @sabia_vcr.use_cassette()
    def test_mercadopago_generates_right_preference_coupon_applied(self):
        coupon_code = 'A123'
        self.config['id'] = str(self.course_id) + '&' + self.user.email + '&' + coupon_code
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['response']['items'][0]['id'],
                         str(self.course_id) + '&' + self.user.email + '&' + coupon_code)

    @sabia_vcr.use_cassette()
    def test_mercadopago_generates_right_preference_back_urls(self):
        preference = self.mercadopago.get_preference(self.config)

        self.assertEqual(preference['response']['back_urls']['success'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(preference['response']['back_urls']['failure'],
                         settings.BASE_URL + reverse('course_paid'))
        self.assertEqual(preference['response']['back_urls']['pending'],
                         settings.BASE_URL + reverse('course_paid'))
