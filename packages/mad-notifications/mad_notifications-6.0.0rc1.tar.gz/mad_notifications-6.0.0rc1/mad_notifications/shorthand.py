import logging

from mad_notifications.models import get_notification_template_model
from mad_notifications.notification import Notification

logger = logging.getLogger(__name__)


def newNotification(user, title, content, template_slug=None, **kwargs):
    """
    Shorthand method to create and send notification

    `title`, `content` will be overridden if `template_slug` is provided

    """
    # get email template from db
    if template_slug is not None:
        try:
            notification_template = get_notification_template_model().objects.get(
                slug=template_slug
            )
        except Exception as e:
            logger.warning("mad_notifications.shorthand.newNotification: %s", str(e))
            notification_template = None
    else:
        notification_template = None

    # create a notification for user
    notification = Notification(
        user=user,
        title=title,
        content=str(content),
        mobile_content=str(content),
        template=notification_template,
        **kwargs,
    )

    return notification.notify()
