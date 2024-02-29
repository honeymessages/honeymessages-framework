#!/usr/bin/env python3
import os

import django

django.setup()

import gzip
import re
from datetime import datetime
import pytz

from honeypot.models import AccessLog, Honeypage

tz = pytz.timezone('UTC')

line_format = re.compile(
    r'(?P<ip>(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:::1)) - - '
    r'\[(?P<date>\d{2}/[a-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} '
    r'([+\-])\d{4})\] '
    r'((\"(?P<method>GET|POST) )(?P<path>.+) (http/[1-2]\.[0-9]")) '
    r'(?P<status_code>\d{3}) '
    r'(?P<bytes_sent>\d+) '
    r'(["](?P<referrer>(-)|(.+))["]) '
    r'(["](?P<useragent>.+)["])',
    re.IGNORECASE
)


def parse_access_logs(log_dir: str):
    files = []
    logs = []

    for file_path in os.listdir(log_dir):
        if file_path.startswith("access."):
            files.append(file_path)

            if file_path.endswith(".gz"):
                logfile = gzip.open(os.path.join(log_dir, file_path))
            else:
                logfile = open(os.path.join(log_dir, file_path))

            for line in logfile.readlines():

                if isinstance(line, bytes):
                    line = line.decode("utf-8")

                data = re.search(line_format, line)

                if data:
                    datadict = data.groupdict()
                    ip = datadict["ip"]
                    datetime_string = datadict["date"]
                    date = tz.normalize(
                        datetime.strptime(datetime_string, "%d/%b/%Y:%H:%M:%S %z")
                    ).astimezone(tz)
                    path = datadict["path"]
                    bytes_sent = datadict["bytes_sent"]
                    referrer = datadict["referrer"]
                    useragent = datadict["useragent"]
                    status = datadict["status_code"]
                    method = data.group(6)

                    logs.append((ip, date, path, bytes_sent, referrer, useragent, status, method))

            logfile.close()

    return logs, files


def print_logs(logs):
    for log in sorted(logs):
        print(log[7], log[2])


if __name__ == "__main__":
    input_dir = "/var/log/nginx/"

    # input_dir = "/tmp/nginx_logs/"  # <--

    nginx_logs, log_files = parse_access_logs(input_dir)

    print(len(log_files), "nginx log files were parsed", ", ".join(sorted(log_files)))
    print(len(nginx_logs), "nginx access logs were found")

    print("Checking all logs against the Django logs")

    unmatched_logs = []

    for nginx_log in nginx_logs:
        path = nginx_log[2]
        path_re = r"^/?%s/?" % path.strip("/")
        method = nginx_log[7]
        access_logs = AccessLog.objects.filter(path__iregex=path_re, method__iexact=method)

        if access_logs.count() <= 0:
            unmatched_logs.append(nginx_log)

    filtered_logs = set()
    if unmatched_logs and len(unmatched_logs) > 0:
        print(len(unmatched_logs), "logs did not match any AccessLogs from Django")

        path_pattern = re.compile(r"^/(?:api|admin|run|login|logout)", re.IGNORECASE)

        for log in unmatched_logs:
            method = log[7]
            path = log[2]

            # print(method, path)
            if not path_pattern.match(path):
                filtered_logs.add(log)

        print(len(filtered_logs), "logs filtered", path_pattern.pattern)

        # match with honeypages
        interesting_logs = set()
        honeypage_paths = [d.get("path").strip("/") for d in Honeypage.objects.values("path").order_by().distinct()]
        honeypage_path_pattern = re.compile(r"^/?(?:{})/?".format("|".join(honeypage_paths)))

        for log in filtered_logs:
            path = log[2]
            if honeypage_path_pattern.match(path):
                interesting_logs.add(log)

        print(len(interesting_logs), "logs for Honeypage paths were found")
        # print_logs(interesting_logs)
