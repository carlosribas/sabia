import factory

from wagtail.core.models import Page
from base.models import Course, CourseMaterial, CoursePage, FooterText, Menu, MenuItem, StandardPage, TeamMember


class TeamMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMember

    name = factory.Sequence(lambda n: 'Member name {0}'.format(n))
    introduction = factory.Sequence(lambda n: 'Member introduction {0}'.format(n))
    body = factory.Sequence(lambda n: 'Member body {0}'.format(n))


class CoursePageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CoursePage

    title = factory.Sequence(lambda n: 'Course title {0}'.format(n))
    slug = factory.Sequence(lambda n: 'course{0}'.format(n))


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = factory.Sequence(lambda n: 'Course name {0}'.format(n))


class CourseMaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseMaterial

    course = factory.SubFactory(CourseFactory)
    title = factory.Sequence(lambda n: 'Title name {0}'.format(n))


class FooterTextFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FooterText

    body = factory.Sequence(lambda n: 'Body content {0}'.format(n))


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    # override the _create method, to establish parent-child relationship between pages
    @classmethod
    def _create(cls, model_class, *args, **kwargs):

        try:
            parent = kwargs.pop('parent')
        except KeyError:
            # no parent, appending page to root
            parent = Page.get_first_root_node()

        page = model_class(*args, **kwargs)
        parent.add_child(instance=page)

        return page


class StandardPageFactory(PageFactory):
    class Meta:
        model = StandardPage

    title = factory.Sequence(lambda n: 'Standard page {0}'.format(n))


class MenuFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Menu

    title = factory.Sequence(lambda n: 'Menu {0}'.format(n))


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    menu = factory.SubFactory(MenuFactory)
