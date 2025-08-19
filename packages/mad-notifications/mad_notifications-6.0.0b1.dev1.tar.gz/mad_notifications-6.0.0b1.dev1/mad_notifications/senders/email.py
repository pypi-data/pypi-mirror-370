import datetime
from django.conf import settings
from mad_notifications.settings import notification_settings
from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
import logging

from mad_notifications.user import NotificationConfig

logger = logging.getLogger(__name__)


class EmailNotification(NotificationConfig):

    def __init__(self, notification):
        self.notification = notification

    def emailNotification(self):
        notification_obj = self.notification

        # from email
        try:
            if (
                notification_obj.template.from_email is not None
                or notification_obj.template.from_email != ""
            ):
                from_email = notification_obj.template.from_email
        except Exception as e:
            logger.warn(str(e))
            from_email = settings.DEFAULT_FROM_EMAIL

        # send email
        try:
            sent = send_mail(
                subject=notification_obj.title,
                message=notification_obj.content,
                from_email=from_email,
                recipient_list=[notification_obj.user.email],
                fail_silently=False,
                html_message=notification_obj.content,
            )
            return sent
        except Exception as e:
            raise


def sendEmailNotification(notification):
    email_notification = notification_settings.EMAIL_NOTIFICATION_CLASS(notification)
    return email_notification.emailNotification()
