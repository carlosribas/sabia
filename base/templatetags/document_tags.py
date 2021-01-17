import os

from django import template

register = template.Library()


# Returns document name
@register.filter
def filename(value):
    return os.path.basename(value)
