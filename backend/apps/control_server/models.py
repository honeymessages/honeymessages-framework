import os
import re
from collections import defaultdict
from datetime import timedelta

from django.db import models
from django.db.models import Q

from honeypot.models import (
    AccessLog,
    Honeypage,
    Honeymail,
    FingerprintLog, BrowserFingerprintLog
)

from .time import now
from geoip2.database import Reader as GeoIP2Reader

_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../run/geoip/')
geoip2_city_reader = GeoIP2Reader(os.path.join(_db_path, "GeoLite2-City.mmdb"))
geoip2_asn_reader = GeoIP2Reader(os.path.join(_db_path, "GeoLite2-ASN.mmdb"))

known_ips = {
    "senders": [
        r"127\.0\.0\.1",  # example
    ],
    "receivers": [
        r"127\.0\.0\.1",  # example
    ]
}

# Q filters to exclude client-side requests
# Create Q objects for each regular expression in the lists
_q_ip_sender_filter = [Q(ip_address__regex=regex) for regex in known_ips["senders"]]
_q_ip_receiver_filter = [Q(ip_address__regex=regex) for regex in known_ips["receivers"]]

# Combine the Q objects with OR for each list
_q_combined_sender_filter = Q()
for q_object in _q_ip_sender_filter:
    _q_combined_sender_filter |= q_object

_q_combined_receiver_filter = Q()
for q_object in _q_ip_receiver_filter:
    _q_combined_receiver_filter |= q_object

# Combine the Q objects with AND for the final query
# usage: logs.exclude(known_ip_q_filter)  # to exclude all client-side requests
known_ip_q_filter = _q_combined_sender_filter | _q_combined_receiver_filter


def matches_any_pattern(patterns, string):
    return any(re.search(pattern, string) for pattern in patterns)


