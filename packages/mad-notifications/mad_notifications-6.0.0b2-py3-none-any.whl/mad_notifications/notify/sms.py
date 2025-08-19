from celery import shared_task
import logging
from mad_notifications.models import SMSProviderConfig, get_notification_model
from mad_notifications.senders.sms.telnyx import sendTelnyxSMSNotification
from mad_notifications.senders.sms.twilio import sendTwilioSMSNotification
from mad_notifications.settings import notification_settings

logger = logging.getLogger(__name__)


@shared_task(
    name="Non-Periodic: SMS notification",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def sms_notification(notification_id):
    try:
        notification_obj = (
            get_notification_model()
            .objects.select_related("user")
            .get(id=notification_id)
        )

        provider_config = SMSProviderConfig.objects.filter(
            is_active=True, is_default=True
        ).first()

        sms_sender = (
            provider_config.provider
            if provider_config
            else notification_settings.DEFAULT_SMS_PROVIDER
        )

        sender_map = {
            "Telnyx": sendTelnyxSMSNotification,
            "Twilio": sendTwilioSMSNotification,
        }

        if sms_sender not in sender_map:
            raise ValueError(f"Invalid SMS provider: {sms_sender}")

        sender_func = sender_map[sms_sender]
        sender_func(notification_obj)
        return f"SMS notifications sent via {sms_sender}"
    except Exception as e:
        logger.error("SMS notification failed: %s", str(e), exc_info=True)
        raise
