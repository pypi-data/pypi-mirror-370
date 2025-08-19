from typing import Any, Dict, Optional
from django.template import Template, Context
from mad_notifications.models import get_notification_model, NotificationTemplate

import logging

logger = logging.getLogger(__name__)


class Notification:
    """
    Handles notification creation and template rendering.

    This class manages notification objects, handles template rendering,
    and provides notification creation functionality.
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialize notification with provided parameters.

        Args:
            **kwargs: Dictionary containing notification parameters
        """
        self.notification_obj = kwargs
        self._process_notification()

    def _process_notification(self) -> None:
        """Process and render notification templates."""
        try:
            context = Context(self.notification_obj.get("data", {}))
            self._render_notification_content(context)
        except Exception as e:
            logger.error("Error processing notification: %s", str(e), exc_info=True)
            raise

    def _render_notification_content(self, context: Context) -> None:
        """
        Render notification content using templates.

        Args:
            context: Template context for rendering
        """
        template = self.notification_obj.get("template")

        if isinstance(template, NotificationTemplate):
            self._render_from_notification_template(template, context)
        else:
            self._render_from_raw_content(context)

    def _render_from_notification_template(
        self, template: NotificationTemplate, context: Context
    ) -> None:
        """
        Render content from a NotificationTemplate instance.

        Args:
            template: NotificationTemplate instance
            context: Template context for rendering
        """
        self.notification_obj["title"] = Template(template.subject).render(context)
        self.notification_obj["content"] = Template(template.content).render(context)
        self.notification_obj["mobile_content"] = Template(
            template.mobile_content
        ).render(context)

    def _render_from_raw_content(self, context: Context) -> None:
        """
        Render content from raw notification object fields.

        Args:
            context: Template context for rendering
        """
        for field in ("title", "content", "mobile_content"):
            content = self.notification_obj.get(field, "")
            self.notification_obj[field] = (
                Template(content).render(context) if content else ""
            )

    def notify(self, fail_silently: bool = False) -> Optional[Any]:
        """
        Create notification in database.

        Args:
            fail_silently: If True, suppress exceptions

        Returns:
            Created notification object or None if failed and fail_silently is True

        Raises:
            Exception: If creation fails and fail_silently is False
        """
        try:
            return get_notification_model().objects.create(**self.notification_obj)
        except Exception as e:
            logger.error("Failed to create notification: %s", str(e), exc_info=True)
            if not fail_silently:
                raise
            return None
