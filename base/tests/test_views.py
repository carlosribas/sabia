import datetime

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse, resolve

from userauth.models import CustomUser, VET
from base.models import Course, CoursePage, CourseUser
from base.views import course_list, my_course

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

        CoursePage.objects.create(title="Cursos", slug="cursos")
        self.course_1 = Course.objects.create(name="course 01", vacancies=0)
        self.course_2 = Course.objects.create(
            name="course 02",
            start_date=datetime.date.today() + datetime.timedelta(days=15),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            vacancies=5
        )

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
        self.assertEqual(courses.count(), 2)

    def test_course_pre_booking(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking',
        }
        response = self.client.post(reverse("cursos"), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking successful')

    def test_course_pre_booking_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user, status='pre-booking')
        self.data = {
            'content': self.course_1.pk,
            'action': 'pre-booking-unsubscribe',
        }
        response = self.client.post(reverse("cursos"), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Pre-booking canceled successfully')

    def test_course_enroll(self):
        self.data = {
            'content': self.course_2.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("cursos"), self.data)
        self.assertEqual(response.status_code, 302)

    def test_course_enroll_failed(self):
        self.data = {
            'content': self.course_1.pk,
            'action': 'enroll',
        }
        response = self.client.post(reverse("cursos"), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Sorry, there are no more vacancies for this course')

    def test_course_unsubscribe(self):
        CourseUser.objects.create(course=self.course_1, user=self.user, status='enroll')
        self.data = {
            'content': self.course_1.pk,
            'action': 'unsubscribe',
        }
        response = self.client.post(reverse("cursos"), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Unsubscribe successfully')


class MyCourseTestCase(TestCase):
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

        CoursePage.objects.create(title="Cursos", slug="cursos")
        self.course_1 = Course.objects.create(name="course 01", vacancies=0)
        CourseUser.objects.create(course=self.course_1, user=self.user)

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
