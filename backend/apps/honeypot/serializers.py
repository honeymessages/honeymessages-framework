from rest_framework import serializers

from .models import AccessLog, Honeypage, Honeymail, HoneydataType, FingerprintLog, Fingerprint, \
    BrowserFingerprintLog


class AccessLogListSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    ip_address = serializers.ReadOnlyField()
    timestamp = serializers.DateTimeField()

    matching_experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )
    matching_honeypage = serializers.HyperlinkedRelatedField(
        view_name="honeypage-detail", many=False, read_only=True
    )
    matching_fingerprint = serializers.HyperlinkedRelatedField(
        view_name="fingerprint-detail", many=False, read_only=True
    )
    matching_browser_fingerprint_log = serializers.HyperlinkedRelatedField(
        view_name="browserfingerprintlog-detail", many=False, read_only=True
    )

    class Meta:
        model = AccessLog
        ordering = [
            "-id",
        ]
        fields = [
            "url", "id", "ip_address", "absolute_url", "method", "timestamp", "user", "username",
            "matching_experiment", "matching_honeypage",
            "matching_browser_fingerprint_log", "matching_fingerprint",
        ]


class AccessLogDetailSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    ip_address = serializers.ReadOnlyField()
    location = serializers.ReadOnlyField()

    username = serializers.ReadOnlyField()

    matching_fingerprint_log = serializers.HyperlinkedRelatedField(
        view_name="fingerprintlog-detail", many=False, read_only=True
    )

    matching_fingerprint = serializers.HyperlinkedRelatedField(
        view_name="fingerprint-detail", many=False, read_only=True
    )
    matching_fingerprint_str = serializers.ReadOnlyField()

    matching_experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )
    matching_experiment_str = serializers.ReadOnlyField()

    seconds_since_experiment = serializers.ReadOnlyField()
    human_time_since_experiment = serializers.ReadOnlyField()

    matching_honeypage = serializers.HyperlinkedRelatedField(
        view_name="honeypage-detail", many=False, read_only=True
    )
    matching_honeypage_str = serializers.ReadOnlyField()

    matching_browser_fingerprint_log = serializers.HyperlinkedRelatedField(
        view_name="fingerprintlog-detail", many=False, read_only=True
    )
    matching_browser_fingerprint_log_str = serializers.ReadOnlyField()

    class Meta:
        model = AccessLog
        ordering = [
            "-id",
        ]
        fields = "__all__"


class FingerprintSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    fingerprint = serializers.ReadOnlyField()

    users = serializers.HyperlinkedRelatedField(
        many=True, view_name="user-detail", read_only=True
    )
    users_str = serializers.ReadOnlyField()

    fingerprint_logs = serializers.HyperlinkedRelatedField(
        view_name="fingerprintlog-detail", many=True, read_only=True
    )

    def to_representation(self, instance):
        response = super(FingerprintSerializer, self).to_representation(instance)
        response["users_str"] = [user.username for user in instance.users.all()]

        return response

    class Meta:
        model = Fingerprint
        read_only_fields = ("users_str", "fingerprint", "components",)
        ordering = [
            "-id",
        ]
        fields = "__all__"


class FingerprintLogSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    # visited_url = serializers.ReadOnlyField()

    fingerprint = serializers.HyperlinkedRelatedField(view_name="fingerprint-detail", read_only=True)
    # fingerprint_id = serializers.PrimaryKeyRelatedField(source="fingerprint", queryset=Fingerprint.objects.all())

    def to_representation(self, instance):
        response = super(FingerprintLogSerializer, self).to_representation(instance)

        response["fingerprint_str"] = instance.fingerprint.fingerprint
        return response

    class Meta:
        model = FingerprintLog
        read_only_fields = ("visited_url", "ip_address", "timestamp",)
        ordering = [
            "-id",
        ]
        fields = "__all__"


class BrowserFingerprintLogSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = BrowserFingerprintLog
        read_only_fields = (
            "visited_url", "features", "browser_like_data", "client_ua", "plugins", "client_data", "timestamp",
            "ip_address"
        )
        ordering = [
            "-id",
        ]
        fields = "__all__"


class HoneydataTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    honeydata_type = serializers.CharField()
    experiments = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=True, read_only=True
    )

    class Meta:
        model = HoneydataType
        ordering = [
            "-pk",
        ]
        fields = "__all__"


class HoneypageDetailSerializer(serializers.HyperlinkedModelSerializer):
    children = serializers.HyperlinkedRelatedField(
        many=True, view_name="honeypage-detail", read_only=True
    )

    link = serializers.CharField(max_length=256)

    """
    _experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )
    """

    suspicious = serializers.BooleanField(read_only=True)

    experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )

    root = serializers.HyperlinkedRelatedField(
        view_name="honeypage-detail", many=False, read_only=True
    )

    fingerprint_logs = serializers.HyperlinkedRelatedField(
        view_name="fingerprintlog-detail", many=True, read_only=True
    )

    browser_fingerprint_logs = serializers.HyperlinkedRelatedField(
        view_name="browserfingerprintlog-detail", many=True, read_only=True
    )

    access_logs = serializers.HyperlinkedRelatedField(
        view_name="accesslog-detail", many=True, read_only=True
    )

    class Meta:
        model = Honeypage
        ordering = [
            "-pk",
        ]
        fields = [
            "id", "link", "pdf_payload", "suspicious",
            "experiment", "protocol", "subdomain", "path",
            "root", "parent", "children",
            "fingerprint_logs", "browser_fingerprint_logs", "access_logs"
        ]


class HoneypageListSerializer(serializers.HyperlinkedModelSerializer):
    children = serializers.HyperlinkedRelatedField(
        many=True, view_name="honeypage-detail", read_only=True
    )

    experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )

    root = serializers.HyperlinkedRelatedField(
        view_name="honeypage-detail", many=False, read_only=True
    )

    class Meta:
        model = Honeypage
        ordering = [
            "-pk",
        ]
        fields = [
            "id", "url", "root", "subdomain", "parent", "children", "experiment"
        ]


class HoneymailSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    experiment = serializers.HyperlinkedRelatedField(
        view_name="experiment-detail", many=False, read_only=True
    )

    class Meta:
        model = Honeymail
        ordering = [
            "-pk",
        ]
        fields = "__all__"
