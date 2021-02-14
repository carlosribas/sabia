import datetime

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from base.models import Course, CourseUser, CourseMaterial


def run():
    target_date = datetime.date.today() + datetime.timedelta(days=1)

    # find courses starting tomorrow
    for course in Course.objects.filter(start_date=target_date):

        # get the broadcast link
        course_material = CourseMaterial.objects.filter(course=course).first()
        link = course_material.link

        # find the users that are registered for the course
        for item in CourseUser.objects.filter(course=course):

            # Send email to the user
            subject = '[Plataforma Sabiá] - É amanhã! {}'.format(course.name)
            html_message = render_to_string(
                'mail_template.html',
                {
                    'name': item.user.first_name,
                    'course': course.name,
                    'start_date': course.start_date,
                    'end_date': course.end_date,
                    'start_time': course.start_time,
                    'link': link
                }
            )
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to = item.user.email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
