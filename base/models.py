from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
    PageChooserPanel,
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

from .blocks import BaseStreamBlock


@register_snippet
class TeamMember(index.Indexed, ClusterableModel):
    """A Django model to store team members."""
    name = models.CharField(_("Name"), max_length=254)
    job_title = models.CharField(_("Job title"), max_length=254, blank=True)
    linkedin = models.CharField(max_length=254, blank=True, help_text=_("Link to Linkedin"))
    introduction = models.TextField(help_text=_("Brief description"))
    body = RichTextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('job_title'),
        FieldPanel('linkedin'),
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
        verbose_name = 'Person'
        verbose_name_plural = 'Team'


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
