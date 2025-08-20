from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mad_notifications"
    verbose_name = "Notifications"

    def ready(self):
        # Import signals so receivers register at startup
        from mad_notifications import signals  # noqa: F401, PLC0415
