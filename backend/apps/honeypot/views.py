import json
import os.path
import re
import sys
import traceback
from collections import defaultdict

import django_filters
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from ua_parser import user_agent_parser

import honeypot.pdf.make_pdf_phone_home as make_pdf_phone_home
from control_server.core import SERVER_ADDRESS_REGEX, extract_ip_address
from .models import (
    Honeypage,
    Honeymail,
    HoneydataType,
    AccessLog,
    FingerprintLog,
    Fingerprint,
    BrowserFingerprintLog
)
from .serializers import (
    HoneypageDetailSerializer,
    HoneymailSerializer,
    HoneydataTypeSerializer,
    AccessLogListSerializer,
    FingerprintLogSerializer,
    FingerprintSerializer,
    BrowserFingerprintLogSerializer,
    AccessLogDetailSerializer,
    HoneypageListSerializer
)

geo_ip2 = GeoIP2()

MIME_TYPES = {
    "css": "text/css",
    "js": "text/javascript",
    "umd.min.js": "text/javascript",
    "png": "image/png",
    "ico": "image/x-icon",
    "pdf": "application/pdf",
    "gif": "image/gif",
    "php": "application/x-httpd-php",
    "com": "application/x-msdos-program",  # for eicar file
    "zip": "application/zip",  # for 42.zip
    "exe": "application/x-msdownload"
}

feature_scope_path = os.path.join(
    settings.DJANGO_ROOT, "run", "fingerprinting", "features-in-scope.txt"
)
browser_feature_map_path = os.path.join(
    settings.DJANGO_ROOT, "run", "fingerprinting", "feature_map.json"
)

# pattern for the real ip header
REAL_IP_PATTERN = re.compile(r"'X-Real-Ip': '([.0-9]+)'")

# Required for browser fingerprinting
browser_feature_map = {}
feature_scope = []
browsers = []


def init():
    global feature_scope
    global browser_feature_map
    global browsers

    if not len(feature_scope) > 0:
        # init feature list
        if not os.path.isfile(feature_scope_path):
            raise IOError('File "features-in-scope.txt" does not exist. Read fingerprinting Readme')
        with open(feature_scope_path, "r") as file:
            content = file.readlines()
        feature_scope = [x.strip() for x in content]

    if not (isinstance(browser_feature_map, dict) and len(browser_feature_map.keys()) > 0):
        # init browser_feature_map
        if not os.path.isfile(browser_feature_map_path):
            raise IOError('File "feature_map.json" does not exist. Run init_fingerprinting script first.')
        with open(browser_feature_map_path, "r") as map_file:
            map_content = map_file.read()
        try:
            json_content = json.loads(map_content)  # [ [ "browser1", [ "feature1", ... ] ], ...]
            for browser_data in json_content:  # [ "browser1", [ "feature1", ... ] ]
                browser = browser_data[0]
                feature_list = browser_data[1]
                browser_feature_map[browser] = feature_list
            browsers = browser_feature_map.keys()
        except Exception:
            raise IOError('Unable to parse "feature_map.json".')


# call init
init()


def default_view(request, args=None):
    return render(request, "apps/honeypot/honeypage.html", {"request": request})


def extract_subdomain_and_path_from_request(url):
    pattern = re.compile(
        r"^https?://(?P<subdomain>[\w-]+).{server_address}/(?P<path>[\w/-]+)?/?$".format(
            server_address=SERVER_ADDRESS_REGEX
        ),
        re.IGNORECASE
    )
    match = pattern.search(url)
    group_dict = match.groupdict() if match else defaultdict()

    subdomain = group_dict.get("subdomain")

    path = group_dict.get("path")
    if isinstance(path, str):
        path = path.strip("/")

    return subdomain, path


