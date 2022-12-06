import datetime
import json
from http import HTTPStatus
from unittest.mock import patch, call

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse, resolve
from decimal import Decimal as Dec, ROUND_HALF_UP

from base.mercado_pago_api import FAILURE_STATUS, SUCCESS_STATUS, PENDING_STATUS
from base.tests.test_integration.test_mercado_pago import preference_mock
from base.tests.test_mercado_pago_api import api_get_payment_mock
from sabia.settings.local import MERCADO_PAGO_WEBHOOK_TOKEN
from userauth.models import CustomUser, VET
from base.models import Course, CourseUser, CourseUserCoupon, ENROLL
from base.views import course_list, course_registration, material, my_course, \
    payment_complete, mercado_pago_webhook

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


class CourseTestCase(TestCase):
    def setUp(self):
        """Configure authentication and variables to start each test"""
        self.user = CustomUser.objects.create_user(
            username=USER_USERNAME,
            email=USER_EMAIL,
            password=USER_PWD,
            academic_background=VET
        )
        self.user.is_staff = True
        self.user.save()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.course_1 = Course.objects.create(name="course 01", vacancies=0)
        self.course_2 = Course.objects.create(
            name="course 02",
            start_date=datetime.date.today() + datetime.timedelta(days=15),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            vacancies=5
        )
        self.course_3 = Course.objects.create(
            name="course 03",
            start_date=datetime.date.today() + datetime.timedelta(days=15),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            vacancies=5,
            price=100,
        )

    ######################
    # course_list
    ######################
    def test_course_status_code(self):
        url = reverse('cursos')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_course_template(self):
        url = reverse('cursos')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'base/course_list.html')

    def test_course_url_resolves_course_view(self):
        view = resolve('/cursos')
        self.assertEquals(view.func, course_list)

    def test_course_exists(self):
        courses = Course.objects.all()
        self.assertEqual(courses.count(), 3)

    ######################
    # my_course
    ######################
    def test_my_course_status_code(self):
        url = reverse('my_course')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_my_course_template(self):
        url = reverse('my_course')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'base/my_course.html')

    def test_my_course_url_resolves_my_course_view(self):
        view = resolve('/cursos/meus-cursos')
        self.assertEquals(view.func, my_course)

    ######################
    # course_registration
    ######################
    def test_course_registration_status_code(self):
        url = reverse('enroll', args=(self.course_1.pk,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_course_registration_template(self):
        url = reverse('enroll', args=(self.course_1.pk,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'base/course_registration.html')

    def test_course_registration_url_resolves_course_registration_view(self):
        view = resolve('/cursos/1')
        self.assertEquals(view.func, course_registration)

    @patch('base.mercado_pago.MercadoPago.get_preference')
    @patch('base.mercado_pago.mercadopago.SDK')
    def test_course_registration_generates_mercadopago_preference(
            self, mercado_pago_sdk_mock, get_preference):
        preference_config = {
            'id': str(self.course_3.id) + '&' + self.user.email + '&',
            'title': self.course_3.name, 'unit_price': float(self.course_3.price),
            'installments': 1, 'payer_email': self.user.email
        }
        preference_mock_data = preference_mock(preference_config)
        # TODO: it's necessary to verify the config that is called
        get_preference.return_value = preference_mock_data

        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')

        self.assertEqual(get_preference.call_args, call(preference_config))

        self.assertEqual(
            preference['items'][0]['id'],
            str(self.course_3.id) + '&' + self.user.email + '&')
        self.assertEqual(preference['items'][0]['title'], self.course_3.name)
        self.assertEqual(preference['items'][0]['unit_price'], self.course_3.price)
        self.assertEqual(preference['payment_methods']['installments'], 1)
        self.assertEqual(preference['payer']['email'], self.user.email)

    @patch('base.mercado_pago.MercadoPago.get_preference')
    @patch('base.mercado_pago.mercadopago.SDK')
    def test_course_registration_sends_mercadopago_public_key(
            self, mercado_pago_sdk_mock, get_preference):
        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        public_key = response.context.get('public_key')
        self.assertEqual(public_key, settings.MERCADO_PAGO_PUBLIC_KEY)

    @patch('base.mercado_pago.MercadoPago.get_preference')
    @patch('base.mercado_pago.mercadopago.SDK')
    def test_course_registration_generates_mercadopago_preference_price_gt_100(
            self, mercado_pago_sdk_mock, get_preference):
        self.course_3.price = 101
        self.course_3.save()

        preference_config = {
            'id': str(self.course_3.id) + '&' + self.user.email + '&',
            'title': str(self.course_3), 'unit_price': float(self.course_3.price),
            'installments': 4, 'payer_email': self.user.email
        }

        preference_mock_data = preference_mock(preference_config)
        get_preference.return_value = preference_mock_data

        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')

        self.assertEqual(get_preference.call_args, call(preference_config))

        self.assertEqual(
            preference['items'][0]['id'],
            str(self.course_3.id) + '&' + self.user.email + '&')
        self.assertEqual(preference['items'][0]['title'], self.course_3.name)
        self.assertEqual(preference['items'][0]['unit_price'], self.course_3.price)
        self.assertEqual(preference['payment_methods']['installments'], 4)

    def test_course_registration_does_not_generate_mercado_preference_if_not_price(
            self):
        url = reverse('enroll', args=(self.course_2.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')
        self.assertIsNone(preference)

    def test_course_registration_does_not_send_mercadopago_public_key_if_not_price(
            self):
        url = reverse('enroll', args=(self.course_2.pk,))
        response = self.client.get(url)
        public_key = response.context.get('public_key')
        self.assertIsNone(public_key)

    @patch('base.mercado_pago.MercadoPago.get_preference')
    @patch('base.mercado_pago.mercadopago.SDK')
    def test_course_registration_applies_coupon_generates_right_preference(
            self, mercado_pago_sdk_mock, get_preference):
        self.course_3.price = 101
        self.course_3.save()

        coupon_code = CourseUserCoupon.objects.create(
            course=self.course_3,
            user=self.user,
            code='test',
            discount=10,
            valid_from=datetime.datetime.now(),
            valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
        )

        # The way price coupon is figured out in the view
        discount = Dec(coupon_code.discount / 100) \
            .quantize(Dec('.01'), rounding=ROUND_HALF_UP)
        course_price = self.course_3.price - (self.course_3.price * discount) \
            .quantize(Dec('.01'), rounding=ROUND_HALF_UP)

        preference_config = {
            'id': str(self.course_3.id) + '&' + self.user.email + '&' + coupon_code.code,
            'title': self.course_3.name, 'unit_price': float(course_price),
            'installments': 4, 'payer_email': self.user.email
        }

        # Mock preference sdk create response and set item values to the final result
        # based on the call of get_preference with the arguments bellow
        preference_mock_data = preference_mock(preference_config)
        get_preference.return_value = preference_mock_data

        data = {'content': self.course_3.pk, 'action': 'code', 'code': coupon_code.code}
        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.post(url, data)
        preference = response.context.get('preference')

        self.assertEqual(get_preference.call_args, call(preference_config))

        self.assertEqual(
            preference['items'][0]['id'],
            str(self.course_3.id) + '&' + self.user.email + '&' + coupon_code.code)

    def test_course_registration_pre_booking(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking successful')

    def test_course_registration_pre_booking_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user,
                                  status='pre-booking')
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking-unsubscribe',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking canceled successfully')

    def test_course_registration_enroll(self):
        self.data = {
            'content': self.course_2.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

    def test_course_registration_enroll_failed(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]),
                         'Sorry, there are no more vacancies for this course')

    def test_course_registration_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user, status='enroll')
        self.data = {
            'content': self.course_1.pk,
            'action': 'unsubscribe',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Unsubscribe successfully')

    def test_course_user_coupon_not_found(self):
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'foo'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]), 'Coupon not found')

    def test_course_user_coupon_invalid_user(self):
        new_user = CustomUser.objects.create_user(
            username='John',
            email='john@example.com',
            password='pass',
            academic_background=VET
        )
        CourseUserCoupon.objects.create(
            course=self.course_3,
            user=new_user,
            code='test',
            discount=10,
            valid_from=datetime.datetime.now(),
            valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'test'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]), 'Coupon not found')

    @patch('base.mercado_pago.MercadoPago.get_preference')
    @patch('base.mercado_pago.mercadopago.SDK')
    def test_course_user_coupon_ok(self, mercado_pago_sdk_mock, get_preference):
        CourseUserCoupon.objects.create(
            course=self.course_3,
            user=self.user,
            code='test',
            discount=10,
            valid_from=datetime.datetime.now(),
            valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'test'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)),
                                    self.data)
        self.assertEqual(response.context[0]['price'], 90.00)
        self.assertEqual(response.context[0]['price1x'], 85.50)
        self.assertEqual(response.context[0]['price2x'], 45.00)
        self.assertEqual(response.context[0]['price3x'], 30.00)
        self.assertEqual(response.context[0]['price4x'], 22.50)

    def test_course_user_coupon_free_registration(self):
        CourseUserCoupon.objects.create(
            course=self.course_3,
            user=self.user,
            code='test',
            discount=100,
            valid_from=datetime.datetime.now(),
            valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'test'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]),
                         'Coupon applied successfully. This course is now free!')

    def test_course_user_coupon_invalid_date(self):
        CourseUserCoupon.objects.create(
            course=self.course_3,
            user=self.user,
            code='test',
            discount=10,
            valid_from=datetime.datetime.now() - datetime.timedelta(days=5),
            valid_to=datetime.datetime.now() - datetime.timedelta(days=1)
        )
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'test'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)),
                                    self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]), 'Coupon not found')

    ######################
    # material
    ######################
    def test_material_status_code(self):
        url = reverse('material')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_material_template(self):
        url = reverse('material')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'base/material.html')

    def test_material_url_resolves_my_course_view(self):
        view = resolve('/material')
        self.assertEquals(view.func, material)


