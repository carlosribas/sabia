from django.utils.translation import ugettext as _

from wagtail.core import hooks
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup, modeladmin_register)

from base.models import Course, CourseMaterial, CoursePage, FooterText, Menu, TeamMember


@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != 'fragmentos']


class TeamMemberAdmin(ModelAdmin):
    model = TeamMember
    menu_label = _('Team')
    menu_icon = 'fa-users'
    list_display = ('name', 'job_title', 'thumb_image')
    list_filter = ('job_title',)
    search_fields = ('name', 'job_title')


class FooterTextAdmin(ModelAdmin):
    model = FooterText
    menu_label = _('Footer Text')
    menu_icon = 'fa-pencil'


class MenuAdmin(ModelAdmin):
    model = Menu
    menu_label = _('Menu')
    menu_icon = 'fa-bars'
    search_fields = ('title', 'slug')


class CourseAdmin(ModelAdmin):
    model = Course
    menu_label = _('Course')
    menu_icon = 'fa-money'
    search_fields = ('name',)
    list_filter = ('name',)
    list_display = ('name', 'start_date', 'end_date', 'vacancies', 'registered')


class CoursePageAdmin(ModelAdmin):
    model = CoursePage
    menu_label = _('Course page text')
    menu_icon = 'fa-file-text'
    list_display = ('title',)


class CourseMaterialAdmin(ModelAdmin):
    model = CourseMaterial
    menu_label = _('Course material')
    menu_icon = 'fa-book'
    search_fields = ('title',)
    list_filter = ('title',)
    list_display = ('course', 'title', 'date')


class SabiaModelAdminGroup(ModelAdminGroup):
    menu_label = _('General')
    menu_icon = 'cog'
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (CourseAdmin, CourseMaterialAdmin, CoursePageAdmin, TeamMemberAdmin, FooterTextAdmin, MenuAdmin)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(SabiaModelAdminGroup)
