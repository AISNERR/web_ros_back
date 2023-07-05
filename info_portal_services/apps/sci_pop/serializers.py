from rest_framework import serializers

from .models import SciPop, Authors, PopFormat, SciPopModeratorComments
from apps.tags.serializers import TagsSerializer
from apps.subjects.serializers import SubjectsSerializer
from apps.news.serializers import UserSerializer
from ..status_model.models import StatusTypes


class SciPopAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Authors
        fields = [
            'id',
            'full_name'
        ]


class SciPopFormatSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopFormat
        fields = [
            'id',
            'title'
        ]


class SciPopModeratorCommentsSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = SciPopModeratorComments
        fields = [
            "id",
            "comment",
            "created_by",
        ]


class SciPopGetSerializer(serializers.ModelSerializer):
    sci_pop_comments = SciPopModeratorCommentsSerializer(
        many=True,
        read_only=True,
    )
    authors = SciPopAuthorSerializer(read_only=True, many=True)
    format = SciPopFormatSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    subject = SubjectsSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)

    class Meta:
        model = SciPop
        fields = '__all__'


class SciPopCreateSerializer(serializers.ModelSerializer):
    authors = SciPopAuthorSerializer(
        required=False,
        allow_null=True,
        read_only=True,
        many=True
    )
    tags = TagsSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = SciPop
        fields = [
            "id",
            "title",
            'format',
            'published_at',
            "material_date",
            'authors',
            'description',
            'video',
            'subject',
            'tags',
            "created_by",
            'created_at'
        ]
        extra_kwargs = {
            'format': {'required': True},
            'created_at': {'read_only': True},
            'published_at': {'read_only': True}
        }

    def create(self, validated_data):
        if 'authors' in validated_data:
            authors = validated_data.pop('authors')
            authors_ids = []
            for name in authors:
                name = name.strip()
                author = Authors.objects.get_or_create(full_name=name)[0]
                authors_ids.append(author)
            validated_data["authors"] = authors_ids
        validated_data["sci_pop_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        return super(SciPopCreateSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'authors' in validated_data:
            authors = validated_data.pop('authors')
            authors_ids = []
            for name in authors:
                name = name.strip()
                author = Authors.objects.get_or_create(full_name=name)[0]
                authors_ids.append(author)
            validated_data["authors"] = authors_ids
        validated_data["sci_pop_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPopCreateSerializer, self).update(instance, validated_data)


class SciPopStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = SciPop
        fields = []

    def update(self, instance, validated_data):
        validated_data["sci_pop_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        return super(SciPopStatusSerializer, self).update(instance, validated_data)


class SciPopModerationSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True)

    class Meta:
        model = SciPop
        fields = [
            "id",
            "sci_pop_status",
            "comment",
            "published_at"
        ]
        extra_kwargs = {
            'published_at': {'read_only': True}
        }

    def validate_sci_pop_status(self, data):
        allowed_statuses = (
            "declined",
            "returned",
            "published",
        )
        if data.status not in allowed_statuses:
            raise serializers.ValidationError(f"Change SciPop status to {data.status} is not allowed")
        return data

    def update(self, instance, validated_data):
        if validated_data.get("comment"):
            SciPopModeratorComments.objects.create(
                sci_pop=instance,
                comment=validated_data.get("comment"),
                created_by=self.context["request"].user,
            )
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPopModerationSerializer, self).update(instance, validated_data)


class SciPopCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SciPopModeratorComments
        fields = [
            "id",
            "sci_pop",
            "comment",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(SciPopCommentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPopCommentSerializer, self).update(instance, validated_data)


class ArchiveSciPopSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = SciPop
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
            validated_data["sci_pop_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        elif validated_data.get("action") == "put_in":
            validated_data["sci_pop_status"] = StatusTypes.objects.get_or_create(status="archived")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(ArchiveSciPopSerializer, self).update(instance, validated_data)