class Messenger(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    supports_attachments = models.BooleanField(
        default=False, verbose_name="supports attachments"
    )
    code_name = models.CharField(max_length=128, blank=True, null=False, unique=True)
    manual_only = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def experiments(self):
        return Experiment.objects.filter(messenger_id=self.id)

    class Meta:
        app_label = "control_server"
        db_table = "control_server_messengers"
        verbose_name = "Messenger"
        ordering = ["-pk"]


class Experiment(models.Model):
    name = models.CharField(max_length=1024, blank=False)
    messenger = models.ForeignKey(
        Messenger,
        related_name="experiments",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    with_honeypage = models.BooleanField(default=False)
    with_suspicious_honeypage = models.BooleanField(default=False)  # honeypage shall look like (harmless) malware
    with_meta_tags_honeypage = models.BooleanField(default=False)  # honeypage shall look like (harmless) malware

    with_honeymail = models.BooleanField(default=False)

    honeypage = models.OneToOneField(
        Honeypage,
        related_name="experiment",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    honeymail = models.OneToOneField(
        Honeymail,
        related_name="experiment",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    # store the user who created this experiment
    creator = models.ForeignKey(
        "auth.User",
        related_name="experiments",
        on_delete=models.PROTECT,
        null=False,
        blank=True,
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    start_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    manual = models.BooleanField(default=True, blank=False)

    def __str__(self):
        return "{}{}{}{}{} ({})".format(
            "[HP] " if self.with_honeypage and not self.with_suspicious_honeypage and not self.with_meta_tags_honeypage else "",
            "[SusHP] " if self.with_suspicious_honeypage else "",
            "[MetaHP] " if self.with_meta_tags_honeypage else "",
            "[Mail] " if self.with_honeymail else "",
            self.messenger.name,
            self.id
        )

    @property
    def honeypage_link(self):
        return self.honeypage.link if self.honeypage else None

    @property
    def honeymail_address(self):
        return self.honeymail.email_address if self.honeymail else None

    @property
    def messenger_str(self):
        return self.messenger.name if self.messenger else None

    def is_valid(self):
        """Returns True if the experiment is fully configured."""
        if not self.messenger:
            return False

        # true if any honeydata is attached
        return self.honeypage or self.with_suspicious_honeypage or self.with_meta_tags_honeypage or self.honeymail

    def is_started(self) -> bool:
        return self.start_at is not None and self.start_at < now()

    def is_finished(self) -> bool:
        return self.finished_at is not None and self.finished_at < now()

    def reset(self):
        if self.is_finished():
            # don't touch finished experiments
            return

        # reset timestamps
        self.start_at = None
        self.finished_at = None
        self.save()

    @staticmethod
    def get_running_experiments():
        """ Returns all experiments that are already started. """
        return Experiment.objects.filter(start_at__lt=now(), finished_at=None).order_by(
            "-start_at"
        )

    @staticmethod
    def get_finished_experiments():
        """ Returns all experiments that are finished. """
        return Experiment.objects.filter(finished_at__lt=now()).order_by("-finished_at")

    @property
    def fingerprint_logs(self):
        """
        Returns the FingerprintLogs that match the ExperimentDetail's Honeypage and all children of that page.
        Returns an empty list of no Honeypage exists.
        :return: FilterSet or []
        """
        if self.honeypage:
            logs = self.honeypage.fingerprint_logs
            for page in list(iter(self.honeypage)):
                logs |= page.fingerprint_logs  # combine FilterSet

            return logs

        return FingerprintLog.objects.none()

    @property
    def browser_fingerprint_logs(self):
        """
        Returns the BrowserFingerprintLogs that match the ExperimentDetail's Honeypage and all children of that page.
        Returns an empty list of no Honeypage exists.
        :return: FilterSet or []
        """
        if self.honeypage:
            logs = self.honeypage.browser_fingerprint_logs
            for page in list(iter(self.honeypage)):
                logs |= page.browser_fingerprint_logs  # combine FilterSet

            return logs

        return BrowserFingerprintLog.objects.none()

    @property
    def access_logs(self):
        """
        Returns the AccessLogs that match the Experiment's Honeypage and all children of that page.
        Returns an empty list if no Honeypage exists.
        :return: FilterSet or []
        """
        if self.honeypage:
            logs = self.honeypage.access_logs
            for page in list(iter(self.honeypage)):
                logs |= page.access_logs  # combine FilterSet

            return logs
        return AccessLog.objects.none()

    def analyze(self, experiment_duration=None):
        """
        Can be used to evaluate an Experiment. Provide max_log_timestamp to reduce scope to a specific duration after
        the experiment.
        @param experiment_duration: allows passing a cut-off time
        @return:
        """
        log_blacklist = []  # to exclude test logs
        # all logs or filtered by time
        _logs = (self.access_logs.exclude(id__in=log_blacklist)
                 .filter(timestamp__lt=self.created_at + experiment_duration)) \
            if experiment_duration \
            else self.access_logs.exclude(id__in=log_blacklist)

        _ssrs = _logs.exclude(known_ip_q_filter)

        _not_our_logs = _logs.exclude(known_ip_q_filter)

        # collects the loaded resources (e.g. "/", "/favicon.ico")
        _resources_loaded = []
        for _log in _logs:
            _resource = _log.absolute_url.rstrip('/') if len(_log.absolute_url) > 1 else _log.absolute_url
            if _resource:
                _resources_loaded.append(_resource)
        _unique_resources_loaded = sorted(list(set(_resources_loaded)))

        _resources_loaded_by = defaultdict(list)
        for _log in _logs:
            _resource = _log.absolute_url.rstrip('/') if len(_log.absolute_url) > 1 else _log.absolute_url
            _requester = _log.ip_address
            _time = _log.timestamp
            if _resource:
                _resources_loaded_by[_resource].append([_requester, _time])

        # some evaluation flags
        _honeypage_requested = _logs.count() > 0
        _honeypages_crawled = len(_logs) > len(self.honeypage.access_logs)  # there are logs not belonging to the root
        _loaded_js = len([x for x in _resources_loaded if re.match(r".*\.js$", x)]) > 0

        # this is the one.gif file which embed.js injects
        _loaded_injected_gif = len([x for x in _resources_loaded if re.match(r".*\.gif$", x)]) > 0
        _sent_fingerprint = len([x for x in _resources_loaded if re.match(r".*browser_info$|.*fingerprint$", x)]) > 0
        _executed_js = _loaded_injected_gif | _sent_fingerprint

        _loaded_css = len([x for x in _resources_loaded if re.match(r".*\.css$", x)]) > 0
        _applied_css_background = len([x for x in _resources_loaded if re.match(r".*background\.png$", x)]) > 0

        # --- image resources ---
        _loaded_shortcut_icon = len([
            x for x in _resources_loaded if re.match(
                r".favicon\.ico$|.apple-touch-icon(?:-precomposed)?\.png$|.meta_tags\.png$",
                x
            )
        ]) > 0

        # <meta property="twitter:image">
        _loaded_meta_twitter_image = len([
            x for x in _resources_loaded if re.match(r".*meta_tags\.png$|.*twitter\.png$", x)
        ]) > 0

        # <meta property="og:image">
        _loaded_meta_og_image = len([x for x in _resources_loaded if re.match(r".*opengraph\.png$", x)]) > 0

        # --- pdf ---
        _loaded_pdf = len([x for x in _resources_loaded if re.match(r".*\.pdf$", x)]) > 0

        _loaded_logo_png = len([x for x in _resources_loaded if re.match(r".*logo\.png$", x)]) > 0

        # --- general stats ---
        _loaded_any_png = len([x for x in _resources_loaded if re.match(r".*\.png$", x)]) > 0

        ips = list(set(map(lambda x: x.ip_address, _logs)))

        def asn_from_ip(_ip_address):
            try:
                res = geoip2_asn_reader.asn(_ip_address)
                return f"{res.autonomous_system_number}/{res.autonomous_system_organization}"
            except:
                return ""

        def city_from_ip(_ip_address):
            try:
                _res = geoip2_city_reader.city(_ip_address)
                return f"{_res.country.iso_code}/{_res.country.name}" \
                       f"{('/' + _res.subdivisions.most_specific.name) if _res.subdivisions.most_specific.name else ''}"\
                       f"{('/' + _res.city.name) if _res.city.name else ''}"
            except:
                return ""

        ip_infos = [{"ip": ip, "location": city_from_ip(ip), "asn": asn_from_ip(ip)} for ip in ips]

        locations = list(set(
            filter(
                lambda x: x is not None,
                map(
                    lambda x: city_from_ip(x.ip_address) if (
                        not matches_any_pattern(known_ips["senders"] + known_ips["receivers"], x.ip_address)
                    ) else None,
                    _logs
                )
            )
        ))

        asns = list(set(map(lambda x: asn_from_ip(x.ip_address), _logs)))

        def has_duplicates(lst):
            return len(lst) != len(set(lst))

        def find_duplicates(lst):
            seen = set()
            duplicates = set()
            for item in lst:
                if item in seen:
                    duplicates.add(item)
                else:
                    seen.add(item)
            return list(duplicates)

        ssr_seconds_since_experiment = sorted(
            list(
                map(
                    lambda x: x.seconds_since_experiment,
                    filter(
                        lambda x: not matches_any_pattern(known_ips["senders"] + known_ips["receivers"], x.ip_address),
                        _logs
                    )
                )
            )
        )

        def check_time_difference(timestamps_list, threshold_s):
            for i in range(len(timestamps_list)):
                for j in range(i + 1, len(timestamps_list)):
                    time_delta = abs(timestamps_list[i] - timestamps_list[j])
                    if time_delta > timedelta(seconds=threshold_s):
                        return True
            return False

        repeated_access = False
        multiple_accesses_to_resource = has_duplicates(_resources_loaded)  # same resource was accessed multiple times

        if multiple_accesses_to_resource:
            _duplicate_res = find_duplicates(_resources_loaded)  # the resources that were accessed multiple times
            for res in _duplicate_res:
                accesses = _resources_loaded_by[res]
                _ips = [sublist[0] for sublist in accesses]
                if len(set(_ips)) > 1:
                    # repeated access
                    repeated_access = True
                    break
                else:
                    threshold = 1
                    seconds = [sublist[1] for sublist in accesses]
                    if check_time_difference(seconds, threshold):
                        # repeated access
                        repeated_access = True
                        break

        experiment_type = "honeypage" if self.with_honeypage \
            else "suspicious_honeypage" if self.with_suspicious_honeypage \
            else "meta_honeypage" if self.with_meta_tags_honeypage \
            else "honeymail" if self.with_honeymail else ""

        return {
            "experiment_id": self.id,
            "evaluation": {
                "experiment_id": self.id,
                "experiment_type": experiment_type,
                "honeypage_accessed": _honeypage_requested,
                "crawled": _honeypages_crawled,
                "repeated_access": repeated_access,
                "loaded_js": _loaded_js,
                "executed_js": _executed_js,

                "num_ssrs": _ssrs.count(),
                "num_unique_resources_loaded": len(_unique_resources_loaded),

                "ips": ips,
                "asns": asns,
                "ip_infos": ip_infos,
                "locations": locations,
                "ssr_seconds_since_experiment": ssr_seconds_since_experiment,
            }
        }

    class Meta:
        app_label = "control_server"
        db_table = "control_server_experiments"
        verbose_name = "Experiments"
        ordering = ["-pk"]
