import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext as _

from base.models import Course, CourseUser, CourseUserInterview, CourseMaterial, CourseMaterialDocument, \
    CourseMaterialVideo, ENROLL, PRE_BOOKING


def course_list(request, template_name="base/course_list.html"):
    # List of available courses
    today = datetime.datetime.today()
    courses = Course.objects.filter(
        Q(end_date__gte=today) | Q(start_date=None) | Q(end_date=None)
    ).order_by('type', '-start_date')

    context = {'courses': courses}
    return render(request, template_name, context)


def course_registration(request, course_id, template_name="base/course_registration.html"):
    course = get_object_or_404(Course, pk=course_id)

    # Check if the user is enrolled in the course
    enrolled = CourseUser.objects.filter(course=course.id, user=request.user.id).first()

    # If it is an individual course, check if the user has already done the interview
    if course.type == 'individual':
        interview = CourseUserInterview.objects.filter(course=course.id, user=request.user.id).first()
    else:
        interview = None

    if request.method == "POST":
        course = get_object_or_404(Course, pk=request.POST['content'])
        user = request.user

        if request.POST['action'] == "pre-booking":
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

        elif request.POST['action'] == "enroll":
            if course.registered < course.vacancies:
                # Increase the number of registered participants
                course.registered = course.registered + 1
                course.save()
                # Create course/user object
                course_user = CourseUser(course=course, user=user, status=ENROLL)
                course_user.save()
                messages.success(request, _('Registration successful!'))
            else:
                messages.error(request, _('Sorry, there are no more vacancies for this course'))

        elif request.POST['action'] == "unsubscribe":
            # Decrease the number of registered participants
            course.registered = course.registered - 1
            course.save()
            # Remove course/user object
            course_user = CourseUser.objects.get(course=course, user=user, status=ENROLL)
            course_user.delete()
            messages.success(request, _('Unsubscribe successfully'))

        elif request.POST['action'] == "interview":
            # Create interview object
            user_interview = CourseUserInterview(course=course, user=user)
            user_interview.save()
            # Send email to the admin
            msg_plain = render_to_string('course_interview', {'course': course.name, 'user': request.user})
            send_mail(
                '[Plataforma Sabiá] Entrevista para curso individual',
                msg_plain,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, _('Interest registered successfully'))

        redirect_url = reverse("enroll", args=(course_id,))
        return HttpResponseRedirect(redirect_url)

    context = {
        'course': course,
        'enrolled': enrolled,
        'interview': interview
    }
    return render(request, template_name, context)


def payment_complete(request):
    body = json.loads(request.body)
    course = get_object_or_404(Course, pk=body['courseId'])

    # Increase the number of registered students
    course.registered = course.registered + 1 if course.registered else 1
    course.save()

    # Check if the amount paid is correct
    payment_note = ''
    if str(course.price) != body['price']:
        payment_note = 'Valor total incorreto'

    # Create course/user object with payment information
    course_user = CourseUser(
        course=course,
        user=request.user,
        status=ENROLL,
        payment_id=body['paymentId'],
        payment_status=body['paymentStatus'],
        payment_note=payment_note
    )
    course_user.save()

    if body['paymentStatus'] == 'COMPLETED':
        response = {'message': _("Payment successful")}
    else:
        response = {'message': _("Waiting for payment confirmation")}

    return JsonResponse(response)


@login_required
def my_course(request, template_name="base/my_course.html"):
    # Check if the user is enrolled in any course
    course_user = CourseUser.objects.filter(user=request.user.id).order_by('-course__start_date')

    # Get course materials
    my_courses = []
    for course in course_user:
        # Get material
        course_material = CourseMaterial.objects.filter(course=course.course).order_by('date')

        # Get items
        material_items = []
        for item in course_material:
            course_material_document = CourseMaterialDocument.objects.filter(course_material=item)
            course_material_video = CourseMaterialVideo.objects.filter(course_material=item)

            material_items.append({
                'name': item.title,
                'date': item.date,
                'link': item.link,
                'description': item.description,
                'document': course_material_document,
                'video': course_material_video
            })

        my_courses.append({'course': course.course.name, 'content': material_items})

    context = {
        'my_courses': my_courses
    }

    return render(request, template_name, context)
