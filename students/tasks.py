from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.contrib.auth import get_user_model


logger = logging.getLogger("users")


@shared_task
def send_welcome_email(user_id):

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
        subject = 'Welcome to Our Platform!'
        message = f'Hello {user.username},\n\nThank you for registering at our platform. We are excited to have you onboard!\n\nBest Regards,\nTeam'
        recipient_list = [user.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user.email}")
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send welcome email to user id {user_id}: {str(e)}")
