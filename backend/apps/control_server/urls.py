from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from control_server import views
from control_server.views import AuthTokenViewSet, UpdatePassword
from honeypot.views import (
    HoneypageViewSet, HoneymailViewSet, AccessLogViewSet, FingerprintLogViewSet,
    FingerprintViewSet, BrowserFingerprintLogViewSet, resource_view
)

router = DefaultRouter()

# logs
router.register(r"access_logs", AccessLogViewSet)

# fingerprints
router.register(r"fingerprints", FingerprintViewSet)
router.register(r"fingerprint_logs", FingerprintLogViewSet)
router.register(r"browser_fingerprint_logs", BrowserFingerprintLogViewSet)

# base models
router.register(r"users", views.UserViewSet)
router.register(r"messengers", views.MessengerViewSet)
router.register(r"experiments", views.ExperimentViewSet)

# honeydata
router.register(r"honeypages", HoneypageViewSet)
router.register(r"honeymails", HoneymailViewSet)
# other
# router.register(r"emails", EmailViewSet)

schema = get_schema_view(
    title="Honeymessages API",
    description="API to interact with the Honeymessages Framework",
    version="0.0.4",
)

urlpatterns = [
    path("schema/", schema, name="openapi-schema"),
    path("token-auth/", csrf_exempt(AuthTokenViewSet.as_view())),
    path("change-password/", UpdatePassword.as_view()),

    re_path(r"(?P<resource_name>[\w-]+)\.(?P<file_ending>[\w.]+)/?$", resource_view),

    path("", include(router.urls)),
]
