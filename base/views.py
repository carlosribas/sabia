import csv
import datetime
import json
import logging

from decimal import Decimal as Dec, ROUND_HALF_UP
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, \
    BadHeaderError, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from itertools import chain

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from base.mercado_pago import MercadoPago
from base.mercadopago_payment_data import MercadoPagoPaymentData, ID_SEPARATOR
from base.models import Course, CourseUser, CourseUserCoupon, CourseUserInterview, CourseMaterial, \
    CourseMaterialDocument, CourseMaterialVideo, ENROLL, PRE_BOOKING
from base.mercado_pago_api import MercadoPagoAPI, FAILURE_STATUS, SUCCESS_STATUS, \
    PENDING_STATUS, IN_PROCESS_STATUS
from sabia.settings.local import MERCADO_PAGO_WEBHOOK_TOKEN
from userauth.models import CustomUser


logger = logging.getLogger(__name__)


def course_list(request, template_name="base/course_list.html"):
    # List of available courses
    today = datetime.datetime.today()
    next_courses = Course.objects.filter(start_date__gte=today).exclude(type='admin').order_by('-start_date')
    other_courses = Course.objects.exclude(Q(start_date__gte=today) | Q(type='admin')).order_by('-start_date')
    courses = list(chain(next_courses, other_courses))
    hidden_courses = Course.objects.filter(type='admin')
    context = {
        'courses': courses,
        'hidden_courses': hidden_courses
    }
    return render(request, template_name, context)


