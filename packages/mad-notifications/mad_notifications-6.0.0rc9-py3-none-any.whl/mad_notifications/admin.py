from django.contrib import admin

from mad_notifications.models import get_device_admin_class
from mad_notifications.models import get_device_model
from mad_notifications.models import get_firebase_config_admin_class
from mad_notifications.models import get_firebase_config_model
from mad_notifications.models import get_notification_admin_class
from mad_notifications.models import get_notification_model
from mad_notifications.models import get_notification_template_admin_class
from mad_notifications.models import get_notification_template_model
from mad_notifications.models import get_sms_provider_config_admin_class
from mad_notifications.models import get_sms_provider_config_model
from mad_notifications.models import get_user_notification_config_admin_class
from mad_notifications.models import get_user_notification_config_model


class SMSProviderConfigAdmin(admin.ModelAdmin):
    list_display = ["provider", "is_active", "is_default", "created_at", "updated_at"]
    list_filter = ["provider", "is_active", "is_default"]
    search_fields = ["provider"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("provider", "is_active", "is_default")}),
        ("Base Config", {"fields": ("phone_number",)}),
        (
            "Twilio Configuration",
            {
                "fields": ("account_sid", "auth_token"),
                "classes": ("collapse",),
            },
        ),
        (
            "Telnyx Configuration",
            {
                "fields": ("api_key", "messaging_profile"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


class FirebaseConfigAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "is_default", "created_at", "updated_at"]
    list_filter = ["is_active", "is_default"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("credentials_json", "is_active", "is_default")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class UserNotificationConfigAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in get_user_notification_config_model()._meta.get_fields()
    ]
    list_filter = ("created_at",)
    ordering = ("-created_at",)


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "from_email", "from_phone", "slug", "created_at"]
    list_filter = ("created_at",)
    ordering = ("-created_at",)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    raw_id_fields = ("user",)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "title", "is_read", "created_at"]
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    raw_id_fields = ("user", "template")


# Model calls
userConfig_model = get_user_notification_config_model()
notificationTemplate_model = get_notification_template_model()
device_model = get_device_model()
notification_model = get_notification_model()
firebase_config_model = get_firebase_config_model()
sms_provider_config_model = get_sms_provider_config_model()

# Classes
userConfig_admin_class = get_user_notification_config_admin_class()
notificationTemplate_admin_class = get_notification_template_admin_class()
device_admin_class = get_device_admin_class()
notification_admin_class = get_notification_admin_class()
firebase_config_admin_class = get_firebase_config_admin_class()
sms_provider_config_admin_class = get_sms_provider_config_admin_class()

# admin reg
admin.site.register(userConfig_model, userConfig_admin_class)
admin.site.register(notificationTemplate_model, notificationTemplate_admin_class)
admin.site.register(device_model, device_admin_class)
admin.site.register(notification_model, notification_admin_class)
admin.site.register(firebase_config_model, firebase_config_admin_class)
admin.site.register(sms_provider_config_model, sms_provider_config_admin_class)
