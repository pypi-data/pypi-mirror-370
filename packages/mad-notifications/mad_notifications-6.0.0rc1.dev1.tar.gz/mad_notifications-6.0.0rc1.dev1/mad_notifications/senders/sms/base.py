from abc import ABC, abstractmethod
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseNotificationSender(ABC):
    """Base class for all notification senders"""

    def __init__(self, notification):
        self.notification = notification
        self.configure()

    @abstractmethod
    def configure(self) -> None:
        """Configure sender with necessary settings"""
        pass

    @abstractmethod
    def send(self) -> Any:
        """Send the notification"""
        pass

    def get_message_payload(self) -> Dict:
        """Get message payload for the notification"""
        pass
