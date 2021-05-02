from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import Tag, TaggedItemBase

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
    PageChooserPanel,
    FieldRowPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Collection, Orderable
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailstreamforms.blocks import WagtailFormBlock
from wagtailtrans.models import Language, TranslatablePage
from wagtailstreamforms.models.abstract import AbstractFormSetting

from userauth.models import CustomUser
from .blocks import BaseStreamBlock
from .richtext_options import RICHTEXT_FEATURES


ENROLL = 'enroll'
PRE_BOOKING = 'pre-booking'
STATUS = (
    (ENROLL, _('Enroll')),
    (PRE_BOOKING, _('Pre-booking')),
)

ADMIN = 'admin'
INDIVIDUAL = 'individual'
GROUP = 'group'
RECORDED = 'recorded'
COURSE = (
    (ADMIN, _('Admin')),
    (INDIVIDUAL, _('Individual')),
    (GROUP, _('Group')),
    (RECORDED, _('Recorded')),
)


def course_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/cursos/<course_id>/<filename>
    return 'cursos/{0}/{1}'.format(instance.course_material.course.pk, filename)


@register_snippet
class TeamMember(index.Indexed, ClusterableModel):
    """A Django model to store team members."""
    name = models.CharField(_("Name"), max_length=254)
    job_title = models.CharField(_("Job title"), max_length=254, blank=True)
    linkedin = models.CharField(max_length=254, blank=True, help_text=_("Link to Linkedin"))
    introduction = models.TextField(help_text=_("Brief description"))
    body = RichTextField()
    order = models.IntegerField(_('Position'), blank=True, default=10)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('name', classname="col6"),
                FieldPanel('job_title', classname="col6"),
                FieldPanel('linkedin', classname="col6"),
                FieldPanel('order', classname="col6"),
            ])
        ], heading=_("Personal information")),
        FieldPanel('introduction'),
        FieldPanel('body'),
        ImageChooserPanel('image')
    ]

    search_fields = [
        index.SearchField('name'),
    ]

    @property
    def thumb_image(self):
        # Returns an empty string if there is no profile pic or the rendition file can't be found.
        try:
            return self.image.get_rendition('fill-50x50').img_tag()
        except:  # noqa: E722 FIXME: remove bare 'except:'
            return ''

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Team")


class CourseTag(TaggedItemBase):
    """This model allows us to create a many-to-many relationship between the Course object and tags."""
    content_object = ParentalKey('Course', related_name='tagged_courses', on_delete=models.CASCADE)


