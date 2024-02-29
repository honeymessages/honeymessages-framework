import json
import os
from datetime import timedelta
from itertools import chain

from codename import codename
from django.db import models
from django.utils.functional import cached_property
from django.utils.timesince import timesince

from control_server.core import SERVER_ADDRESS, PROTOCOL


class AccessLog(models.Model):
    absolute_url = models.TextField(null=False, blank=True)

    http_host = models.CharField(max_length=512, null=False, blank=True)
    subdomain = models.CharField(max_length=64, null=False, blank=True, default="")
    path = models.CharField(max_length=128, null=False, blank=True)

    ip_address = models.CharField(max_length=45, null=False, blank=True)
    user = models.ForeignKey(
        "auth.User", on_delete=models.PROTECT, null=True, blank=True
    )

    referrer = models.CharField(max_length=512, null=True, blank=True)

    method = models.CharField(max_length=8, null=False, blank=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    content_params = models.TextField(null=True, blank=True)
    scheme = models.CharField(max_length=24, null=True, blank=True)

    headers = models.TextField(null=True, blank=True)
    get = models.TextField(null=True, blank=True)
    post = models.TextField(null=True, blank=True)
    cookies = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    meta = models.TextField(null=True, blank=True)
    files = models.TextField(null=True, blank=True)

    session_key = models.CharField(max_length=4096, null=False, blank=True)

    timestamp = models.DateTimeField(null=False, blank=True)
    location = models.TextField(verbose_name="GeoIP 2 Location", blank=True)

    request = models.TextField(verbose_name="Request", blank=True)
    response = models.TextField(verbose_name="Response", blank=True)

    @property
    def user_agent(self):
        try:
            obj = json.loads(self.headers)
            return obj.get("User-Agent", None)
        except Exception:
            print("Error parsing user agent for Access Log", self.id)
            return None

    @property
    def username(self):
        return self.user.username if self.user else None

    @cached_property
    def matching_honeypage(self):
        """
        Matching Honeypage (matched on subdomain).
        """
        return Honeypage.objects.filter(subdomain__iexact=self.subdomain).first()

    @cached_property
    def matching_honeypage_str(self):
        """
        String representation of matching Honeypage (matched on subdomain).
        """
        return "Honeypage #{}".format(self.matching_honeypage.pk) if self.matching_honeypage else None

    @cached_property
    def matching_experiment(self):
        """
        Matching experiment (based on Honeypage match).
        """
        return self.matching_honeypage.root.experiment if self.matching_honeypage else None

    @cached_property
    def matching_experiment_str(self):
        """
        String representation of matching Experiment.
        """
        return self.matching_experiment.name if self.matching_experiment else None

    @property
    def seconds_since_experiment(self):
        if self.matching_experiment:
            # get the most relevant timestamp from the experiment
            experiment_timestamp = self.matching_experiment.finished_at or self.matching_experiment.start_at or \
                                   self.matching_experiment.created_at
            return (self.timestamp - experiment_timestamp).total_seconds()

        return None

    @property
    def human_time_since_experiment(self):
        if self.matching_experiment:
            experiment_timestamp = self.matching_experiment.finished_at or self.matching_experiment.start_at or \
                                   self.matching_experiment.created_at
            return timesince(experiment_timestamp, self.timestamp)

        return ""

    @cached_property
    def matching_fingerprint_log(self):
        """
        FingerprintLogs belonging to this request.
        Only includes fingerprints received approximately at the same time as the request.
        """

        return FingerprintLog.objects.filter(
            visited_url__icontains=self.http_host,
            timestamp__gte=self.timestamp - timedelta(seconds=3),
            timestamp__lte=self.timestamp + timedelta(minutes=1),
        ).order_by('timestamp').first()

    @cached_property
    def matching_fingerprint(self):
        """
        Distinct fingerprints that were recorded for this AccessLog (based on matching_fingerprint_logs).
        """
        return self.matching_fingerprint_log.fingerprint

    @cached_property
    def matching_fingerprint_str(self):
        """
        String representation of FingerprintLogs belonging to this request.
        """
        # fingerprint.fingerprint is the "hash" value, e.g. hs8g3jsxGSDFf
        return self.matching_fingerprint.fingerprint

    @cached_property
    def matching_browser_fingerprint_log(self):
        """
        FingerprintLogs belonging to this request.
        Only includes fingerprints received in under 3 minutes after logging the request.
        """
        return BrowserFingerprintLog.objects.filter(
            visited_url__icontains=self.http_host,
            timestamp__gte=self.timestamp - timedelta(seconds=10),
            timestamp__lte=self.timestamp + timedelta(minutes=2),
        ).order_by('timestamp').first()

    @cached_property
    def matching_browser_fingerprint_log_str(self):
        """
        String representation of FingerprintLogs belonging to this request.
        """
        return self.matching_browser_fingerprint_log.feature_ua

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_access_logs"
        default_permissions = ["view"]
        verbose_name = "Access Log"
        ordering = [
            "-pk",
        ]


class Fingerprint(models.Model):
    fingerprint = models.CharField(unique=True, max_length=1024, null=False, blank=False)
    fp_js_version = models.CharField(max_length=45, null=False, blank=True, default="3.0.1")
    users = models.ManyToManyField("auth.User", related_name="fingerprints", blank=True)

    @property
    def users_str(self):
        return [user.username for user in self.users.all()]

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_fingerprints"
        default_permissions = ["view"]
        verbose_name = "Fingerprint"
        ordering = [
            "-pk",
        ]


class FingerprintLog(models.Model):
    visited_url = models.CharField(max_length=1024, null=False, blank=True)
    ip_address = models.CharField(max_length=45, null=False, blank=True)
    fingerprint = models.ForeignKey(
        "honeypot.Fingerprint",
        on_delete=models.PROTECT,
        related_name="fingerprint_logs",
        parent_link=True,  # ?
        blank=True,
        null=True,
    )
    components = models.CharField(max_length=60000, null=False, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=True)

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_fingerprint_logs"
        default_permissions = ["view"]
        verbose_name = "Fingerprint Log"
        ordering = [
            "-pk",
        ]


class BrowserFingerprintLog(models.Model):
    """
    Feature-based browser fingerprinting.
    """

    visited_url = models.CharField(max_length=1024, null=False, blank=False)
    ip_address = models.CharField(max_length=45, null=False, blank=True)
    feature_fp_version = models.CharField(max_length=45, null=False, blank=True, default="undefined")

    # e.g. 11110111101111...
    features = models.CharField(max_length=1024, null=False, blank=False)

    # Browser and version derived from features, e.g. chrome87, chrome88, chrome89, chrome90
    feature_ua = models.CharField(max_length=1024, null=False, blank=False)

    # e.g. {'mozilla_like': False, 'chrome_like': True, 'opera_like': False, ...}
    browser_like_data = models.CharField(max_length=1024, null=False, blank=False)

    # e.g. Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit [...]
    client_ua = models.CharField(max_length=512, null=False, blank=False)

    # Parsed client_ua, e.g. Chrome89
    parsed_ua = models.CharField(max_length=1024, null=False, blank=False)

    # e.g. 'Chrome PDF Plugin,Chrome PDF Viewer,Native Client'
    plugins = models.CharField(max_length=1024, null=False, blank=False)

    # additional data e.g. {'languages': 'de-DE,de,en-US,en', 'outer_res': '1792x934', 'inner_res': '1792x855'}
    client_data = models.CharField(max_length=1024, null=False, blank=False)

    timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=True)

    def __str__(self):
        return f"({self.id}) {self.ip_address} Parsed UA: {self.parsed_ua} / Feature UA: {self.feature_ua}"

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_browser_fingerprint_logs"
        default_permissions = ["view"]
        verbose_name = "Browser Fingerprint Log"
        ordering = [
            "-pk",
        ]


