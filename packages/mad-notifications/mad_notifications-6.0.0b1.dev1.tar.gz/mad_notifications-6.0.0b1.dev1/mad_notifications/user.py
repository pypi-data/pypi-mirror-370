from mad_notifications.models import get_user_notification_config_model

# User notification configurations
class NotificationConfig:
    def __init__(self, notification):
        self.notification = notification
        
        # check if notification config object exists for this user or not, if doesnt exist, create a new object and process accordingly
        nConfig, created = get_user_notification_config_model().objects.get_or_create(
            user = self.notification.user
        )
        
        self.nConfig = nConfig
        # else check to see if the notifaction on that channel is allowed or not.