from django.db.models.signals import post_save
from django.dispatch import receiver
from mad_notifications.notify.email import email_notification
from mad_notifications.notify.push import push_notification
from mad_notifications.models import get_notification_model
from mad_notifications.notify.sms import sms_notification
from mad_notifications.notify.whatsapp import whatsApp_notification


@receiver(post_save, sender=get_notification_model())
def NotificationPostSave(sender, instance, created, update_fields, **kwargs):
    # Only trigger notifications on creation, not updates
    if not created:
        return

    # Bundle async tasks together
    tasks = []
    if instance.allow_push:
        tasks.append(push_notification.s(instance.id))
    if instance.allow_email:
        tasks.append(email_notification.s(instance.id))
    if instance.allow_sms:
        tasks.append(sms_notification.s(instance.id))
    if instance.allow_whatsapp:
        tasks.append(whatsApp_notification.s(instance.id))

    # Execute tasks in chord if available
    if tasks:
        from celery import chord

        chord(tasks)(None)
