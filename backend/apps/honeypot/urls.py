from django.urls import re_path

from . import views

app_name = "honeypot"


urlpatterns = [
    # honeypage resource routing
    re_path(r"(?P<resource_name>[\w-]+)\.(?P<file_ending>[\w.]+)/?$", views.resource_view),

    # anything else goes to a honeypage
    re_path(r"^(?:(?P<slug>.+)/?)?$", views.HoneyPageView.as_view()),
]
