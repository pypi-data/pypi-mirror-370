from mad_notifications.models import Device, Notification, get_device_model, get_notification_model, get_user_notification_config_model
from rest_framework import serializers


class UserNotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_notification_config_model()
        fields = '__all__'
        read_only_fields = ('user',)
        


class DeviceSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, required=True)
    class Meta:
        model = get_device_model()
        fields = (
            'id',
            'user',
            'token',

            'created_at', 'updated_at',
            'url',
        )

        read_only_fields = ('user',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_notification_model()
        fields = (
            'id',
            'user',
            'title',
            'content',
            'is_read',
            'icon',
            'image',
            "data",
            "actions",

            'created_at', 'updated_at',
            'url',
        )
        read_only_fields = fields
