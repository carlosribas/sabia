import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from base.models import Course


@login_required
def course_list(request, template_name="base/course_list.html"):
    today = datetime.datetime.today()
    courses = Course.objects.filter(start_date__gte=today).order_by('-start_date')
    context = {'courses': courses}

    return render(request, template_name, context)
