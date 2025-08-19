from django.conf import settings
from django.utils.module_loading import import_string
from django.test.signals import setting_changed

USER_SETTINGS = getattr(settings, "MAD_NOTIFICATIONS", None)


USER_NOTIFICATION_CONFIG_MODEL = getattr(
    settings,
    "MAD_NOTIFICATIONS_USER_NOTIFICATION_CONFIG_MODEL",
    "mad_notifications.UserNotificationConfig",
)

NOTIFICATION_MODEL = getattr(
    settings, "MAD_NOTIFICATIONS_NOTIFICATION_MODEL", "mad_notifications.Notification"
)
NOTIFICATION_TEMPLATE_MODEL = getattr(
    settings,
    "MAD_NOTIFICATIONS_TEMPLATE_MODEL",
    "mad_notifications.NotificationTemplate",
)
DEVICE_MODEL = getattr(
    settings, "MAD_NOTIFICATIONS_DEVICE_MODEL", "mad_notifications.Device"
)

# DEFAULT SMS PROVIDER
DEFAULT_SMS_PROVIDER = getattr(
    settings,
    "MAD_NOTIFICATIONS_DEFAULT_SMS_PROVIDER",
    "Twilio",  # defaults to Twilio
)

# TWILIO
TWILIO_ACCOUNT_SID = getattr(settings, "TWILIO_ACCOUNT_SID", None)
TWILIO_ACCOUNT_AUTH_TOKEN = getattr(settings, "TWILIO_ACCOUNT_AUTH_TOKEN", None)
TWILIO_ACCOUNT_PHONE_NUMBER = getattr(settings, "TWILIO_ACCOUNT_PHONE_NUMBER", None)

# TELNYX
TELNYX_API_KEY = getattr(settings, "TELNYX_API_KEY", None)
TELNYX_MESSAGING_PROFILE = getattr(settings, "TELNYX_MESSAGING_PROFILE", None)
TELNYX_FROM_PHONE_NUMBER = getattr(settings, "TELNYX_FROM_PHONE_NUMBER", None)

DEFAULTS = {
    #
    "NOTIFICATION_MODEL": NOTIFICATION_MODEL,
    "NOTIFICATION_TEMPLATE_MODEL": NOTIFICATION_TEMPLATE_MODEL,
    "DEVICE_MODEL": DEVICE_MODEL,
    "USER_NOTIFICATION_CONFIG_MODEL": USER_NOTIFICATION_CONFIG_MODEL,
    #
    #
    # Firebase Defaults
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS": "mad_notifications.senders.push.firebase.FirebaseMobilePushNotification",
    # Email Defaults
    "EMAIL_NOTIFICATION_CLASS": "mad_notifications.senders.email.EmailNotification",
    # SMS Defaults
    "DEFAULT_SMS_PROVIDER": DEFAULT_SMS_PROVIDER,
    ## Twilio Defaults
    "TWILIO_NOTIFICATION_CLASS": "mad_notifications.senders.sms.twilio.TwilioNotification",
    "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
    "TWILIO_ACCOUNT_AUTH_TOKEN": TWILIO_ACCOUNT_AUTH_TOKEN,
    "TWILIO_ACCOUNT_PHONE_NUMBER": TWILIO_ACCOUNT_PHONE_NUMBER,
    ## Telnyx Defaults
    "TELNYX_NOTIFICATION_CLASS": "mad_notifications.senders.sms.telnyx.TelnyxNotification",
    "TELNYX_API_KEY": TELNYX_API_KEY,
    "TELNYX_MESSAGING_PROFILE": TELNYX_MESSAGING_PROFILE,
    "TELNYX_FROM_PHONE_NUMBER": TELNYX_FROM_PHONE_NUMBER,
    # User config
    "USER_NOTIFICATION_CONFIG_ADMIN_CLASS": "mad_notifications.admin.UserNotificationConfigAdmin",
    # Notification Templates
    "NOTIFICATION_TEMPLATE_ADMIN_CLASS": "mad_notifications.admin.NotificationTemplateAdmin",
    # Device
    "DEVICE_ADMIN_CLASS": "mad_notifications.admin.DeviceAdmin",
    "NOTIFICATION_ADMIN_CLASS": "mad_notifications.admin.NotificationAdmin",
    # Add more as required.
}

IMPORT_STRINGS = (
    # PUSH
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS",
    # EMAIL
    "EMAIL_NOTIFICATION_CLASS",
    # SMS
    "TWILIO_NOTIFICATION_CLASS",
    "TELNYX_NOTIFICATION_CLASS",
    #
    "USER_NOTIFICATION_CONFIG_ADMIN_CLASS",
    "NOTIFICATION_TEMPLATE_ADMIN_CLASS",
    "DEVICE_ADMIN_CLASS",
    "NOTIFICATION_ADMIN_CLASS",
)

MANDATORY = IMPORT_STRINGS


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class MadNotificationSettings:
    def __init__(
        self, user_settings=None, defaults=None, import_strings=None, mandatory=None
    ):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "MAD_NOTIFICATIONS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Mad Notifications setting: %s" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("mad_notifications setting: %s is mandatory" % attr)

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


notification_settings = MadNotificationSettings(
    USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY
)


def reload_mad_notification_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "MAD_NOTIFICATIONS":
        notification_settings.reload()


setting_changed.connect(reload_mad_notification_settings)
