from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


VET = 'vet'
STUDENT = 'student'
OTHER = 'other'
USER_TYPE = (
    (VET, _('Veterinarian')),
    (STUDENT, _('Veterinary medicine student')),
    (OTHER, _('Others')),
)

NO = 'no'
YES = 'yes'
YES_NO_ANSWER = (
    (NO, _('No')),
    (YES, _('Yes')),
)


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r"^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$",
        message=_("Enter a valid phone number starting with (DDD)")
    )
    phone = models.CharField(_("Phone"), validators=[phone_regex], max_length=15, blank=True)
    academic_background = models.CharField(_("Academic background"), max_length=30, choices=USER_TYPE)
    other = models.CharField(_("Other"), max_length=100, blank=True)
    newsletter = models.CharField(max_length=3, choices=YES_NO_ANSWER, default=YES)

    class Meta:
        ordering = ['first_name']

    def get_absolute_url(self):
        return reverse('account_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
