import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

from users.models import User

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged in.")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged out.")

@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    if created:
        logger.info(f"User {instance.username} registered.")