from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.reverse import reverse

from control_server.models import Messenger, Experiment
from control_server.time import now


class UserSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    experiments = serializers.HyperlinkedRelatedField(
        many=True, view_name="experiment-detail", read_only=True
    )
    fingerprints = serializers.HyperlinkedRelatedField(
        many=True, view_name="fingerprint-detail", read_only=True
    )

    class Meta:
        model = User
        ordering = [
            "-pk",
        ]
        fields = ["url", "username", "first_name", "last_name", "email", "experiments", "is_superuser", "is_staff",
                  "fingerprints"]


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        super(ChangePasswordSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        super(ChangePasswordSerializer, self).create(validated_data)

    @staticmethod
    def validate_new_password(value):
        validate_password(value)
        return value


class MessengerSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=64)
    experiments = serializers.HyperlinkedRelatedField(
        many=True, view_name="experiment-detail", read_only=True
    )
    code_name = serializers.ReadOnlyField()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if isinstance(self.instance, list):
            response["experiments"] = "[{}] Experiments".format(
                len(response["experiments"])
            )
            keys_to_remove = ["supports_attachments"]
            for key in keys_to_remove:
                if key in response:
                    response.pop(key)
        return response

    @staticmethod
    def validate_name(value):
        if len(Messenger.objects.filter(name__iexact="value").all()) > 0:
            raise serializers.ValidationError("A messenger with this name already exists.")
        return value

    class Meta:
        model = Messenger
        ordering = ["-pk"]
        fields = ["id", "url", "name", "experiments", "code_name"]


class PkToHyperlinkRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, view_name, **kwargs):
        super().__init__(**kwargs)
        self.view_name = view_name

    def to_representation(self, value):
        """
        This way, a HyperlinkedRelatedField can be created with only knowing the view name and pk of the object.
        :param value:
        :return:
        """
        return reverse(self.view_name, args=(value.pk,), request=self.context['request'])


class ExperimentListSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=1024)
    messenger = serializers.HyperlinkedRelatedField(many=False, view_name="messenger-detail", read_only=True)
    messenger_str = serializers.ReadOnlyField()

    honeypage = serializers.HyperlinkedRelatedField(many=False, view_name="honeypage-detail", read_only=True)
    honeymail = serializers.HyperlinkedRelatedField(many=False, view_name="honeymail-detail", read_only=True)

    # timestamps
    created_at = serializers.DateTimeField(read_only=True, default=serializers.CreateOnlyDefault(now))
    start_at = serializers.DateTimeField(read_only=True)
    finished_at = serializers.DateTimeField(read_only=True)

    creator = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Experiment
        ordering = [
            "-id",
        ]
        fields = [
            "url", "id", "name", "messenger", "messenger_str",
            "honeypage", "honeymail", "creator", "created_at", "start_at", "finished_at"
        ]


class ExperimentDetailSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=1024)

    messenger_id = serializers.ReadOnlyField()
    messenger = serializers.HyperlinkedRelatedField(many=False, view_name="messenger-detail", read_only=True)
    messenger_str = serializers.ReadOnlyField()

    honeypage = serializers.HyperlinkedRelatedField(many=False, view_name="honeypage-detail", read_only=True)
    honeymail = serializers.HyperlinkedRelatedField(many=False, view_name="honeymail-detail", read_only=True)

    honeypage_link = serializers.ReadOnlyField()
    honeymail_address = serializers.ReadOnlyField()

    with_honeypage = serializers.BooleanField(
        default=False, read_only=True, help_text="(attach Honeypage)"
    )

    with_suspicious_honeypage = serializers.BooleanField(
        default=False, read_only=True, help_text="(attach suspicious looking Honeypage)"
    )

    with_meta_tags_honeypage = serializers.BooleanField(
        default=False, read_only=True, help_text="(attach Honeypage with Meta Tags)"
    )

    with_honeymail = serializers.BooleanField(
        default=False, read_only=True, help_text="(attach Honeymail)"
    )

    creator = serializers.ReadOnlyField(source="creator.username")

    # timestamps
    created_at = serializers.DateTimeField(read_only=True, default=serializers.CreateOnlyDefault(now))
    start_at = serializers.DateTimeField(read_only=True)
    finished_at = serializers.DateTimeField(read_only=True)

    access_logs = serializers.HyperlinkedRelatedField(
        many=True, view_name="accesslog-detail", read_only=True
    )

    fingerprint_logs = serializers.HyperlinkedRelatedField(
        many=True, view_name="fingerprintlog-detail", read_only=True
    )

    browser_fingerprint_logs = serializers.HyperlinkedRelatedField(
        many=True, view_name="browserfingerprintlog-detail", read_only=True
    )

    def update(self, instance, validated_data):
        if (
            validated_data.with_honeypage
            or validated_data.with_honeymail
            or validated_data.with_suspicious_honeypage
            or validated_data.with_meta_tags_honeypage
        ):
            raise serializers.ValidationError("Cannot change honeydata for created experiments.")

        if instance.finished_at:
            raise serializers.ValidationError("Finished experiments can't be changed.")

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        response = super(ExperimentDetailSerializer, self).to_representation(instance)

        for field in ["messenger", "honeypage", "honeymail"]:
            # iterate all fields of this object and add the id of some related objects
            if hasattr(instance, field):
                value = getattr(instance, field)
                if value and hasattr(value, "pk"):
                    response.update({field + "_id": value.pk})

        response.update(
            {
                "messenger_name": instance.messenger.name,
                "with_honeymail": instance.with_honeymail,
                "with_honeypage": instance.with_honeypage,
                "with_suspicious_honeypage": instance.with_suspicious_honeypage,
                "with_meta_tags_honeypage": instance.with_meta_tags_honeypage,
            }
        )

        return response

    def validate(self, data):
        # object-level validation
        if not data.get("manual", False):
            # not manual
            messenger_obj = data.get("messenger")
            if messenger_obj.manual_only:
                raise serializers.ValidationError(
                    "Messenger {} only supports manual experiments.".format(
                        str(data.get("messenger").name)
                    )
                )

        return data

    class Meta:
        model = Experiment
        ordering = ["-pk"]
        fields = "__all__"


class ExperimentCreateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=1024)

    """
    hint: we are using a trick here to allow us to GET the Hyperlink of an object,
    e.g. https://.../messenger/1/; and POST only the pk (messenger_id=1).
    Therefore we need the HyperlinkedRelatedField read-only and an additional PrimaryKeyRelatedField with source.
    """
    messenger = serializers.HyperlinkedRelatedField(many=False, view_name="messenger-detail", read_only=True)
    messenger_id = serializers.PrimaryKeyRelatedField(source="messenger", queryset=Messenger.objects.all())
    messenger_str = serializers.ReadOnlyField()

    with_honeypage = serializers.BooleanField(
        default=False, write_only=True, help_text="(attach Honeypage)"
    )

    with_suspicious_honeypage = serializers.BooleanField(
        default=False, write_only=True, help_text="(attach suspicious looking Honeypage)"
    )

    with_meta_tags_honeypage = serializers.BooleanField(
        default=False, write_only=True, help_text="(attach Honeypage with Meta Tags)"
    )

    with_honeymail = serializers.BooleanField(
        default=False, write_only=True, help_text="(attach Honeymail)"
    )

    def validate(self, data):
        # object-level validation
        num_true = sum([
            data.get("with_honeypage", False),
            data.get("with_suspicious_honeypage", False),
            data.get("with_meta_tags_honeypage", False)
        ])
        is_max_one_honeypage_type = num_true <= 1

        if not is_max_one_honeypage_type:
            raise serializers.ValidationError(
                "Experiments can either have a honeypage, a suspicious honeypage, or a meta tags honeypage."
            )

        if not (
            data.get("with_honeypage", False)
            or data.get("with_suspicious_honeypage", False)
            or data.get("with_meta_tags_honeypage", False)
            or data.get("with_honeymail", False)
        ):
            raise serializers.ValidationError(
                "Experiments need at least one type of honeydata."
            )

        name = data.get("name", "")
        if not name:
            name = "REPLACE ME"
            data["name"] = name

        return data

    class Meta:
        model = Experiment
        ordering = ["-pk"]
        fields = [
            "url", "id", "name",
            "messenger", "messenger_id", "messenger_str",
            "with_honeypage", "with_suspicious_honeypage", "with_meta_tags_honeypage", "with_honeymail"
        ]
