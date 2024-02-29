from django.apps import AppConfig


class ControlServerConfig(AppConfig):
    name = "control_server"
    verbose_name = "Control Server"

    def ready(self):
        print("Control Server ready")
