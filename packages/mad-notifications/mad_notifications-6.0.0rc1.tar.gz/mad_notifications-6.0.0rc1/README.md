# Mad Notifications

Mad Notifications app for django to send notifications to the user

## Quick start

1. Add "mad_notifications" to your INSTALLED_APPS setting like this:

   ```python
   INSTALLED_APPS = [
       ...
       'mad_notifications',
   ]
   ```

2. Include the notifications URLconf in your project urls.py like this:

   ```python
   path('notifications/', include('mad_notifications.api.urls')),
   ```

3. Run `python manage.py migrate` to create the notifications models.

## Usage

### Shorthand method

```python
from mad_notifications.shorthand import newNotification
# create and send
return newNotification(
    user=user, # django user object
    title="", # string
    content="", # string
    template_slug = None, # string - slug from mad_notification.NotificationTemplate
    data = {}, # dict
    actions = {} # dict
)
```

### Notification Class

```python
from mad_notifications.notification import Notification
# create a notification
notification = Notification(
    user = user,
    title = "New Order",
    content = "You have a new order!",
    data = {
        'order': order_data,
    },
    actions = {
        'click_action': "ORDER_SCREEN"
    },
    template = email_template, # mad_notification.NotificationTemplate Object
)
# send the notification
notification.notify()
```

## Overriding default

```python

MAD_NOTIFICATIONS_USER_NOTIFICATION_CONFIG_MODEL = "mad_notifications.UserNotificationConfig"
MAD_NOTIFICATIONS_NOTIFICATION_MODEL = "mad_notifications.Notification"
MAD_NOTIFICATIONS_TEMPLATE_MODEL = "mad_notifications.NotificationTemplate"
MAD_NOTIFICATIONS_DEVICE_MODEL = "mad_notifications.Device"
MAD_NOTIFICATIONS_DEFAULT_SMS_PROVIDER = "Twilio" # valid values "Twilio" / "Telnyx"

TWILIO_ACCOUNT_SID = ""
TWILIO_ACCOUNT_AUTH_TOKEN = ""
TWILIO_ACCOUNT_PHONE_NUMBER = ""

TELNYX_API_KEY = ""
TELNYX_MESSAGING_PROFILE = ""
TELNYX_FROM_PHONE_NUMBER = ""


MAD_NOTIFICATIONS = {
    "FIREBASE_MOBILE_PUSH_NOTIFICATION_CLASS": "mad_notifications.senders.firebase.FirebaseMobilePushNotification",
    "EMAIL_NOTIFICATION_CLASS": "mad_notifications.senders.email.EmailNotification",

    "TWILIO_NOTIFICATION_CLASS": "mad_notifications.senders.twilio.TwilioNotification",
    "TELNYX_NOTIFICATION_CLASS": "mad_notifications.senders.telnyx.TelnyxNotification",

    # User config
    "USER_NOTIFICATION_CONFIG_ADMIN_CLASS": "mad_notifications.admin.UserNotificationConfigAdmin",
    # Notification Templates
    "NOTIFICATION_TEMPLATE_ADMIN_CLASS": "mad_notifications.admin.NotificationTemplateAdmin",
    # Device
    "DEVICE_ADMIN_CLASS": "mad_notifications.admin.DeviceAdmin",
    "NOTIFICATION_ADMIN_CLASS": "mad_notifications.admin.NotificationAdmin",
}
```

## Developer Guide

### Setting up a new provider

Create logic in `~/senders/PROVIDER.py` and call via tasks in `~/notify/PROVIDER.py`
