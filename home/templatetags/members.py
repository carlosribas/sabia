from django import template

from base.models import TeamMember

register = template.Library()


@register.inclusion_tag('home/members.html', takes_context=True)
def get_members(context):
    members = TeamMember.objects.all().order_by('order', 'name')

    return {
        'members': members,
    }