from django.test import TestCase, RequestFactory
from wagtail.core.models import Page, Site

from .factories import CourseFactory, CourseMaterialFactory, CoursePageFactory, FooterTextFactory, TeamMemberFactory
from base.models import Course, CourseMaterial, CoursePage, FooterText, TeamMember


class TestPageModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        # Wagtail needs a site, e.g. to define url
        # Page.get_first_root_node() is used by Wagtail to find the root page
        cls.site = Site.objects.create(is_default_site=True, root_page=Page.get_first_root_node())
        cls.team_member = TeamMemberFactory()
        cls.course_page = CoursePageFactory()
        cls.course = CourseFactory()
        cls.course_material = CourseMaterialFactory()
        cls.footer = FooterTextFactory()

    def test_team_member_str(self):
        member = TeamMember.objects.first()
        self.assertEqual(str(member), "Member name 0")

    def test_team_member_image(self):
        member = TeamMember.objects.first()
        self.assertEqual(member.thumb_image, "")

    def test_course_page_str(self):
        course = CoursePage.objects.first()
        self.assertEqual(str(course), "Course title 0")

    def test_course_str(self):
        course = Course.objects.first()
        self.assertEqual(str(course), "Course name 0")

    def test_course_material_str(self):
        course_material = CourseMaterial.objects.first()
        self.assertEqual(str(course_material), "Title name 0")

    def test_footer_str(self):
        text = FooterText.objects.first()
        self.assertEqual(str(text), "Footer Text")