def course_registration(request, course_id, template_name="base/course_registration.html"):
    course = get_object_or_404(Course, pk=course_id)

    # Get the course fee
    price = course.price  # paypal value
    if price and price <= 100:
        price1x = course.price
        price2x = None
        price3x = None
        price4x = None
        installments = 1
    elif price and price > 100:
        price1x = course.price - (course.price * Dec('.05')).quantize(Dec('.01'), rounding=ROUND_HALF_UP)
        price2x = (price / 2).quantize(Dec('.01'))
        price3x = (price / 3).quantize(Dec('.01'))
        price4x = (price / 4).quantize(Dec('.01'))
        installments = 4
    else:
        price1x = None
        price2x = None
        price3x = None
        price4x = None
        installments = None

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
                '[Baroni-Massad] Entrevista para curso individual',
                msg_plain,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, _('Interest registered successfully'))

        elif request.POST['action'] == "code":
            code = request.POST['code']
            coupon = None

            try:
                coupon = CourseUserCoupon.objects.get(
                    course=course,
                    code=code,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            except CourseUserCoupon.DoesNotExist:
                messages.warning(request, _('Coupon not found'))

            if coupon and coupon.user and coupon.user != request.user:
                messages.warning(request, _('Coupon not found'))
            elif coupon and coupon.discount != 100:
                discount = Dec(coupon.discount / 100).quantize(Dec('.01'), rounding=ROUND_HALF_UP)
                price = course.price - (course.price * discount).quantize(Dec('.01'), rounding=ROUND_HALF_UP)
                price1x = (price - price * 5 / 100).quantize(Dec('.01'), rounding=ROUND_HALF_UP)
                price2x = (price / 2).quantize(Dec('.01'))
                price3x = (price / 3).quantize(Dec('.01'))
                price4x = (price / 4).quantize(Dec('.01'))

                mercadopago = MercadoPago()
                config = {
                    'id': str(course_id) + ID_SEPARATOR + request.user.email + ID_SEPARATOR + coupon.code,
                    'title': str(course), 'unit_price': float(price1x),
                    'installments': installments, 'payer_email': request.user.email
                }
                preference = mercadopago.get_preference(config)
                if preference is not None:
                    preference_response = preference['response']
                    public_key = settings.MERCADO_PAGO_PUBLIC_KEY
                else:
                    preference_response = None
                    public_key = None

                context = {
                    'course': course,
                    'enrolled': enrolled,
                    'interview': interview,
                    'price': price,
                    'price1x': price1x,
                    'price2x': price2x,
                    'price3x': price3x,
                    'price4x': price4x,
                    'preference': preference_response,
                    'public_key': public_key
                }
                messages.success(request, _('Coupon applied successfully'))
                return render(request, template_name, context)
            elif coupon and coupon.discount == 100:
                context = {'course': course, 'enrolled': enrolled, 'interview': interview, 'coupon': code}
                messages.success(request, _('Coupon applied successfully. This course is now free!'))
                return render(request, template_name, context)

        redirect_url = reverse("enroll", args=(course_id,))
        return HttpResponseRedirect(redirect_url)

    if request.user.is_authenticated and not enrolled and price:
        mercadopago = MercadoPago()
        config = {
            'id': str(course_id) + ID_SEPARATOR + request.user.email + ID_SEPARATOR, 'title': str(course),
            'unit_price': float(price1x),
            'installments': installments, 'payer_email': request.user.email
        }
        preference = mercadopago.get_preference(config)
        if preference is not None:
            preference_response = preference['response']
            public_key = settings.MERCADO_PAGO_PUBLIC_KEY
        else:
            preference_response = None
            public_key = None
    else:
        preference_response = None
        public_key = None

    context = {
        'course': course,
        'enrolled': enrolled,
        'interview': interview,
        'price': price,
        'price1x': price1x,
        'price2x': price2x,
        'price3x': price3x,
        'price4x': price4x,
        'preference': preference_response,
        'public_key': public_key
    }

    return render(request, template_name, context)


@login_required
def payment_complete(request):
    payment_status = request.GET.get('status')
    payment_id = request.GET.get('payment_id')
    if payment_status not in [
        FAILURE_STATUS, SUCCESS_STATUS, PENDING_STATUS, IN_PROCESS_STATUS
    ] or payment_id is None:
        return HttpResponseBadRequest(_('Cannot process this request'))

    mercadopago_api = MercadoPagoAPI(payment_id)
    mercadopago_response = mercadopago_api.fetch_payment_data()
    if mercadopago_response is None:
        logger.error(
            'Could not retrieve payment data for payment_id ' + payment_id
            + ' for user ' + request.user.email)
        messages.error(request,
                       _('Something went wrong. Please contact the staff if your '
                         'payment was made and will return you as soon as possible.'))
        return redirect('/')

    if mercadopago_api.payment_not_found():
        return HttpResponseBadRequest(_('Cannot process this request'))

    mp_payment_data = MercadoPagoPaymentData(mercadopago_response)
    course_id = mp_payment_data.get_course_id()
    get_object_or_404(Course, pk=int(course_id))
    new_payment_status = mp_payment_data.get_payment_status()

    if payment_status == FAILURE_STATUS:
        messages.error(request, _('There was an error with the payment'))
    if payment_status == SUCCESS_STATUS:
        messages.success(request, _('Payment Successful'))
    if payment_status == PENDING_STATUS:
        if new_payment_status == SUCCESS_STATUS:
            messages.success(request, _('Payment Successful'))
        else:
            messages.warning(request, _('Waiting for payment confirmation'))

    return redirect('enroll', course_id)


@csrf_exempt
@require_POST
def mercado_pago_webhook(request, token):
    # Request made probably outside MP Webhook
    if token != MERCADO_PAGO_WEBHOOK_TOKEN:
        logger.warning('Request receveid with wrong token')
        response = render(request, '404.html', {})
        response.status_code = HTTPStatus.NOT_FOUND
        return response

    body = json.loads(request.body)
    payment_id = body['data']['id']
    logger.info('Webhook called for payment id ' + payment_id)
    mercadopago_api = MercadoPagoAPI(payment_id)

    mercadopago_response = mercadopago_api.fetch_payment_data()
    if mercadopago_response is None:
        logger.error('Could not retrieve payment data')
        return HttpResponse('Could not retrieve payment data', status=HTTPStatus.OK)
    logger.info('Payment data for payment id ' + payment_id)
    logger.info(mercadopago_response)
    mp_payment_data = MercadoPagoPaymentData(mercadopago_response)
    course_id = mp_payment_data.get_course_id()
    logger.info('Gettting course object for course id ' + course_id)
    course = get_object_or_404(Course, pk=int(course_id))

    payer_email = mp_payment_data.get_payer_email()
    logger.info('Gettting user by payer email ' + payer_email)
    user = get_object_or_404(CustomUser, email=payer_email)
    payment_status = mp_payment_data.get_payment_status()

    coupon_code = mp_payment_data.get_coupon() if mp_payment_data.coupon_used()  \
        else ''

    try:
        course_user = CourseUser.objects.get(user=user, course=course,
                                             payment_id=payment_id)
    except CourseUser.DoesNotExist:
        course_user = None

    if body['action'] == 'payment.updated':
        if not course_user:
            logging.warning('Webhook request has status updated but the'
                            'CourseUser object was not created before for'
                            ' the payment id ' + payment_id)
            # TODO: unify string format; see other places
            return HttpResponse('Warning: payment {} was not created'.format(payment_id),
                                status=HTTPStatus.OK)
        elif course_user.payment_status == PENDING_STATUS \
                and payment_status == SUCCESS_STATUS:
            course_user.payment_status = payment_status
            course_user.save(update_fields=['payment_status'])

    if body['action'] == 'payment.created':
        if payment_status == SUCCESS_STATUS or payment_status == PENDING_STATUS:
            CourseUser.objects.create(
                course=course,
                user=user,
                status=ENROLL,
                payment_id=payment_id,
                payment_status=payment_status,
                coupon_used=coupon_code
            )
            course.registered += 1
            course.save(update_fields=['registered'])

    return HttpResponse('OK', status=HTTPStatus.OK)


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


@login_required
def material(request, template_name="base/material.html"):
    return render(request, template_name)


@login_required
def cursos_xsendfile(request):
    path = request.get_full_path()
    course_id = path.split("/")[3]
    course = get_object_or_404(Course, pk=course_id)
    try:
        CourseUser.objects.get(course=course, user=request.user)
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Sendfile'] = smart_str(path)
        return response
    except CourseUser.DoesNotExist:
        raise PermissionDenied


@login_required
def send_email(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            subject_typed = request.POST['subject']
            message_typed = request.POST['message']
            users = CustomUser.objects.all()
            list_of_emails = []
            text_content = message_typed
            html_content = message_typed

            for user in users:
                if user.email:
                    list_of_emails.append(user.email)

            if subject_typed and message_typed and list_of_emails:
                subject, from_email, to = subject_typed, settings.EMAIL_HOST_USER, list_of_emails

                if subject and from_email and to:
                    connection = mail.get_connection()
                    connection.open()

                    try:
                        msg = EmailMultiAlternatives(subject, text_content, from_email, bcc=to)
                        msg.attach_alternative(html_content, "text/html")
                        if request.FILES:
                            file_uploaded = request.FILES['attachment']
                            msg.attach(file_uploaded.name, file_uploaded.read(), file_uploaded.content_type)
                        msg.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

                    connection.close()
                    messages.success(request, _('Email successfully sent!'))
            else:
                messages.error(request, _('You must fill in the subject and message fields'))

        return render(request, 'base/send_email.html')
    else:
        raise PermissionDenied


@login_required
def users_report(request, course_id):
    if request.user.is_superuser:
        course = get_object_or_404(Course, pk=course_id)
        user_list = CourseUser.objects.filter(course=course)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={course.name}.csv'
        writer = csv.writer(response, delimiter=',')
        for item in user_list:
            writer.writerow([item.user, item.user.email])

        return response
    else:
        raise Http404
