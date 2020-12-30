import datetime

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext as _

from base.models import Course, CourseUser, CoursePage, ENROLL, PRE_BOOKING


def course_list(request, template_name="base/course_list.html"):
    # Introductory text about courses
    course_text = CoursePage.objects.get(slug="cursos").course_page_items.all()

    # List of available courses
    today = datetime.datetime.today()
    courses = Course.objects.filter(Q(start_date__gte=today) | Q(start_date=None)).order_by('-start_date')

    # Check if the user is enrolled in any course
    course_user = CourseUser.objects.filter(user=request.user.id)
    enrolled_courses = []
    pre_booked_courses = []
    for item in course_user:
        if item.status == "enroll":
            enrolled_courses.append(item.course.id)
        elif item.status == "pre-booking":
            pre_booked_courses.append(item.course.id)

    if request.method == "POST":
        course = get_object_or_404(Course, pk=request.POST['content'])
        user = request.user

        if request.POST['action'] == "enroll":
            if course.registered < course.vacancies:
                # Increase the number of registered students
                course.registered = course.registered + 1
                course.save()
                # Create course/user object
                course_user = CourseUser(course=course, user=user, status=ENROLL)
                course_user.save()
                messages.success(request, _('Registration successful'))
            else:
                messages.error(request, _('Sorry, there are no more vacancies for this course'))

        elif request.POST['action'] == "unsubscribe":
            # Decrease the number of registered students
            course.registered = course.registered - 1
            course.save()
            # Remove course/user object
            course_user = CourseUser.objects.get(course=course, user=user, status=ENROLL)
            course_user.delete()
            messages.success(request, _('Unsubscribe successfully'))

        elif request.POST['action'] == "pre-booking":
            # Increase the pre-booking number
            course.pre_booking = course.pre_booking + 1
            course.save()
            # Create course/user object
            course_user = CourseUser(course=course, user=user, status=PRE_BOOKING)
            course_user.save()
            messages.success(request, _('Pre-booking successful'))

        elif request.POST['action'] == "pre-booking-unsubscribe":
            # Decrease the pre-booking number
            course.pre_booking = course.pre_booking - 1
            course.save()
            # Remove course/user object
            course_user = CourseUser.objects.get(course=course, user=user, status=PRE_BOOKING)
            course_user.delete()
            messages.success(request, _('Pre-booking canceled successfully'))

        redirect_url = reverse("cursos")
        return HttpResponseRedirect(redirect_url)

    context = {
        'course_text': course_text,
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'pre_booked_courses': pre_booked_courses
    }

    return render(request, template_name, context)
