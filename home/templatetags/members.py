import datetime
from django import template
from django.db.models import Q
from itertools import chain

from base.models import Course, TeamMember

register = template.Library()


@register.inclusion_tag('home/members.html', takes_context=True)
def get_members(context):
    members = TeamMember.objects.all().order_by('order', 'name')

    return {
        'members': members,
    }


@register.inclusion_tag('home/courses.html', takes_context=True)
def get_courses(context):
    today = datetime.datetime.today()
    next_courses = Course.objects.filter(start_date__gte=today).exclude(type='admin').order_by('-start_date')
    other_courses = Course.objects.exclude(Q(start_date__gte=today) | Q(type='admin')).order_by('-start_date')
    courses = list(chain(next_courses, other_courses))[:3]
    hidden_courses = Course.objects.filter(type='admin')
    return {
        'courses': courses,
        'hidden_courses': hidden_courses
    }