@patch('base.mercado_pago_api.requests.get')
class CoursePaymentTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=USER_USERNAME,
            email=USER_EMAIL,
            password=USER_PWD,
            academic_background=VET
        )

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        # TODO: see Bidx1 for Fixtures
        self.course = Course.objects.create(
            name="awesome course",
            start_date=datetime.date.today() + datetime.timedelta(days=15),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            vacancies=5,
            price=100,
        )

    def test_finish_mercadopago_payment_redirects_to_course_page(
            self, mock_api_get_payment_data):
        # TODO: see Bidx1 to reproduce test with other status parameters
        mock_api_get_payment_data.return_value.json.return_value = \
            self.mercadopago_api_get_payment_mock(FAILURE_STATUS)
        # Other parameters can be ommited
        url = reverse('course_paid') + '?payment_id=123&status=' + FAILURE_STATUS
        response = self.client.get(url)

        self.assertRedirects(response, reverse('enroll', args=(self.course.pk,)))

    def test_mercadopago_payment_failure_status_redirects_to_course_page_with_message(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = \
            self.mercadopago_api_get_payment_mock(FAILURE_STATUS)
        # Other parameters can be ommited
        url = reverse('course_paid') + '?payment_id=123&status=' + FAILURE_STATUS
        response = self.client.get(url, follow=True)

        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'There was an error with the payment')

    def test_mercadopago_payment_success_status_redirects_to_course_page_with_message(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = \
            self.mercadopago_api_get_payment_mock(SUCCESS_STATUS)
        # Other parameters can be ommited
        url = reverse('course_paid') + '?payment_id=123&status=' + SUCCESS_STATUS
        response = self.client.get(url, follow=True)

        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Payment Successful')

    # def test_mercadopago_payment_success_increments_registered_students(
    #         self, mock_api_get_payment_data):
    #     mock_api_get_payment_data.return_value.json.return_value = \
    #         self.mercadopago_api_get_payment_mock(SUCCESS_STATUS)
    #     # Other parameters can be ommited
    #     url = reverse('course_paid') + '?payment_id=123&status=' + SUCCESS_STATUS
    #     self.client.get(url, follow=True)
    #
    #     course = Course.objects.first()
    #     self.assertEqual(course.registered, 1)

    # def test_mercadopago_payment_success_creates_course_user(
    #         self, mock_api_get_payment_data):
    #     # TODO: mock sdk for this and others
    #     mock_api_get_payment_data.return_value.json.return_value = \
    #         self.mercadopago_api_get_payment_mock(SUCCESS_STATUS)
    #     # Other parameters can be ommited
    #     url = reverse('course_paid') + '?payment_id=123&status=' + SUCCESS_STATUS
    #     self.client.get(url, follow=True)
    #
    #     course_user = CourseUser.objects.first()
    #     self.assertEqual(course_user.payment_id, '123')
    #     self.assertEqual(course_user.payment_status, SUCCESS_STATUS)
    #     self.assertEqual(course_user.user, self.user)

    def test_mercadopago_payment_pending_status_redirects_to_course_page_with_message(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = \
            self.mercadopago_api_get_payment_mock(PENDING_STATUS)
        # Other parameters can be ommited
        url = reverse('course_paid') + '?payment_id=123&status=' + PENDING_STATUS
        response = self.client.get(url, follow=True)

        message = list(get_messages(response.wsgi_request))
        # TODO: see assertContains or equivalent for messages
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Waiting for payment confirmation')

    # def test_payment_complete_with_coupon_url_resolves_payment_complete_view(
    #         self, mock_api_get_payment_data):
    #     view = resolve('/cursos/finalizado/coupon/A123')
    #     self.assertEqual(view.func, payment_complete)

    # def test_mercadopago_payment_success_with_coupon_url_creates_course_object_with_coupon_code(
    #         self, mock_api_get_payment_data):
    #     mock_api_get_payment_data.return_value.json.return_value = \
    #         self.mercadopago_api_get_payment_mock(SUCCESS_STATUS)
    #     coupon_code = CourseUserCoupon.objects.create(
    #         course=self.course,
    #         user=self.user,
    #         code='A123',
    #         discount=10,
    #         valid_from=datetime.datetime.now(),
    #         valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
    #     )
    #
    #     # Other parameters can be ommited
    #     url = reverse('course_paid_coupon_applied', args=(coupon_code.code,)) \
    #         + '?payment_id=123&status=' + SUCCESS_STATUS
    #     self.client.get(url, follow=True)
    #
    #     course_user = CourseUser.objects.first()
    #     self.assertEqual(course_user.coupon_used, coupon_code.code)

    def mercadopago_api_get_payment_mock(self, status):
        # TODO: use mock from mercadopago api
        # Real mercadopago response have several other fields that are ommited here
        return {
            "additional_info": {
                "authentication_code": None,
                "available_balance": None,
                "ip_address": "189.121.200.222",
                "items": [
                    {
                        "category_id": None,
                        "description": None,
                        "id": str(self.course.id),
                        "picture_url": None,
                        "quantity": "1",
                        "title": "Radiologia pra clínicos: Doenças respiratórias",
                        "unit_price": "464.54998779296875"
                    }
                ],
            },
            "status": status,
        }


def webhook_data_mock(payment_status, payment_id):
    return {
        'action': payment_status,
        'api_version': 'v1',
        'data': {
            'id': str(payment_id)
        },
        'date_created': '2022-11-16T19:49:05Z',
        'id': 103945298430,
        'live_mode': False,
        'type': 'payment',
        'user_id': '269058111'
    }


@patch('base.mercado_pago_api.requests.get')
class MercadoPagoWebookTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=USER_USERNAME,
            email=USER_EMAIL,
            password=USER_PWD,
            academic_background=VET
        )
        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        # TODO: see Bidx1 for Fixtures
        self.course = Course.objects.create(
            name="awesome course",
            start_date=datetime.date.today() + datetime.timedelta(days=15),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            vacancies=5,
            price=150,
        )

        self.payment_mock = api_get_payment_mock()
        self.payment_mock['additional_info']['items'][0]['id'] = \
            str(self.course.id) + '&' + self.user.email + '&'

    def test_webhook_url_resolves_webhook_view(self, mock_api_get_payment_data):
        view = resolve('/mercadopago_webhook/' + MERCADO_PAGO_WEBHOOK_TOKEN)
        self.assertEquals(view.func, mercado_pago_webhook)

    def test_webhook_url_incorrect_token_returns_404(self, mock_api_get_payment_data):
        response = self.client.post(
            reverse(mercado_pago_webhook, args=('FAKE_TOKEN',)),
            data=json.dumps({'a': 1}), content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_webhook_url_right_token_returns_200(self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', str(self.payment_mock['id']))

        response = self.client.post(
            reverse(mercado_pago_webhook, args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
            data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_webhook_url_doesnt_find_payment_data_and_status_is_updated_returns_200(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.updated', self.payment_mock['id'])

        response = self.client.post(reverse(mercado_pago_webhook,
                                            args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                                    data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_webhook_url_doesnt_find_payment_data_and_status_is_updated_send_email(
            self, mock_api_get_payment_data):
        # TODO
        ...

    def test_webhook_url_payment_created_and_approved_create_course_user(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', self.payment_mock['id'])

        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')
        course_user = CourseUser.objects.first()
        self.assertEqual(course_user.status, ENROLL)
        self.assertEqual(course_user.user, self.user)
        self.assertEqual(course_user.payment_id, data['data']['id'])
        self.assertEqual(course_user.payment_status, SUCCESS_STATUS)

    def test_webhook_url_payment_created_and_approved_create_course_user_with_coupon(
            self, mock_api_get_payment_data):
        coupon_code = 'A123'
        self.payment_mock['additional_info']['items'][0]['id'] = \
            str(self.course.id) + '&' + self.user.email + '&' + coupon_code
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', self.payment_mock['id'])

        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')
        course_user = CourseUser.objects.first()
        self.assertEqual(course_user.coupon_used, coupon_code)
        self.assertEqual(course_user.payment_status, SUCCESS_STATUS)

    def test_webhook_url_payment_created_and_approved_increments_registered_students(
            self, mock_api_get_payment_data):
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', self.payment_mock['id'])

        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')
        course_updated = Course.objects.first()
        self.assertEqual(course_updated.registered, self.course.registered + 1)

    def test_webhook_url_payment_created_and_pending_create_course_user(
            self, mock_api_get_payment_data):
        # TODO: see Bidx1 to join this test with
        #  test_webhook_url_payment_created_and_approved_create_course_user
        self.payment_mock['status'] = PENDING_STATUS
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', self.payment_mock['id'])

        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')
        course_user = CourseUser.objects.first()
        self.assertEqual(course_user.status, ENROLL)
        self.assertEqual(course_user.user, self.user)
        self.assertEqual(course_user.payment_id, data['data']['id'])
        self.assertEqual(course_user.payment_status, PENDING_STATUS)

    def test_webhook_url_payment_created_and_pending_increments_registered_students(
            self, mock_api_get_payment_data):
        # TODO: see Bidx1 to join this test with
        #  test_webhook_url_payment_created_and_approved_increments_registered_students
        self.payment_mock['status'] = PENDING_STATUS
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.created', self.payment_mock['id'])

        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')
        course_updated = Course.objects.first()
        self.assertEqual(course_updated.registered, self.course.registered + 1)

    def test_payment_updated_to_success_after_payment_pending_updates_payment_status(
            self, mock_api_get_payment_data):
        self.payment_mock['status'] = SUCCESS_STATUS
        mock_api_get_payment_data.return_value.json.return_value = self.payment_mock
        data = webhook_data_mock('payment.updated', self.payment_mock['id'])

        CourseUser.objects.create(
            course=self.course,
            user=self.user,
            status=ENROLL,
            payment_id=self.payment_mock['id'],
            payment_status=PENDING_STATUS,
        )
        self.client.post(reverse(mercado_pago_webhook,
                                 args=(MERCADO_PAGO_WEBHOOK_TOKEN,)),
                         data=json.dumps(data),
                         content_type='application/json')

        # No other CourseUser object was created
        self.assertEqual(len(CourseUser.objects.all()), 1)

        course_user = CourseUser.objects.first()
        self.assertEqual(course_user.payment_status, SUCCESS_STATUS)
