from celery import shared_task
import logging
from mad_notifications.models import get_notification_model
from mad_notifications.senders.email import sendEmailNotification

logger = logging.getLogger(__name__)

@shared_task(name="Non-Periodic: Email notification")
def email_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)

        sendEmailNotification(notification_obj)
        return "Email notifications sent"

    except Exception as e:
        logger.error(str(e))
        return "Unable to send Email notification: " + str(e)
