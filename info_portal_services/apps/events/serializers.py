from rest_framework import serializers

from apps.tags.serializers import TagsSerializer
from apps.subjects.serializers import SubjectsSerializer
from apps.news.serializers import UserSerializer
from .models import Events, EventModeratorComments, EventFormats, EventTypes
from apps.status_model.models import StatusTypes


class EventFormatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventFormats
        fields = [
            "id",
            "event_format",
            "name"
        ]


class EventTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventTypes
        fields = [
            "id",
            "event_type",
            "name"
        ]


class EventsGetSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)
    event_format = EventFormatsSerializer(read_only=True)
    event_type = EventTypesSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Events
        fields = [
            "id",
            "title",
            "description",
            "short_description",
            "place",
            "date_start",
            "date_end",
            "email",
            "phone",
            "event_source",
            "organizer",
            "address",
            "image",
            "event_format",
            "event_type",
            "subject",
            "tags",
            "created_by",
        ]


class EventsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Events
        fields = [
            "id",
            "title",
            "description",
            "short_description",
            "place",
            "date_start",
            "date_end",
            "email",
            "phone",
            "event_source",
            "organizer",
            "address",
            "image",
            "event_format",
            "event_type",
            "subject",
            "tags",
            "created_by",
        ]
        extra_kwargs = {
            'event_format': {'required': True},
            'event_type': {'required': True},
        }

    def validate(self, attrs):
        attrs = super(EventsCreateSerializer, self).validate(attrs)
        if attrs.get("date_start") >= attrs.get("date_end"):
            raise serializers.ValidationError(f'Incorrect dates "date_start" >= "date_end"')
        return attrs

    def create(self, validated_data):
        validated_data["event_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["created_by"] = self.context['request'].user
        return super(EventsCreateSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # We change status "returned" to "created" after content-manager has updated his event
        # but not yet send it to review
        validated_data["event_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(EventsCreateSerializer, self).update(instance, validated_data)


class EventModeratorCommentsSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = EventModeratorComments
        fields = [
            "id",
            "comment",
            "created_by",
        ]


class EventInfoSerializer(serializers.ModelSerializer):
    event_comments = EventModeratorCommentsSerializer(
        many=True,
        read_only=True,
    )
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)
    event_format = EventFormatsSerializer(read_only=True)
    event_type = EventTypesSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Events
        fields = '__all__'


class EventsStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Events
        fields = []

    def update(self, instance, validated_data):
        # Contend-manager send event on review
        validated_data["event_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        return super(EventsStatusSerializer, self).update(instance, validated_data)


class EventsModerationSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True)

    class Meta:
        model = Events
        fields = [
            "id",
            "event_status",
            "comment",
        ]

    def validate_event_status(self, data):
        allowed_statuses = (
            "declined",
            "returned",
            "published",
        )
        if data.status not in allowed_statuses:
            raise serializers.ValidationError(f"Change event status to {data.status} is not allowed")
        return data

    def update(self, instance, validated_data):
        if validated_data.get("comment"):
            EventModeratorComments.objects.create(
                event=instance,
                comment=validated_data.get("comment"),
                created_by=self.context["request"].user,
            )
        validated_data["modified_by"] = self.context['request'].user
        return super(EventsModerationSerializer, self).update(instance, validated_data)


class EventsCommentSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(EventsCommentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["modified_by"] = self.context['request'].user
        return super(EventsCommentSerializer, self).update(instance, validated_data)

    class Meta:
        model = EventModeratorComments
        fields = [
            "id",
            "event",
            "comment",
        ]


class ArchiveEventSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = Events
        fields = [
            "action",
        ]

    def validate_action(self, data):
        allowed_actions = (
            "get_from",
            "put_in",
        )
        if data not in allowed_actions:
            raise serializers.ValidationError(f"Can't perform '{data}' action. Allowed actions are: "
                                              f"'{allowed_actions[0]}', '{allowed_actions[1]}'.")
        return data

    def update(self, instance, validated_data):
        if validated_data.get("action") == "get_from":
            validated_data["event_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        elif validated_data.get("action") == "put_in":
            validated_data["event_status"] = StatusTypes.objects.get_or_create(status="archived")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(ArchiveEventSerializer, self).update(instance, validated_data)
