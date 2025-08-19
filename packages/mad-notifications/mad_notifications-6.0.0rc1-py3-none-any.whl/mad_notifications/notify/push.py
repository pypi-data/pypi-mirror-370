import logging
import firebase_admin
import json
from django.core.cache import cache
from mad_notifications.models import get_notification_model, FirebaseConfig
from celery import shared_task
from mad_notifications.senders.push.firebase import sendFirebaseMobilePushNotification

logger = logging.getLogger(__name__)


def get_firebase_app():
    """
    Get or initialize Firebase app using credentials from database.
    Returns Firebase app instance.
    """
    app = cache.get("firebase_app")
    if app:
        return app

    config = FirebaseConfig.objects.filter(is_active=True, is_default=True).first()
    if not config:
        raise ValueError("No active Firebase configuration found")

    creds = json.loads(config.credentials_json)
    app = firebase_admin.initialize_app(firebase_admin.credentials.Certificate(creds))

    cache.set("firebase_app", app, timeout=3600)  # Cache for 1 hour
    return app


@shared_task(
    name="Non-Periodic: Push notification",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def push_notification(notification_id):
    try:
        notification_obj = (
            get_notification_model()
            .objects.select_related("user")
            .get(id=notification_id)
        )
        devices = notification_obj.user.device_set.all()

        if not notification_obj.mobile_content:
            return "Error: Notification has no content"

        firebase_app = get_firebase_app()

        for device in devices:
            try:
                sendFirebaseMobilePushNotification(device, notification_obj)
                logger.info("Push notification sent to device: %s", device.id)
            except Exception as e:
                logger.error(
                    "Could not send push notification to device: %s message: %s",
                    device.id,
                    str(e),
                )
                # TODO: Implement device cleanup logic if needed

        return "Push notifications sent successfully"
    except Exception as e:
        logger.error("Push notification failed: %s", str(e), exc_info=True)
        raise
