from django.test import TestCase, RequestFactory

from userauth.models import CustomUser, VET
from userauth.forms import SignupForm
from userauth.views import profile_view


class TestCustomUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = CustomUser.objects.create(username="joao", password="pass", first_name="Joao", last_name="Silva")
        cls.user2 = CustomUser.objects.create(username="bla", password="bla", first_name="bla", last_name="bla")

    def test_string_representation_of_customuser(self):
        expected_representation_customuser = 'Joao Silva'
        self.assertEqual(expected_representation_customuser, str(self.user))

    def test_profile_view_with_user_gets_valid_response(self):
        request = self.factory.get(self.user.get_absolute_url())
        # log user in
        request.user = self.user
        self.assertEqual(profile_view(request).status_code, 200)

    def test_signup_form(self):
        form_data = {'first_name': 'Maria', 'last_name': 'Silva', 'academic_background': VET}
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.signup(self, user=self.user2)
        self.assertEqual(self.user2.first_name, 'Maria')
