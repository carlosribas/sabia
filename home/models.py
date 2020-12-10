from django.db import models
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey

from wagtail.core.models import Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailtrans.models import TranslatablePage


class HomePageCarouselImages(Orderable):
    """Carousel for the home page."""
    page = ParentalKey("home.HomePage", related_name="carousel_images")
    title = models.CharField(_("Title"), max_length=100, blank=True)
    title_color = models.CharField(_("Title color"), max_length=7, blank=True, help_text=_("For example: #ffffff"))
    description = models.CharField(_("Description"), max_length=250, blank=True)
    description_color = models.CharField(
        _("Description color"), max_length=7, blank=True, help_text=_("For example: #ffffff")
    )
    image = models.ForeignKey(
        "wagtailimages.Image", verbose_name=_('Image'), null=True, blank=False, on_delete=models.SET_NULL,
        related_name="+"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("title_color"),
        FieldPanel("description"),
        FieldPanel("description_color"),
        ImageChooserPanel("image")
    ]


class HomePageServices(Orderable):
    """Services to show on the home page."""
    page = ParentalKey("home.HomePage", related_name="services")
    title = models.CharField(_("Title"), max_length=50)
    description = models.CharField(_("Description"), max_length=200)
    link = models.ForeignKey(
        TranslatablePage, verbose_name=_('Link'), blank=True, null=True, related_name='+', on_delete=models.CASCADE,
        help_text=_("Page to link to"),
    )
    image = models.ForeignKey(
        "wagtailimages.Image", verbose_name=_('Image'), null=True, on_delete=models.SET_NULL, related_name="+"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("link"),
        ImageChooserPanel("image")
    ]


class HomePage(TranslatablePage):
    """Home page model."""
    max_count = 1
    service_title = models.CharField(_("Service title"), max_length=50)
    service_body = RichTextField(_("Service body"), blank=True)

    content_panels = TranslatablePage.content_panels + [
        MultiFieldPanel(
            [InlinePanel("carousel_images", min_num=1, label=_("Image"))], heading=_("Carousel Images"),
        ),
        MultiFieldPanel([
            FieldPanel('service_title'),
            FieldPanel('service_body'),
            InlinePanel("services", min_num=1, max_num=3, label=_("Service"))
        ], heading=_("Services")),
    ]
