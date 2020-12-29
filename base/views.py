import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext as _

from base.models import Course, CourseUser, CoursePage


def course_list(request, template_name="base/course_list.html"):
    # Introductory text about courses
    course_text = CoursePage.objects.get(slug="cursos").course_page_items.all()

    # List of available courses
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
            if course.registered < course.vacancies:
                # Update total enrolled students
                course.registered = course.registered + 1
                course.save()
                # Create course/user object
                course_user = CourseUser(course=course, user=user)
                course_user.save()
                messages.success(request, _('Registration successful'))
            else:
                messages.error(request, _('Sorry, there are no more vacancies for this course'))
        elif request.POST['action'] == "unsubscribe":
            course = get_object_or_404(Course, pk=request.POST['content'])
            user = request.user
            # Update total enrolled students
            course.registered = course.registered - 1
            course.save()
            # Remove course/user object
            course_user = CourseUser.objects.get(course=course, user=user)
            course_user.delete()
            messages.success(request, _('Unsubscribe successfully'))

        redirect_url = reverse("cursos")
        return HttpResponseRedirect(redirect_url)

    context = {'course_text': course_text, 'courses': courses, 'enrolled_courses': enrolled_courses}

    return render(request, template_name, context)
