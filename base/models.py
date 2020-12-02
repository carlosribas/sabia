from __future__ import unicode_literals

from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Collection, Page
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from .blocks import BaseStreamBlock


@register_snippet
class TeamMember(index.Indexed, ClusterableModel):
    """A Django model to store team members."""
    name = models.CharField(_("Name"), max_length=254)
    job_title = models.CharField(_("Job title"), max_length=254, blank=True)
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
    max_count = 1
    body = RichTextField()

    panels = [
        FieldPanel('body'),
    ]

    def __str__(self):
        return _("Footer Text")

    class Meta:
        verbose_name_plural = _("Footer Text")


class StandardPage(Page):
    """
    A generic content page. It could be used for any type of page content that only needs a title,
    image, introduction and body field.
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
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        StreamFieldPanel('body'),
        ImageChooserPanel('image'),
    ]


class GalleryPage(Page):
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

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        StreamFieldPanel('body'),
        ImageChooserPanel('image'),
        FieldPanel('collection'),
    ]

    # Defining what content type can sit under the parent. Since it's a blank array no subpage can be added
    subpage_types = []


class FormField(AbstractFormField):
    """
    Quick way to generate a general purpose data-collection form or contact form
    without having to write code.
    """
    page = ParentalKey('FormPage', related_name='form_fields', on_delete=models.CASCADE)


class FormPage(AbstractEmailForm):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField(BaseStreamBlock())
    thank_you_text = RichTextField(blank=True)

    # Note how we include the FormField object via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]
