from django.db import models
from django.utils.translation import ugettext as _
from modelcluster.fields import ParentalKey

from wagtail.core.models import Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailstreamforms.blocks import WagtailFormBlock
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
    link = models.CharField(max_length=500, blank=True, null=True, help_text=_("URL to link to, e.g. /contato"))
    image = models.ForeignKey(
        "wagtailimages.Image", verbose_name=_('Image'), null=True, blank=False, on_delete=models.SET_NULL,
        related_name="+"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("title_color"),
        FieldPanel("description"),
        FieldPanel("description_color"),
        FieldPanel("link"),
        ImageChooserPanel("image")
    ]


class HomePageServices(Orderable):
    """Services to show on the home page."""
    page = ParentalKey("home.HomePage", related_name="services")
    title = models.CharField(_("Title"), max_length=50)
    description = models.CharField(_("Description"), max_length=200)
    link = models.ForeignKey(
        TranslatablePage, verbose_name=_("Link"), blank=True, null=True, related_name='+', on_delete=models.CASCADE,
        help_text=_("Page to link to"),
    )
    image = models.ForeignKey(
        "wagtailimages.Image", verbose_name=_("Image"), null=True, on_delete=models.SET_NULL, related_name="+"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("link"),
        ImageChooserPanel("image")
    ]


class HomePageWhyChooseUs(Orderable):
    """Content to show on the Why Choose Us."""
    page = ParentalKey("home.HomePage", related_name="why_choose_us")
    title = models.CharField(_("Title"), max_length=50)
    description = models.CharField(_("Description"), max_length=254)
    icon = models.CharField(max_length=100, blank=True, help_text=_("Fontawesome icon"))

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel('icon'),
    ]


class HomePage(TranslatablePage):
    """Home page model."""
    max_count = 1
    service_title = models.CharField(_("Service title"), max_length=50)
    service_body = RichTextField(_("Service body"), blank=True)
    member_link = models.ForeignKey(
        TranslatablePage, verbose_name=_("Link to be a member"), blank=True, null=True, on_delete=models.PROTECT,
        related_name='+', help_text=_("Page to link to"),
    )
    form = StreamField([
        ('form', WagtailFormBlock()),
    ], blank=True, null=True)

    content_panels = TranslatablePage.content_panels + [
        MultiFieldPanel(
            [InlinePanel("carousel_images", min_num=1, label=_("Image"))], heading=_("Carousel Images"),
        ),
        MultiFieldPanel([
            FieldPanel("service_title"),
            FieldPanel("service_body"),
            InlinePanel("services", min_num=1, max_num=3, label=_("Service"))
        ], heading=_("Services")),
        FieldPanel("member_link"),
        MultiFieldPanel([
            InlinePanel("why_choose_us", min_num=1, max_num=3, label=_("Item"))
        ], heading=_("Why choose us")),
        StreamFieldPanel('form'),
    ]
