import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
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

        redirect_url = reverse("cursos")
        return HttpResponseRedirect(redirect_url)

    context = {
        'course_text': course_text,
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'pre_booked_courses': pre_booked_courses
    }

    return render(request, template_name, context)


def course_registration(request, course_id, template_name="base/course_registration.html"):
    course = get_object_or_404(Course, pk=course_id)

    # Check the number of possible installments
    if course.price3x:
        installment = 3
    elif course.price2x:
        installment = 2
    else:
        installment = 1

    context = {'course': course, 'installment': installment}
    return render(request, template_name, context)


def payment_complete(request):
    body = json.loads(request.body)
    course = get_object_or_404(Course, pk=body['courseId'])

    # Increase the number of registered students
    course.registered = course.registered + 1
    course.save()

    # Check if the amount paid is correct
    payment_note = ''
    possible_installment = [str(course.price2x), str(course.price3x)]
    if str(course.price) != body['price']:
        payment_note = 'Valor total incorreto'
    elif body['installmentPrice'] not in possible_installment:
        payment_note = 'Valor parcelado incorreto'

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

    # Send email to the user
    msg_plain = render_to_string('course_registration_email', {'course': course.name})
    send_mail(
        '[Plataforma Sabiá] Confirmação de inscrição',
        msg_plain,
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False,
    )

    if body['paymentStatus'] == 'COMPLETED':
        response = {'message': _("Payment successful")}
    else:
        response = {'message': _("Waiting for payment confirmation")}

    return JsonResponse(response)
