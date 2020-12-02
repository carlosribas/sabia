from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePageCarouselImages(Orderable):
    """Carousel for the home page."""
    page = ParentalKey("home.HomePage", related_name="carousel_images")
    title = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=250, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=False, on_delete=models.SET_NULL, related_name="+",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        ImageChooserPanel("image")
    ]


class HomePageServices(Orderable):
    """Services to show on the home page."""
    page = ParentalKey("home.HomePage", related_name="services")
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    link = models.URLField()
    image = models.ForeignKey("wagtailimages.Image", null=True, on_delete=models.SET_NULL, related_name="+")

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("link"),
        ImageChooserPanel("image")
    ]


class HomePage(Page):
    """Home page model."""
    max_count = 1
    service_title = models.CharField(max_length=50)
    service_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("carousel_images", min_num=1, label="Image")], heading="Carousel Images",
        ),
        MultiFieldPanel([
            FieldPanel('service_title'),
            FieldPanel('service_body'),
            InlinePanel("services", min_num=1, max_num=3, label="Service")
        ], heading="Services"),
    ]