@register_snippet
class Course(index.Indexed, ClusterableModel):
    """A Django model to create courses."""
    type = models.CharField(_("Type"), max_length=15, choices=COURSE)
    name = models.CharField(_("Name"), max_length=254)
    introduction = models.CharField(_("Introduction"), max_length=254)
    start_date = models.DateField(_("Start date"), blank=True, null=True)
    end_date = models.DateField(_("End date"), blank=True, null=True)
    start_time = models.TimeField(_("Start time"), blank=True, null=True)
    end_time = models.TimeField(_("End time"), blank=True, null=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, blank=True, null=True)
    vacancies = models.IntegerField(_("Vacancies"), blank=True, null=True)
    registered = models.IntegerField(_("Registered"), blank=True, null=True, default=0)
    pre_booking = models.IntegerField(_("Pre-booking"), blank=True, null=True, default=0)
    description = RichTextField(_("Description"), features=RICHTEXT_FEATURES, blank=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    tags = ClusterTaggableManager(through=CourseTag, blank=True)

    panels = [
        FieldPanel('type'),
        FieldPanel('name'),
        FieldPanel('introduction'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('start_date', classname="col6"),
                FieldPanel('end_date', classname="col6"),
            ])
        ], heading=_("Dates")),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('start_time', classname="col6"),
                FieldPanel('end_time', classname="col6"),
            ])
        ], heading=_("Schedule")),
        FieldPanel('price'),
        FieldPanel('vacancies'),
        FieldPanel('registered'),
        FieldPanel('description'),
        ImageChooserPanel('image'),
        FieldPanel('tags'),
    ]

    search_fields = [
        index.SearchField('name'),
    ]

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def get_tags(self):
        """
        Return all the tags that are related to the course into a list we can access on the template.
        We're additionally adding a URL to access Course objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = '/' + '/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'tags',
                tag.slug
            ])
        return tags

    def show_course(self):
        return self.start_date >= datetime.datetime.now().date() if self.start_date else False

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


@register_snippet
class CourseMaterial(index.Indexed, ClusterableModel):
    """A Django model to create content for courses."""
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=254)
    date = models.DateField(_("Date"), blank=True, null=True)
    description = RichTextField(_("Description"), features=RICHTEXT_FEATURES, blank=True)
    link = models.URLField(_('Broadcast link'), blank=True, null=True)

    panels = [
        FieldPanel('course'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('title', classname="col6"),
                FieldPanel('date', classname="col6"),
                FieldPanel('link', classname="col12"),
                FieldPanel('description', classname="col12"),
            ])
        ], heading=_("Lesson information")),
        InlinePanel('course_material_document', label=_("Documents")),
        InlinePanel('course_material_video', label=_("Videos"))
    ]

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        verbose_name = _("Course material")
        verbose_name_plural = _("Course materials")


class CourseMaterialDocument(Orderable):
    course_material = ParentalKey('CourseMaterial', related_name='course_material_document')
    document = models.FileField(_("Document"), upload_to=course_directory_path, max_length=254, blank=True, null=True)


class CourseMaterialVideo(Orderable):
    course_material = ParentalKey('CourseMaterial', related_name='course_material_video')
    video = models.FileField(_('Video'), upload_to=course_directory_path, max_length=254, blank=True, null=True)


@register_snippet
class CourseUser(models.Model):
    """A Django model to register the user in a course"""
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name=_('User'), on_delete=models.CASCADE)
    status = models.CharField(_("Status"), max_length=30, choices=STATUS)
    date = models.DateTimeField(_("Date"), auto_now_add=True, blank=True)
    payment_id = models.CharField(_("Payment Id"), max_length=254, blank=True)
    payment_status = models.CharField(_("Payment status"), max_length=254, blank=True)
    payment_note = models.CharField(_("Note"), max_length=254, blank=True)
    coupon_used = models.CharField(_("Coupon"), max_length=254, blank=True)


@register_snippet
class CourseUserInterview(models.Model):
    """A Django model to register the user interest in an individual course"""
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name=_('User'), on_delete=models.CASCADE)
    show_button = models.BooleanField(_("Show payment button"), default=False)


@register_snippet
class CourseUserCoupon(models.Model):
    """A Django model to create discount coupons"""
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name=_('User'), on_delete=models.CASCADE, blank=True, null=True)
    code = models.CharField(_("Code"), max_length=50, unique=True)
    discount = models.IntegerField(_("Discount"), default=5, validators=[MinValueValidator(0), MaxValueValidator(100)])
    valid_from = models.DateTimeField(_("Valid from"))
    valid_to = models.DateTimeField(_("Valid to"))

    panels = [
        FieldPanel('course'),
        FieldPanel('user'),
        FieldPanel('code'),
        FieldPanel('discount'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('valid_from', classname="col6"),
                FieldPanel('valid_to', classname="col6"),
            ])
        ], heading=_("Dates")),
    ]

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")


@register_snippet
class FooterText(models.Model):
    """
    This provides editable text for the site footer. It uses the decorator `register_snippet` to allow it
    to be accessible via the admin. It is made accessible on the template via a template tag defined in
    base/templatetags/navigation_tags.py
    """
    body = RichTextField()

    panels = [
        FieldPanel('body'),
    ]

    def __str__(self):
        return _("Footer Text")

    class Meta:
        verbose_name_plural = _("Footer Text")


class StandardPage(TranslatablePage):
    """
    A generic content page. It could be used for any type of page content that only needs a title,
    image, introduction and body field.
    """

    introduction = models.TextField(help_text=_("Text to describe the page"), blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_("Landscape mode only; horizontal width between 1000px and 3000px.")
    )
    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)
    content_panels = TranslatablePage.content_panels + [
        FieldPanel('introduction', classname="full"),
        StreamFieldPanel('body'),
        ImageChooserPanel('image'),
    ]


class GalleryPage(TranslatablePage):
    """
    This is a page to list locations from the selected Collection. We use a Q object to list any Collection
    created (/admin/collections/) even if they contain no items.
    """

    introduction = models.TextField(
        help_text=_("Text to describe the page"),
        blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_("Landscape mode only; horizontal width between 1000px and 3000px.")
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True
    )
    collection = models.ForeignKey(
        Collection,
        limit_choices_to=~models.Q(name__in=['Root']),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Select the image collection for this gallery.")
    )

    content_panels = TranslatablePage.content_panels + [
        FieldPanel('introduction', classname="full"),
        StreamFieldPanel('body'),
        ImageChooserPanel('image'),
        FieldPanel('collection'),
    ]

    # Defining what content type can sit under the parent. Since it's a blank array no subpage can be added
    subpage_types = []


class FormPage(TranslatablePage):
    intro = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    body = StreamField([
        ('form', WagtailFormBlock()),
    ])

    content_panels = TranslatablePage.content_panels + [
        FieldPanel('intro'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
    ]


class AdvancedFormSetting(AbstractFormSetting):
    to_address = models.EmailField()


@register_snippet
class Menu(ClusterableModel):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title', editable=True, help_text="Unique identifier of menu.")

    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('slug'),
        ], heading=_("Menu")),
        InlinePanel('menu_items', label=_("Menu Item"))
    ]

    def __str__(self):
        return self.title


class MenuItem(Orderable):
    menu = ParentalKey('Menu', related_name='menu_items', help_text=_("Menu to which this item belongs"))
    title = models.CharField(max_length=50, help_text=_("Title of menu item that will be displayed"))
    link_url = models.CharField(max_length=500, blank=True, null=True, help_text=_("URL to link to, e.g. /contato"))
    link_page = models.ForeignKey(
        TranslatablePage, blank=True, null=True, related_name='+', on_delete=models.CASCADE,
        help_text=_("Page to link to"),
    )
    title_of_submenu = models.CharField(
        blank=True, null=True, max_length=50,
        help_text=_("Title of submenu (LEAVE BLANK if there is no custom submenu)")
    )
    icon = models.CharField(max_length=100, blank=True, help_text=_("Fontawesome icon"))
    show_when = models.CharField(
        max_length=15,
        choices=[('always', _("Always")), ('logged_in', _("When logged in")), ('not_logged_in', _("When not logged in"))],
        default='always',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('link_url'),
        PageChooserPanel('link_page'),
        FieldPanel('title_of_submenu'),
        FieldPanel('icon'),
        FieldPanel('show_when'),
    ]

    def trans_page(self, language_code):
        if self.link_page:
            can_page = self.link_page.canonical_page if self.link_page.canonical_page else self.link_page
            if language_code == settings.LANGUAGE_CODE:  # requested language is the canonical language
                return can_page
            try:
                language = Language.objects.get(code=language_code)
            except Language.DoesNotExist:  # no language found, return original page
                return self.link_page
            return TranslatablePage.objects.get(language=language, canonical_page=can_page)
        return None

    def trans_url(self, language_code):
        if self.link_url:
            return '/' + language_code + self.link_url
        elif self.link_page:
            return self.trans_page(language_code).url
        return None

    @property
    def slug_of_submenu(self):
        # becomes slug of submenu if there is one, otherwise None
        if self.title_of_submenu:
            return slugify(self.title_of_submenu)
        return None

    def show(self, authenticated):
        return ((self.show_when == 'always')
                or (self.show_when == 'logged_in' and authenticated)
                or (self.show_when == 'not_logged_in' and not authenticated))

    def __str__(self):
        return self.title
