from mad_notifications.models import (
    Device,
    get_device_model,
    get_notification_model,
    get_user_notification_config_model,
)
from mad_notifications.api.serializers import (
    DeviceSerializer,
    NotificationSerializer,
    UserNotificationConfigSerializer,
)
from rest_framework import viewsets, mixins, serializers
from rest_framework.response import Response

# Create your views here.


class UserNotificationConfigViewSet(viewsets.ModelViewSet):
    this_view = "notifications"

    throttle_scope = this_view
    required_alternate_scopes = {
        "GET": [[this_view + ":read"]],
        "PUT": [[this_view + ":update"]],
        "PATCH": [[this_view + ":update"]],
    }

    queryset = (
        get_user_notification_config_model().objects.all().order_by("-created_at")
    )
    serializer_class = UserNotificationConfigSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class DeviceViewSet(viewsets.ModelViewSet):
    this_view = "device"

    throttle_scope = this_view
    required_alternate_scopes = {
        "GET": [[this_view + ":read"]],
        "POST": [[this_view + ":create"]],
        "PUT": [[this_view + ":update"]],
        "PATCH": [[this_view + ":update"]],
        "DELETE": [[this_view + ":delete"]],
    }

    queryset = get_device_model().objects.all().order_by("-created_at")
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        token = self.request.data.get("token", None)
        try:
            Device.objects.get(token=token, user=self.request.user)
            raise serializers.ValidationError(
                {"error": "Device token already exists for this user"}
            )
        except Device.DoesNotExist:
            return serializer.save(user=self.request.user)


class NotificationViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """
    User Notifications API
    """

    this_view = "notifications"

    throttle_scope = this_view
    required_alternate_scopes = {
        "GET": [[this_view + ":read"]],
        "POST": [[this_view + ":create"]],
        "PUT": [[this_view + ":update"]],
        "PATCH": [[this_view + ":update"]],
        "DELETE": [[this_view + ":delete"]],
    }

    queryset = get_notification_model().objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    search_fields = ["title", "content"]
    filterset_fields = [
        "is_read",
    ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_read:
            instance.is_read = True
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
