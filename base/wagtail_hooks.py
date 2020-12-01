from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from base.models import FooterText


class FooterTextAdmin(ModelAdmin):
    model = FooterText
    search_fields = ('body',)


class SabiaModelAdminGroup(ModelAdminGroup):
    menu_label = 'General config'
    menu_icon = 'cog'
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (FooterTextAdmin,)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(SabiaModelAdminGroup)
