from mad_notifications.api.views import DeviceViewSet, NotificationViewSet, UserNotificationConfigViewSet
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('config', UserNotificationConfigViewSet)
router.register('notification', NotificationViewSet)
router.register('device', DeviceViewSet)

urlpatterns = router.urls
urlpatterns += [
]
