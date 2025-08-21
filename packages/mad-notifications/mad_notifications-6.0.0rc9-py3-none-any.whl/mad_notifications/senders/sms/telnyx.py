import logging
from typing import Dict, Any

import telnyx
from mad_notifications.models import SMSProviderConfig
from mad_notifications.senders.sms.base import BaseNotificationSender

logger = logging.getLogger(__name__)


class TelnyxNotification(BaseNotificationSender):
    """Telnyx notification sender implementation"""

    def configure(self) -> None:
        """Configure Telnyx client with credentials"""
        try:
            config = SMSProviderConfig.objects.get(provider="Telnyx", is_active=True)
            self.api_key = config.api_key
            self.messaging_profile = config.messaging_profile
            self.from_number = config.phone_number

            self.profile = telnyx.MessagingProfile.retrieve(self.messaging_profile)

        except SMSProviderConfig.DoesNotExist:
            logger.error("No active Telnyx configuration found")
            raise ValueError("Telnyx configuration not found or inactive")

    def get_message_payload(self) -> Dict[str, str]:
        """Build Telnyx message payload"""
        return {
            "from": f"+{self.from_number}",
            "to": str(self.notification.user.phone),
            "text": self.notification.mobile_content,
            "api_key": self.api_key,
            "messaging_profile_id": self.messaging_profile,
            "type": "SMS",
        }

    def send(self) -> Any:
        """Send SMS via Telnyx"""
        try:
            message = self.get_message_payload()
            return telnyx.Message.create(**message)
        except Exception as e:
            logger.exception("Telnyx SMS sending failed: %s", str(e))
            raise


def sendTelnyxSMSNotification(notification: Any) -> Any:
    """Helper function to send Telnyx SMS notification"""
    telnyx_notification = TelnyxNotification(notification)
    return telnyx_notification.send()
