from django.conf import settings
from django.contrib.auth.models import User

from control_server.models import Experiment


def export_vars(request):
    """
    Can be enabled in Django common settings under context_processors in the TEMPLATES section.
    This context processor adds the currently used settings module to each request,
    so it can be used in the templates like this `{{ SETTINGS_MODULE }}`.
    :param request:
    :return:
    """
    engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
    db_string = "PostgreSQL" if "postgresql" in engine else "SQLite" if "sqlite" in engine else "unknown"
    user_count = User.objects.count()
    user_string = str(user_count) + " User" + ("s" if user_count != 1 else "")

    data = {
        "SETTINGS_MODULE": settings.SETTINGS_MODULE,
        "DATABASE_ENGINE": db_string,
        "USER_COUNT": user_string,
        "RUNNING_EXPERIMENT_COUNT": Experiment.get_running_experiments().count(),
        "FINISHED_EXPERIMENT_COUNT": Experiment.objects.filter(
            finished_at__isnull=False
        ).count()
    }

    return data
