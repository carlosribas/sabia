import datetime

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse, resolve

from userauth.models import CustomUser, VET
from base.models import Course, CourseUser, CourseUserCoupon
from base.views import course_list, course_registration, material, my_course

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

    def test_course_registration_generates_mercadopago_preference(self):
        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')
        self.assertEqual(preference['items'][0]['title'], 'course 03')
        self.assertEqual(preference['items'][0]['unit_price'], 100)
        self.assertEqual(preference['payment_methods']['installments'], 1)

    def test_course_registration_sends_mercadopago_public_key(self):
        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        public_key = response.context.get('public_key')
        self.assertEqual(public_key, settings.MERCADO_PAGO_PUBLIC_KEY)

    def test_course_registration_generates_mercadopago_preference_price_gt_100(self):
        self.course_3.price = 101
        self.course_3.save()

        url = reverse('enroll', args=(self.course_3.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')
        self.assertEqual(preference['items'][0]['id'], str(self.course_3.pk))
        self.assertEqual(preference['items'][0]['title'], 'course 03')
        self.assertEqual(preference['items'][0]['unit_price'], 95.95)
        self.assertEqual(preference['payment_methods']['installments'], 4)

    def test_course_registration_does_not_generate_mercado_preference_if_not_price(self):
        url = reverse('enroll', args=(self.course_2.pk,))
        response = self.client.get(url)
        preference = response.context.get('preference')
        self.assertIsNone(preference)

    def test_course_registration_does_not_send_mercadopago_public_key_if_not_price(self):
        url = reverse('enroll', args=(self.course_2.pk,))
        response = self.client.get(url)
        public_key = response.context.get('public_key')
        self.assertIsNone(public_key)

    def test_course_registration_pre_booking(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking successful')

    def test_course_registration_pre_booking_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user, status='pre-booking')
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking-unsubscribe',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking canceled successfully')

    def test_course_registration_enroll(self):
        self.data = {
            'content': self.course_2.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_course_registration_enroll_failed(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Sorry, there are no more vacancies for this course')

    def test_course_registration_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user, status='enroll')
        self.data = {
            'content': self.course_1.pk,
            'action': 'unsubscribe',
        }
        response = self.client.post(reverse("enroll", args=(self.course_1.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Unsubscribe successfully')

    def test_course_user_coupon_not_found(self):
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'foo'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)), self.data)
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
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]), 'Coupon not found')

    def test_course_user_coupon_ok(self):
        CourseUserCoupon.objects.create(
            course=self.course_3,
            user=self.user,
            code='test',
            discount=10,
            valid_from=datetime.datetime.now(),
            valid_to=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.data = {'content': self.course_3.pk, 'action': 'code', 'code': 'test'}
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)), self.data)
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
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[0]), 'Coupon applied successfully. This course is now free!')

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
        response = self.client.post(reverse("enroll", args=(self.course_3.pk,)), self.data)
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