class CSRFExemptMixin(ContextMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class HoneyPageView(CSRFExemptMixin, TemplateView):
    template_name = "apps/honeypot/linked_honeypage.html"
    @property
    def name(self):
        return "HoneyPage"

    def get(self, request, slug=None, *args, **kwargs):
        honeypage: Honeypage | None = None
        subdomain, path = extract_subdomain_and_path_from_request(request.build_absolute_uri())

        if subdomain or path:
            if not path:
                honeypage: Honeypage = Honeypage.objects.filter(
                    subdomain__iexact=subdomain
                ).first()
            else:
                honeypage: Honeypage = Honeypage.objects.filter(
                    subdomain__iexact=subdomain,
                    path__iregex=r"{}/?".format(path)
                ).first()

        parent = None
        children = []
        if honeypage:
            children = honeypage.children.all()
            parent = honeypage.parent

        return render(
            request,
            "apps/honeypot/linked_honeypage.html",
            {
                "title": (subdomain or "") + (("/" + path) if path else ""),
                "request": request,
                "children": children,
                "parent": parent,
                "registered": honeypage is not None,
                "suspicious": honeypage is not None and honeypage.suspicious,
                "meta_tags": honeypage is not None and honeypage.with_meta_tags
            },
        )


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def resource_view(request, resource_name=None, file_ending=None, *args, **kwargs):
    # check resource type
    mime_type = MIME_TYPES.get(file_ending)

    if mime_type == MIME_TYPES.get("pdf"):
        file_name = resource_name + "." + file_ending
        if file_name == "generate.pdf":
            # get honeypage by subdomain and path (standard use case)
            url = request.build_absolute_uri().rstrip("/").rstrip(file_name)
            subdomain, path = extract_subdomain_and_path_from_request(url)
            honeypage = Honeypage.objects.filter(subdomain__iexact=subdomain, path__iregex=r"%s/?" % path).first()

            # get pdf payload from that honeypage and generate the pdf
            if honeypage and honeypage.pdf_payload and len(honeypage.pdf_payload) > 0:
                payload_url = honeypage.pdf_payload
                return HttpResponse(
                    make_pdf_phone_home.generate_pdf(payload_url, payload_url).encode("utf-8"),
                    content_type=mime_type,
                    status=200
                )
            else:
                # no honeypage, so return an empty pdf
                return HttpResponse(
                    make_pdf_phone_home.generate_pdf(content="Seems quite empty here...").encode("utf-8"),
                    content_type=mime_type,
                    status=200
                )
                pass

    # fetch js scripts
    if mime_type == MIME_TYPES.get("js"):
        file_path = "run/static/scripts/{}.{}".format(resource_name.replace("/", ""), file_ending)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    return HttpResponse(f.read(), content_type=mime_type, status=200)
            except IOError:
                pass

    # try to fetch honeypage files by name
    file_path = "run/static/honeypage/{}.{}".format(resource_name.replace("/", ""), file_ending)
    if mime_type and os.path.isfile(file_path):
        try:
            with open(file_path, "rb") as f:
                return HttpResponse(f.read(), content_type=mime_type, status=200)
        except IOError:
            pass

    # unsupported type or resource does not exist
    print(
        "{}.{} was requested, but can't be served.".format(
            resource_name, file_ending
        )
    )

    response = render(request, "404.html", {})
    response.status_code = 404

    return response  # HttpResponse("", content_type=mime_type, status=404)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def browser_info(request):
    """ API Endpoint for receiving browser fingerprints from Honeypages """
    data_dict = {}

    if request.user and (request.user.is_authenticated or not request.user.is_anonymous):
        # we have a known user, so we skip
        print("Browser fingerprinting skipped for known user " + request.user.username)
        return HttpResponse("///Browser fingerprinting skipped for known user", 200)

    ip_address = extract_ip_address(request)

    try:
        body = request.body.decode("utf-8")
        data_list = json.loads(body)

        for element in data_list:
            parsed_value = element[1]
            if len(parsed_value) == 1:
                # parse "1" and "0" to True or False respectively
                if parsed_value == "1":
                    parsed_value = True
                elif parsed_value == "0":
                    parsed_value = False
            data_dict.update({element[0]: parsed_value})
    except json.decoder.JSONDecodeError:
        traceback.print_exc(limit=1, file=sys.stdout)

    # handle the received data
    try:
        url = data_dict.get(
            "visited_url", ""
        )  # this is the Honeypage URL

        feature_fp_version = data_dict.get("feature_fp_version")

        ua = data_dict["client_ua"]
        parsed_ua = _parse_ua(ua)
        feature_ua = ", ".join(_parse_features(data_dict)["result"])

        print('Received browser fingerprint for {}: "{}", seems like "{}"'.format(
            url, parsed_ua, feature_ua
        ))

        browser_like_data = {
            "chrome": bool(data_dict["chrome"]),
            "opera": bool(data_dict["opera"]),
            "netscape": bool(data_dict["netscape"]),
            "safari": bool(data_dict["safari"]),
            "old_ie": bool(data_dict["old_ie"]),
            "ie_like": bool(data_dict["ie_like"]),
            "safari_like": bool(data_dict["safari_like"]),
            "mozilla_like": bool(data_dict["mozilla_like"]),
            "chrome_like": bool(data_dict["chrome_like"]),
            "opera_like": bool(data_dict["opera_like"]),
            "edge_like": bool(data_dict["edge_like"]),
            "webdriver": bool(data_dict["webdriver"]),
            "automation": bool(data_dict["automation"]),
            "phantom": bool(data_dict["phantom"]),
            "nightmare": bool(data_dict["nightmare"]),
            "awesomium": bool(data_dict["awesomium"]),
            "es5": bool(data_dict["es5"]),
            "es6": bool(data_dict["es6"]),
            "es7": bool(data_dict["es7"]),
            "es8": bool(data_dict["es8"]),
            "es9": bool(data_dict["es9"]),
            "es10": bool(data_dict["es10"])
        }

        client_data = {
            "vendor": data_dict["vendor"],
            "languages": data_dict["languages"],
            "outer_res": data_dict["outer_res"],
            "inner_res": data_dict["inner_res"],
        }

        BrowserFingerprintLog(
            visited_url=url,
            feature_fp_version=feature_fp_version,
            features=data_dict["features"],
            client_ua=ua,
            parsed_ua=parsed_ua,
            feature_ua=feature_ua,
            client_data=client_data,
            browser_like_data=browser_like_data,
            plugins=data_dict["plugins"],
            ip_address=ip_address
        ).save()
    except Exception:
        traceback.print_exc(limit=1, file=sys.stdout)

    return HttpResponse("///Browser info received", 200)


def _is_like_browser(data, browser):
    return (
        (
            not data["chrome"] and not data["chrome_like"] and not data["edge_like"] and not data["old_ie"]
            and not data["ie_like"] and not data["mozilla_like"] and not data["netscape"] and not data["opera"]
            and not data["opera_like"] and not data["safari"] and not data["safari_like"]
        )
        or (
            browser.startswith("chrome") and (data["chrome"] or data["chrome_like"] or data["phantom"])
            and not data["edge_like"]
        )
        or (browser.startswith("edge") and data["edge_like"])
        or (browser.startswith("firefox") and (data["netscape"] or data["mozilla_like"]) and not data["ie_like"])
        or (browser.startswith("ie") and (data["old_ie"] or data["ie_like"]))
        or (browser.startswith("opera") and (data["opera"] or data["opera_like"]))
        or (browser.startswith("safari") and (data["safari"] or data["safari_like"]))
    )


def _parse_features(data):
    features = data["features"]
    if len(features) != len(feature_scope):
        print("Unexpected browser fingerprint length")
        return {"max": 0, "result": ["unknown"]}

    # check client features with features of browser versions
    matches = {}
    for feature_idx, feature in enumerate(features):
        for browser in browsers:
            if not _is_like_browser(data, browser):
                # For example skip Chrome and Firefox if edge_like
                continue

            client_has_feature = feature == "1"
            browser_has_feature = feature_scope[feature_idx] in browser_feature_map[browser]

            if not (client_has_feature ^ browser_has_feature):  # XNOR
                matches[browser] = matches[browser] + 1 if browser in matches else 1

    max_score = 0
    result = []
    for browser in matches.keys():
        score = matches[browser]
        if score > max_score:
            max_score = score
            result = [browser]
        elif score == max_score:
            result.append(browser)

    return {"max": max_score, "result": result}


def _parse_ua(ua_str):
    # uses ua parser to retrieve Browser and Major version from the UA string
    parsed = user_agent_parser.Parse(ua_str)
    name = parsed["user_agent"]["family"]
    major = parsed["user_agent"]["major"]

    if not name or not major:
        return None

    return name + major


@csrf_exempt
@require_http_methods(["GET", "POST"])
def fingerprint(request):
    """ API Endpoint for receiving client fingerprints from Honeypages """
    # uses free version of FingerprintJS2 with limited accuracy

    data_dict = {}
    ip_address = extract_ip_address(request)

    try:
        body = request.body.decode("utf-8")
        data_list = json.loads(body)

        for element in data_list:
            for key in element.keys():
                data_dict.update({key: element[key]})
    except json.decoder.JSONDecodeError:
        traceback.print_exc(limit=1, file=sys.stdout)

    try:
        url = data_dict.get("visited_url", "")  # this is my custom Header with the Honeypage URL
        fingerprint_str = data_dict["visitor_id"]
        fingerprint_obj = Fingerprint.objects.filter(fingerprint=fingerprint_str).first()

        if not fingerprint_obj:
            # create new Fingerprint
            fingerprint_obj = Fingerprint(
                fingerprint=fingerprint_str,
                fp_js_version=data_dict["fingerprintjs_version"]
            )
            fingerprint_obj.save()

        if request.user and (request.user.is_authenticated or not request.user.is_anonymous):
            # we have a known user; add the fingerprint
            # if request.user not in fingerprint_obj.users.all():
            fingerprint_obj.users.add(request.user)
            fingerprint_obj.save()
            print("Received FingerprintJS {} for user {}".format(fingerprint_str, request.user.username))

        # save Fingerprint Log
        FingerprintLog(
            visited_url=url,
            fingerprint=fingerprint_obj,
            components=json.dumps(data_dict["components"]),
            ip_address=ip_address
        ).save()
    except Exception as e:
        traceback.print_exc()

    return HttpResponse("///Fingerprint received", 200)


class AccessLogFilter(filters.FilterSet):
    # absolute_url = django_filters.CharFilter(lookup_expr='icontains')
    # path = django_filters.CharFilter(lookup_expr='icontains')
    # http_host = django_filters.CharFilter(lookup_expr='icontains')
    # subdomain = django_filters.CharFilter(lookup_expr='icontains')
    # id = django_filters.NumberFilter()
    # id__lte = django_filters.NumberFilter()
    id__gt = django_filters.NumberFilter(field_name="id", lookup_expr="gt")
    id__lte = django_filters.NumberFilter(field_name="id", lookup_expr="lte")

    class Meta:
        model = AccessLog
        fields = []


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogListSerializer

    pagination_class = LargeResultsSetPagination
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AccessLogFilter
    filterset_fields = ("id",)
    ordering_fields = ["id"]

    def get_serializer_class(self):
        # detail view is requested via "?detail"
        if self.action == 'retrieve' or "detail" in self.request.query_params.keys():
            return AccessLogDetailSerializer
        elif self.action == 'list':
            return AccessLogListSerializer

        # default
        return AccessLogListSerializer

    @action(detail=True)
    def similar(self, request, pk=None):
        """
        API endpoint to list all `AccessLogs` that come from the same ip.
        """
        log = AccessLog.objects.filter(pk=pk).first()
        similar_logs = self.filter_queryset(AccessLog.objects.filter(ip_address=log.ip_address))

        page = self.paginate_queryset(similar_logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(similar_logs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def unauthenticated(self, request):
        """
        API endpoint to list all `AccessLogs` with no authenticated user.
        """
        logs = self.filter_queryset((AccessLog.objects.filter(user__isnull=True)))
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def authenticated(self, request):
        """
        API endpoint to list all `AccessLogs` from an authenticated user.
        """
        logs = self.filter_queryset(AccessLog.objects.filter(user__isnull=False))
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def foreign(self, request):
        """
        API endpoint to list all `AccessLogs` where the IP address is not in [`127.0.0.1`, `10.40.191.254`].
        """
        logs = self.filter_queryset(AccessLog.objects.exclude(ip_address__in=["127.0.0.1", "10.40.191.254"]))
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def interesting(self, request):
        """
        API endpoint to list all `AccessLogs` where the request is unauthenticated.
        """

        ip_address_filter = [
            "93.208.215.241",  # Lennard Heyn and his fingerprinting
        ]
        path_regex = r"^/[api|api-login|admin|logout|login|fingerprint]/?.*$"
        queryset = self.filter_queryset(
            AccessLog.objects.filter(user__isnull=True).exclude(
                path__iregex=path_regex
            ).exclude(
                ip_address__in=ip_address_filter
            )
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FingerprintFilter(filters.FilterSet):
    id__gt = django_filters.NumberFilter(field_name="id", lookup_expr="gt")
    id__lte = django_filters.NumberFilter(field_name="id", lookup_expr="lte")

    class Meta:
        model = Fingerprint
        fields = []


class FingerprintViewSet(viewsets.ModelViewSet):
    queryset = Fingerprint.objects.all()
    serializer_class = FingerprintSerializer
    pagination_class = LargeResultsSetPagination
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FingerprintFilter
    filterset_fields = ("id",)
    ordering_fields = ["id"]

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )


class FingerprintLogFilter(filters.FilterSet):
    id__gt = django_filters.NumberFilter(field_name="id", lookup_expr="gt")
    id__lte = django_filters.NumberFilter(field_name="id", lookup_expr="lte")

    class Meta:
        model = FingerprintLog
        fields = []


class FingerprintLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FingerprintLog.objects.all()
    serializer_class = FingerprintLogSerializer
    pagination_class = LargeResultsSetPagination
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FingerprintLogFilter
    filterset_fields = ("id",)
    ordering_fields = ["id"]

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )


class BrowserFingerprintLogFilter(filters.FilterSet):
    id__gt = django_filters.NumberFilter(field_name="id", lookup_expr="gt")
    id__lte = django_filters.NumberFilter(field_name="id", lookup_expr="lte")

    class Meta:
        model = BrowserFingerprintLog
        fields = []


class BrowserFingerprintLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BrowserFingerprintLog.objects.all()
    serializer_class = BrowserFingerprintLogSerializer
    pagination_class = LargeResultsSetPagination
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BrowserFingerprintLogFilter
    filterset_fields = ("id",)
    ordering_fields = ["id"]

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )


class HoneydataTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows exchanges to be viewed or edited. """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    queryset = HoneydataType.objects.all()
    serializer_class = HoneydataTypeSerializer


class HoneypageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Honeypage.objects.all()
    serializer_class = HoneypageDetailSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )

    def get_serializer_class(self):
        if self.action == 'retrieve' or "detail" in self.request.query_params.keys():
            return HoneypageDetailSerializer
        elif self.action == 'list':
            return HoneypageListSerializer
        return HoneypageListSerializer

    @action(detail=False)
    def root_honeypages(self, request):
        """
        API endpoint to list all `Honeypages` without a parent.
        """
        serializer = HoneypageListSerializer(
            Honeypage.objects.filter(parent=None), many=True, context={"request": request}
        )
        return Response(serializer.data)

    # *** API Endpoints regarding FingerprintLogs ***
    @action(detail=True)
    def get_fingerprint_logs(self, request, pk=None):
        """
        API endpoint to list all FingerprintLog instances where the visited_url matches this Honeypage.
        """
        return self._craft_paginated_fingerprint_log_response(
            Honeypage.objects.filter(pk=pk).first().fingerprint_logs, request
        )

    @action(detail=True)
    def get_browser_fingerprint_logs(self, request, pk=None):
        """
        API endpoint to list all FingerprintLog instances where the visited_url matches this Honeypage.
        """
        return self._craft_paginated_browser_fingerprint_log_response(
            Honeypage.objects.filter(pk=pk).first().browser_fingerprint_logs, request
        )

    def _craft_paginated_fingerprint_log_response(self, queryset, request):
        context = {"request": request}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FingerprintLogSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = FingerprintLogSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def _craft_paginated_browser_fingerprint_log_response(self, queryset, request):
        context = {"request": request}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BrowserFingerprintLogSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = BrowserFingerprintLogSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    # *** API Endpoints regarding AccessLogs ***
    @action(detail=True)
    def get_access_logs(self, request, pk=None):
        """
        Lists all AccessLog instances where subdomain and path match this HoneyPage.
        Excludes logs from authenticated users.
        """
        return self._craft_paginated_access_log_response(
            Honeypage.objects.filter(pk=pk).first().access_logs, request
        )

    @action(detail=True)
    def get_access_logs_authenticated(self, request, pk=None):
        """
        API endpoint to list all AccessLog instances for this experiment from authenticated users.
        """
        return self._craft_paginated_access_log_response(
            Honeypage.objects.filter(pk=pk).first().access_logs_authenticated, request
        )

    def _craft_paginated_access_log_response(self, queryset, request):
        context = {"request": request}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AccessLogListSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = AccessLogListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)


class HoneymailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Honeymail.objects.all()
    serializer_class = HoneymailSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )
