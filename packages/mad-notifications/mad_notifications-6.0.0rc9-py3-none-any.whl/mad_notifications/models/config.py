from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models

from mad_notifications.settings import notification_settings


class FirebaseConfig(models.Model):
    """Configuration model for Firebase push notifications."""

    project_id = models.CharField(max_length=20, blank=False, null=True)  # noqa: DJ001
    credentials_json = models.TextField(
        help_text="Firebase service account credentials JSON"
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Firebase Configuration"
        verbose_name_plural = "Firebase Configurations"

    def __str__(self):
        return f"Firebase Config ({self.id})"


class SMSProviderConfig(models.Model):
    """Configuration model for SMS providers"""

    PROVIDER_CHOICES = [("Twilio", "Twilio"), ("Telnyx", "Telnyx")]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        unique=True,
        help_text="SMS provider service",
    )
    is_active = models.BooleanField(
        default=False, help_text="Whether this provider is currently active"
    )
    is_default = models.BooleanField(
        default=False, help_text="Whether this is the default provider"
    )

    # Provider specific fields
    account_sid = models.CharField(max_length=255, blank=True)  # For Twilio
    auth_token = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Telnyx specific fields
    api_key = models.CharField(max_length=255, blank=True)
    messaging_profile = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SMS Provider Configuration"
        verbose_name_plural = "SMS Provider Configurations"

    def __str__(self):
        return f"SMS Provider Config ({self.id})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.is_default:
            # Ensure only one default provider
            default_exists = (
                SMSProviderConfig.objects.filter(is_default=True)
                .exclude(id=self.id)
                .exists()
            )

            if default_exists:
                msg = (
                    "Another provider is already set as default. "
                    "Please unset the existing default first."
                )
                raise ValidationError(msg)

        # Validate required fields based on provider
        if self.provider == "Twilio":
            if not all([self.account_sid, self.auth_token, self.phone_number]):
                msg = (
                    "Twilio provider requires account_sid, auth_token and phone_number"
                )
                raise ValidationError(msg)
        elif self.provider == "Telnyx":
            if not all([self.api_key, self.messaging_profile, self.phone_number]):
                msg = "Telnyx provider requires api_key, messaging_profile and phone_number"
                raise ValidationError(msg)


def get_sms_provider_config_model():
    """Return the SMS_PROVIDER_CONFIG_MODEL in this project."""
    return apps.get_model(notification_settings.SMS_PROVIDER_CONFIG_MODEL)


def get_firebase_config_model():
    """Return the SMS_PROVIDER_CONFIG_MODEL in this project."""
    return apps.get_model(notification_settings.FIREBASE_CONFIG_MODEL)


## Admin classes
def get_sms_provider_config_admin_class():
    return notification_settings.SMS_PROVIDER_CONFIG_ADMIN_CLASS


def get_firebase_config_admin_class():
    return notification_settings.FIREBASE_CONFIG_ADMIN_CLASS
