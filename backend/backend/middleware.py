import json
import re
from json import JSONDecodeError
from os import environ

import chardet
from django.contrib.gis.geoip2 import GeoIP2
from django.http.request import HttpHeaders
from geoip2.errors import AddressNotFoundError

from control_server.core import extract_ip_address, SERVER_ADDRESS, SERVER_ADDRESS_REGEX
from control_server.time import now
from honeypot.models import AccessLog

geo_ip2 = GeoIP2()


class ContextMiddleware(object):
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    @staticmethod
    def absolute(request):
        urls = {
            "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
            "ABSOLUTE_ROOT_URL": request.build_absolute_uri("/").strip("/"),
        }

        return urls

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        my_request = request.GET.copy()

        for key, value in self.absolute(request).items():
            my_request[key] = value

        response = self.get_response(my_request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


def parse_http_headers(headers: HttpHeaders):
    headers_dict = {"HTTP_PREFIX": headers.HTTP_PREFIX}

    for key, value in headers._store.items():
        if isinstance(value, tuple):
            headers_dict[value[0]] = value[1]
        else:
            headers_dict[key] = str(value)

    return headers_dict


class AccessLogMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        # You can only read .body ONCE. This is enforced by Django.
        body = request.body

        response = self.get_response(request)

        # to reduce the amount of stored logs, do not log requests from authenticated users
        if request.user.is_authenticated:
            return response

        blacklist = ["password"]
        log = {}

        # create session if session key doesn't exist
        if not request.session.session_key:
            request.session.create()

        # ip address
        log["ip_address"] = extract_ip_address(request)

        log["path"] = str(request.path)
        log["method"] = str(request.method)
        log["referrer"] = str(request.META.get("HTTP_REFERER", ""))
        log["session_key"] = str(request.session.session_key)
        log["scheme"] = str(request.scheme)

        log["headers"] = json.dumps(parse_http_headers(request.headers))
        log["get"] = json.dumps(dict(request.GET.copy()))
        log["post"] = json.dumps({
            key: str(value) for (key, value) in request.POST.items() if key.lower() not in blacklist
        })

        meta = {
            key: str(value)
            for (key, value) in request.META.items()
            if (
                key.lower() not in blacklist
                and "wsgi" not in key[:4]
                and environ.get(key) != value
            )
        }
        log["meta"] = json.dumps(meta)

        # try to decode the body
        # we first try utf-8 and latin-1 and then guess with chardet
        try:
            log["body"] = json.dumps(body.decode("utf-8"))
        except UnicodeDecodeError:
            try:
                log["body"] = json.dumps(body.decode("latin-1"))
            except UnicodeDecodeError:
                guessed_encoding = chardet.detect(body)
                try:
                    log["body"] = json.dumps(body.decode(guessed_encoding))
                except UnicodeDecodeError:
                    log["body"] = body

        # content
        log["content_type"] = str(request.content_type)
        log["content_params"] = str(request.content_params)

        # cookies
        if request.COOKIES:
            cookies = {
                key: str(value)
                for (key, value) in request.COOKIES.items()
                if key.lower() not in blacklist
            }
            log["cookies"] = json.dumps(cookies)

        log["user"] = request.user if request.user.is_authenticated else None

        log["timestamp"] = str(now())

        log["absolute_url"] = str(request.build_absolute_uri()[:1024])

        http_host = request.META["HTTP_HOST"]
        log["http_host"] = str(http_host)

        subdomain = re.split(SERVER_ADDRESS_REGEX, http_host)[0].strip(".")
        log["subdomain"] = subdomain if subdomain != SERVER_ADDRESS else ""

        try:
            log["location"] = json.dumps(geo_ip2.city(log["ip_address"]))
        except AddressNotFoundError as e:
            # print("No location found for", log["ip_address"], e)
            pass

        response_dict = {}
        for attr in ["status_code", "reason_phrase", "status_text", "content_type", "charset"]:
            if hasattr(response, attr):
                response_dict[attr] = getattr(response, attr)

        if getattr(response, "status_code") > 200 and hasattr(response, "content"):
            response_dict["content"] = getattr(response, "content").decode('UTF-8')

        if hasattr(response, "cookies"):
            try:
                response_dict["cookies"] = json.dumps(response.cookies)
            except JSONDecodeError:
                pass

        log["response"] = json.dumps(response_dict)

        try:
            AccessLog(**log).save()
        except Exception as e:
            print(e)

        return response
