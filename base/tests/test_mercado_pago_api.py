from unittest.mock import patch, Mock

from django.test import TestCase

from base.mercado_pago_api import MercadoPagoAPI
from base.mercadopago_payment_data import ID_SEPARATOR

PAYMENT_ID = 1310422398


def api_get_payment_mock():
    return {
            "acquirer_reconciliation": [],
            "additional_info": {
                "authentication_code": None,
                "available_balance": None,
                "ip_address": "189.121.200.222",
                "items": [
                    {
                        "category_id": None,
                        "description": None,
                        "id": "123" + ID_SEPARATOR + "user@example.com" + ID_SEPARATOR,
                        "picture_url": None,
                        "quantity": "1",
                        "title": "Radiologia pra clínicos: Doenças respiratórias",
                        "unit_price": "464.54998779296875"
                    }
                ],
                "nsu_processadora": None
            },
            "authorization_code": None,
            "binary_mode": False,
            "brand_id": None,
            "build_version": "2.119.1",
            "call_for_authorize_id": None,
            "captured": True,
            "card": {
                "cardholder": {
                    "identification": {
                        "number": "12345678909",
                        "type": "CPF"
                    },
                    "name": "APRO"
                },
                "date_created": "2022-11-17T12:56:13.000-04:00",
                "date_last_updated": "2022-11-17T12:56:13.000-04:00",
                "expiration_month": 11,
                "expiration_year": 2025,
                "first_six_digits": "503143",
                "id": None,
                "last_four_digits": "6351"
            },
            "charges_details": [],
            "collector_id": 269058111,
            "corporation_id": None,
            "counter_currency": None,
            "coupon_amount": 0,
            "currency_id": "BRL",
            "date_approved": "2022-11-17T12:56:13.382-04:00",
            "date_created": "2022-11-17T12:56:13.214-04:00",
            "date_last_updated": "2022-11-17T12:56:13.382-04:00",
            "date_of_expiration": None,
            "deduction_schema": None,
            "description": "Radiologia pra clínicos: Doenças respiratórias",
            "differential_pricing_id": None,
            "external_reference": None,
            "fee_details": [
                {
                    "amount": 23.13,
                    "fee_payer": "collector",
                    "type": "mercadopago_fee"
                }
            ],
            "financing_group": None,
            "id": PAYMENT_ID,
            "installments": 1,
            "integrator_id": None,
            "issuer_id": "24",
            "live_mode": False,
            "marketplace_owner": None,
            "merchant_account_id": None,
            "merchant_number": None,
            "metadata": {},
            "money_release_date": "2022-11-17T12:56:13.382-04:00",
            "money_release_schema": None,
            "money_release_status": None,
            "notification_url": None,
            "operation_type": "regular_payment",
            "order": {
                "id": "6530236222",
                "type": "mercadopago"
            },
            "payer": {
                "first_name": None,
                "last_name": None,
                "email": None,
                "identification": {
                    "number": "32659430",
                    "type": "DNI"
                },
                "phone": {
                    "area_code": None,
                    "number": None,
                    "extension": None
                },
                "type": None,
                "entity_type": None,
                "id": "1230953962"
            },
            "payment_method": {
                "id": "master",
                "type": "credit_card"
            },
            "payment_method_id": "master",
            "payment_type_id": "credit_card",
            "platform_id": None,
            "point_of_interaction": {
                "business_info": {
                    "sub_unit": "checkout_pro",
                    "unit": "online_payments"
                },
                "type": "UNSPECIFIED"
            },
            "pos_id": None,
            "processing_mode": "aggregator",
            "refunds": [],
            "shipping_amount": 0,
            "sponsor_id": None,
            "statement_descriptor": "CRNS13",
            "status": "approved",
            "status_detail": "accredited",
            "store_id": None,
            "taxes_amount": 0,
            "transaction_amount": 464.55,
            "transaction_amount_refunded": 0,
            "transaction_details": {
                "acquirer_reference": None,
                "external_resource_url": None,
                "financial_institution": None,
                "installment_amount": 464.55,
                "net_received_amount": 441.42,
                "overpaid_amount": 0,
                "payable_deferral_period": None,
                "payment_method_reference_id": None,
                "total_paid_amount": 464.55
            }
        }


def api_get_payment_not_found_mock():
    return {
        'message': 'Payment not found', 'error': 'not_found', 'status': 404,
        'cause': [
            {
                'code': 2000, 'description': 'Payment not found',
                'data': '12-12-2022T17:10:45UTC;fa5e2139-8ee9-46b1-8b76-57f895eab9a4'
            }
        ]
    }


@patch('base.mercado_pago_api.requests.get')
class TestMercadoPagoAPI(TestCase):
    def setUp(self):
        self.mercadopago_api = MercadoPagoAPI(payment_id='123')

    def test_fetch_payment_data(self, mock_api_requests_get):
        mock_api_requests_get.return_value = Mock(ok=True)
        mock_api_requests_get.return_value.json.return_value = api_get_payment_mock()
        response = self.mercadopago_api.fetch_payment_data()
        self.assertIsNotNone(response)
        self.assertEqual(response, api_get_payment_mock())

    def test_fetch_payment_data_error(self, mock_api_requests_get):
        mock_api_requests_get.return_value.ok = False
        response = self.mercadopago_api.fetch_payment_data()
        self.assertIsNone(response)

    def test_fetch_payment_data_doesnt_find_payment_data_signals_payment_not_found(
            self, mock_api_requests_get):
        mock_api_requests_get.return_value = Mock(ok=True)
        mock_api_requests_get.return_value.json.return_value = \
            api_get_payment_not_found_mock()
        response = self.mercadopago_api.fetch_payment_data()

        self.assertEqual(response, api_get_payment_not_found_mock())
        self.assertTrue(self.mercadopago_api.payment_not_found())

