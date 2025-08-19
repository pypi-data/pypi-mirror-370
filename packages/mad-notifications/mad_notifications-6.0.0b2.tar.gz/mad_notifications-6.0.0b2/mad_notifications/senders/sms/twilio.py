import logging
from typing import Dict, Any

from twilio.rest import Client

from mad_notifications.models import SMSProviderConfig
from mad_notifications.senders.sms.base import BaseNotificationSender

logger = logging.getLogger(__name__)


class TwilioNotification(BaseNotificationSender):
    """Twilio notification sender implementation"""

    def configure(self) -> None:
        """Configure Twilio client with credentials"""
        try:
            config = SMSProviderConfig.objects.get(provider="Twilio", is_active=True)
            self.account_sid = config.account_sid
            self.auth_token = config.auth_token
            self.from_number = config.phone_number

            self.client = Client(self.account_sid, self.auth_token)

        except SMSProviderConfig.DoesNotExist:
            logger.error("No active Twilio configuration found")
            raise ValueError("Twilio configuration not found or inactive")

    def get_message_payload(self, is_whatsapp: bool = False) -> Dict[str, str]:
        """Build Twilio message payload"""
        from_prefix = "whatsapp:" if is_whatsapp else ""
        to_prefix = "whatsapp:" if is_whatsapp else ""
        return {
            "body": self.notification.mobile_content,
            "from_": f"{from_prefix}{self.from_number}",
            "to": f"{to_prefix}{self.notification.user.phone}",
        }

    def send(self, is_whatsapp: bool = False) -> Any:
        """Send message via Twilio"""
        try:
            message = self.get_message_payload(is_whatsapp)
            return self.client.messages.create(**message)
        except Exception as e:
            service = "WhatsApp" if is_whatsapp else "SMS"
            logger.exception(f"Twilio {service} sending failed: %s", str(e))
            raise


def sendTwilioSMSNotification(notification: Any) -> Any:
    """Helper function to send Twilio SMS notification"""
    twilio_notification = TwilioNotification(notification)
    return twilio_notification.send()


def sendTwilioWhatsAppNotification(notification: Any) -> Any:
    """Helper function to send Twilio WhatsApp notification"""
    twilio_notification = TwilioNotification(notification)
    return twilio_notification.send(is_whatsapp=True)
