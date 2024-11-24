from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course
import logging

logger = logging.getLogger("courses")

@shared_task
def send_course_creation_email(course_id):
    try:
        course = Course.objects.get(id=course_id)
        subject = f'New Course Created: {course.name}'
        message = f'A new course "{course.name}" has been created and is now available.'
        recipient_list = [course.instructor.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

        logger.info(f"Course creation email sent to {course.instructor.email}")
    except Course.DoesNotExist:
        logger.error(f"Course with id {course_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send course creation email: {str(e)}")
