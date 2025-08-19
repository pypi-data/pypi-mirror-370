from celery import shared_task
import logging
from mad_notifications.models import get_notification_model
from mad_notifications.senders.sms.twilio import (
    sendTwilioWhatsAppNotification,
)

logger = logging.getLogger(__name__)


# Tasks to send respective notifications


@shared_task(name="Non-Periodic: WhatsApp notification")
def whatsApp_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)

        try:
            sendTwilioWhatsAppNotification(notification_obj)
            return "WhatsApp notifications sent via Twilio"
        except Exception as e:  # noqa: E722
            logger.warning(f"Tried WhatsApp Notification, got: {e!s}")

    except Exception as e:
        logger.error(str(e))
        return "Unable to send WhatsApp notification: " + str(e)
