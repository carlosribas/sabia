import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext as _

from base.models import Course, CourseUser


@login_required
def course_list(request, template_name="base/course_list.html"):
    today = datetime.datetime.today()
    courses = Course.objects.filter(start_date__gte=today).order_by('-start_date')
    course_user = CourseUser.objects.filter(user=request.user.id)
    enrolled_courses = []
    for item in course_user:
        enrolled_courses.append(item.course.id)

    if request.method == "POST":
        if request.POST['action'] == "enroll":
            course = get_object_or_404(Course, pk=request.POST['content'])
            user = request.user
            course_user = CourseUser(course=course, user=user)
            course_user.save()
            messages.success(request, _('Registration successful'))
        elif request.POST['action'] == "unsubscribe":
            course = get_object_or_404(Course, pk=request.POST['content'])
            user = request.user
            course_user = CourseUser.objects.get(course=course, user=user)
            course_user.delete()
            messages.success(request, _('Unsubscribe successfully'))

        redirect_url = reverse("inscricao")
        return HttpResponseRedirect(redirect_url)

    context = {'courses': courses, 'enrolled_courses': enrolled_courses}

    return render(request, template_name, context)
