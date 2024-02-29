import os
import re
from codename import codename
from django.conf import settings

PROTOCOL = settings.PROTOCOL

LOCAL_ADDRESS = "localtest.me:80"
LOCAL_ADDRESS_REGEX = r"(?:127.0.0.1|localhost|localtest)(?:\.me)?(?:\:[0-9]{2,4})?"

REMOTE_ADDRESS = os.environ.get("DOMAIN_NAME", "localtest.me")  # DOMAIN_NAME
REMOTE_ADDRESS_REGEX = REMOTE_ADDRESS

SERVER_ADDRESS = LOCAL_ADDRESS if settings.DEBUG else REMOTE_ADDRESS
SERVER_ADDRESS_REGEX = LOCAL_ADDRESS_REGEX if settings.DEBUG else REMOTE_ADDRESS_REGEX

HONEYPOT_URL = (
    (PROTOCOL + "://" + LOCAL_ADDRESS)
    if settings.DEBUG
    else (PROTOCOL + "://" + REMOTE_ADDRESS)
)

PATH_REGEX = re.compile(
    r"^https?://(?:{}|{})/(.*)$".format(REMOTE_ADDRESS, LOCAL_ADDRESS_REGEX), re.I
)

assert not SERVER_ADDRESS.endswith("/"), "SERVER_ADDRESS must not end with slash."


def get_codename(seed: str = None) -> str:
    return codename(id=seed, separator="-")


def extract_path(url: str) -> str:
    """
    Extracts the path from the url.
    :param url:
    :return: path: str
    """
    match = PATH_REGEX.match(url)
    if match and match.group(1):
        return match.group(1)
    else:
        return ""


def extract_ip_address(request) -> str:
    """
    Extracts the IP address of the sender from the request object.
    :param request: the WSGIRequest
    :return: str
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip_address = (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )

    # the institute uses a proxy that packs the actual IP into the X-REALIP header
    return request.headers.get("X-Real-IP", request.headers.get("X-Real-Ip", ip_address))
