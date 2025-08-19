from django.db import models
from django.core.exceptions import ValidationError


class FirebaseConfig(models.Model):
    """Configuration model for Firebase push notifications."""

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

    def clean(self):
        if self.is_default:
            # Ensure only one default provider
            default_exists = (
                SMSProviderConfig.objects.filter(is_default=True)
                .exclude(id=self.id)
                .exists()
            )

            if default_exists:
                raise ValidationError(
                    "Another provider is already set as default. "
                    "Please unset the existing default first."
                )

        # Validate required fields based on provider
        if self.provider == "Twilio":
            if not all([self.account_sid, self.auth_token, self.phone_number]):
                raise ValidationError(
                    "Twilio provider requires account_sid, auth_token and phone_number"
                )
        elif self.provider == "Telnyx":
            if not all([self.api_key, self.messaging_profile, self.phone_number]):
                raise ValidationError(
                    "Telnyx provider requires api_key, messaging_profile and phone_number"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
