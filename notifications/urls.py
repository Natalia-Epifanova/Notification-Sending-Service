from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .apps import NotificationsConfig
from .views import (MyTokenObtainPairView, NotificationViewSet, RegisterView,
                    UserContactsViewSet)

app_name = NotificationsConfig.name
router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"user-contacts", UserContactsViewSet, basename="user-contacts")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
