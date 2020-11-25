from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r"^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$",
        message=_("Enter a valid phone number starting with (DDD)")
    )
    phone = models.CharField(validators=[phone_regex], verbose_name=_("Phone"), max_length=15, blank=True, null=True)

    class Meta:
        ordering = ['first_name']

    def get_absolute_url(self):
        return reverse('account_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
