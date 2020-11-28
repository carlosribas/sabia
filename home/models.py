from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePageCarouselImages(Orderable):
    """Carousel for the home page."""
    page = ParentalKey("home.HomePage", related_name="carousel_images")
    carousel_title = models.CharField(max_length=100, blank=True)
    carousel_description = models.CharField(max_length=250, blank=True)
    carousel_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("carousel_title"),
        FieldPanel("carousel_description"),
        ImageChooserPanel("carousel_image")
    ]


class HomePage(Page):
    """Home page model."""
    template = "home/home_page.html"
    max_count = 1
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
        MultiFieldPanel(
            [InlinePanel("carousel_images", min_num=1, label="Image")],
            heading="Carousel Images",
        )
    ]
