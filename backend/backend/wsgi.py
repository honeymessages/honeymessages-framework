"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application

try:
    application = get_wsgi_application()
except Exception:
    traceback.print_exc()
    # Error loading applications
    if "mod_wsgi" in sys.modules:
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
