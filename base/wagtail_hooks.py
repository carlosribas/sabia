from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from base.models import FooterText, TeamMember


class TeamMemberModelAdmin(ModelAdmin):
    model = TeamMember
    menu_label = 'Team'
    menu_icon = 'fa-users'
    list_display = ('name', 'job_title', 'thumb_image')
    list_filter = ('job_title', )
    search_fields = ('name', 'job_title')


class FooterTextAdmin(ModelAdmin):
    model = FooterText
    search_fields = ('body',)


class SabiaModelAdminGroup(ModelAdminGroup):
    menu_label = 'General'
    menu_icon = 'cog'
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (FooterTextAdmin, TeamMemberModelAdmin)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(SabiaModelAdminGroup)
