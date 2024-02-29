from django.contrib import admin
from django.db import ProgrammingError
from django.urls import include, path, re_path

from . import views
from control_server.views import ApiLoginView
from honeypot.views import fingerprint, browser_info

handler404 = views.handler404
handler500 = views.handler500

try:
    urlpatterns = [
        # XHR endpoints
        re_path(r"fingerprint/?$", fingerprint, name="fingerprint"),
        re_path(r"browser_info/?$", browser_info, name="browser_info"),

        re_path(r"^admin/", admin.site.urls),

        # view for API login using BasicAuthentication
        re_path(r"^api-login/", ApiLoginView.as_view()),

        # control server api
        path("api/", include("control_server.urls")),

        # rest authentication
        path("", include("rest_framework.urls", namespace="rest_framework")),

        # all other urls lead to the honeypot
        path("", include("honeypot.urls")),
    ]
except ProgrammingError:
    urlpatterns = []