class HoneydataType(models.Model):
    honeydata_type = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.honeydata_type

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_honeydatatypes"
        default_permissions = ["view"]
        verbose_name = "HoneydataType"
        ordering = [
            "-pk",
        ]


class Honeypage(models.Model):
    subdomain = models.CharField(max_length=128, default="")
    path = models.CharField(max_length=128, default="", blank=True)
    protocol = models.CharField(max_length=5, default="http")
    pdf_payload = models.CharField(max_length=256, default="", blank=True)
    suspicious = models.BooleanField(default=False, blank=True)
    with_meta_tags = models.BooleanField(default=False, blank=True)

    parent = models.ForeignKey(
        "honeypot.Honeypage",
        on_delete=models.PROTECT,
        related_name="children",
        parent_link=True,
        blank=True,
        null=True,
    )

    def __iter__(self):
        """
        Implement the iterator protocol.
        Test with `print(list(iter(root_honeypage)))`
        :return:
        """
        for child in chain(*map(iter, list(self.children.all()))):
            yield child
        yield self

    @property
    def all_children_subdomains(self):
        paths = [self.subdomain]

        for child in self.children.all():
            paths += child.all_child_subdomains

        return paths

    @property
    def root(self):
        if not self.parent:
            return self
        else:
            return self.parent.root

    @property
    def experiment(self):
        return self.root.experiment

    @property
    def link(self):
        return "{}://{}.{}/{}".format(
            self.protocol, self.subdomain, SERVER_ADDRESS, self.path + "/" if self.path != "" else ""
        )

    @property
    def fingerprint_logs(self):
        """
        Returns all FingerprintLogs that match this HoneyPage's url.
        :return:
        """
        return FingerprintLog.objects.filter(visited_url=self.link.replace(":80", ""))

    @property
    def browser_fingerprint_logs(self):
        """
        Returns all FingerprintLogs that match this HoneyPage's url.
        :return:
        """
        return BrowserFingerprintLog.objects.filter(visited_url=self.link.replace(":80", ""))

    @property
    def access_logs(self):
        """
        Returns AccessLogs that match this HoneyPage's path and subdomain.
        :return:
        """
        return AccessLog.objects.filter(user__isnull=True, subdomain=self.subdomain)

    @staticmethod
    def generate_unique_pdf_payload():
        # get unique subdomain
        while True:
            subdomain_code = "pdf-{subdomain}-{subdomain_suffix}".format(
                subdomain=codename(separator="-"),
                subdomain_suffix=codename().split()[0]
            )
            if subdomain_code and Honeypage.objects.filter(pdf_payload__startswith=subdomain_code).count() == 0:
                break

        # make sure the whole payload is unique
        while True:
            pdf_payload = "{protocol}://{subdomain}.{domain}/".format(
                protocol=PROTOCOL,
                subdomain=subdomain_code,
                domain=SERVER_ADDRESS
            )

            if pdf_payload and Honeypage.objects.filter(pdf_payload=pdf_payload).count() == 0:
                break

        return pdf_payload

    @staticmethod
    def generate_unique_subdomain():
        unique_subdomain = codename(separator="-") + "-" + codename().split()[0]
        while Honeypage.objects.filter(subdomain__iexact=unique_subdomain).count() > 0:
            unique_subdomain = codename(separator="-") + "-" + codename().split()[0]
        return unique_subdomain

    @staticmethod
    def generate_honeypage(suspicious=False, with_meta_tags=False):
        """
        # create pdf
        pdf_name = Honeypage.generate_unique_pdf_name()
        pdf_path = os.path.join(STATIC_ROOT, "honeypage", pdf_name)
        pdf_payload = Honeypage.generate_unique_pdf_payload()

        # create instrumented PDF
        make_canary_pdf(pdf_payload, pdf_path)
        """

        honeypage = Honeypage(
            subdomain=Honeypage.generate_unique_subdomain(),
            path="",
            protocol=PROTOCOL,
            parent=None,
            pdf_payload=Honeypage.generate_unique_pdf_payload(),
            suspicious=suspicious,
            with_meta_tags=with_meta_tags
        )
        honeypage.save()
        return honeypage

    def attach_branches(self, n_layers=2, n_children_per_page=2):
        def build_tree(root, i=0):
            if i < n_layers:
                for _ in range(n_children_per_page):
                    node_honeypage = Honeypage(
                        subdomain=Honeypage.generate_unique_subdomain(),
                        path="",
                        protocol=root.protocol,
                        parent=root,
                        pdf_payload=Honeypage.generate_unique_pdf_payload(),
                    )
                    node_honeypage.save()
                    build_tree(node_honeypage, i + 1)

        build_tree(self)

    @staticmethod
    def generate_branched_honeypage(n_layers=3, n_children_per_page=2):
        honeypage = Honeypage.generate_honeypage()
        Honeypage.attach_branches(honeypage, n_layers, n_children_per_page)
        return honeypage

    @staticmethod
    def generate_suspicious_honeypage():
        return Honeypage.generate_honeypage(suspicious=True)

    @staticmethod
    def generate_meta_tags_honeypage():
        return Honeypage.generate_honeypage(with_meta_tags=True)

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_honeypages"
        default_permissions = ["view"]
        verbose_name = "Honeypage"
        ordering = [
            "-pk",
        ]

class Honeymail(models.Model):
    email_address = models.CharField(max_length=128, unique=True)

    @staticmethod
    def generate_honeymail(code_name=None):
        def get_codename():
            return codename(separator="-")

        code_name = code_name if code_name is not None else get_codename()

        def build_email_address():
            code = get_codename()
            return "{}+{}-{}@gmail.com".format(
                os.environ.get("BASE_HONEY_EMAIL_ADDRESS", "please-change-me"),
                code_name,
                code
            )

        # get unique email address
        email_address = build_email_address()
        while Honeymail.objects.filter(email_address=email_address).count() > 0:
            email_address = build_email_address()

        honeymail = Honeymail(email_address=email_address)
        honeymail.save()
        return honeymail

    class Meta:
        app_label = "honeypot"
        db_table = "honeypot_honeymails"
        default_permissions = ["view"]
        verbose_name = "Honeymail"
        ordering = ["-pk"]
