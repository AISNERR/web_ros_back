from rest_framework import serializers

from .models import SciPub, Authors, Source, SciPubModeratorComments
from apps.tags.serializers import TagsSerializer
from apps.subjects.serializers import SubjectsSerializer
from apps.news.serializers import UserSerializer
from apps.status_model.models import StatusTypes


class SciPubSourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Source
        fields = [
            'id',
            'title'
        ]


class SciPubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = [
            'id',
            'title'
        ]


class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Authors
        fields = [
            'id',
            'title'
        ]


class AuthorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Authors
        fields = ['title']


class SciPubCreateSerializer(serializers.ModelSerializer):
    authors = AuthorCreateSerializer(
        required=False,
        allow_null=True,
        read_only=True,
        many=True
    )

    class Meta: 
        model = SciPub
        fields = [
            'id',
            'title',
            'date_published',
            'source_date',
            'authors',
            'file_pdf',
            'scipub_type',
            'summary',
            'scipub_source',
            'release',
            'url_reference',
            'subject',
            'tags',
            'created_at',
            'created_by',
            'modified_by',
            'modified_at',
        ]

    def create(self, validated_data):
        validated_data["scipub_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["created_by"] = self.context['request'].user
        if 'authors' in validated_data:
            authors = validated_data.pop('authors')
            authors_ids = []
            for name in authors:
                author = Authors.objects.get_or_create(title=name)[0]
                authors_ids.append(author)
            validated_data["authors"] = authors_ids

        return super(SciPubCreateSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # We change status "returned" to "created" after content-manager has updated his scipub
        # but not yet send it to review
        validated_data["scipub_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPubCreateSerializer, self).update(instance, validated_data)



class SciPubStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = SciPub
        fields = []

    def update(self, instance, validated_data):
        # Contend-manager send publication on review
        validated_data["scipub_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        return super(SciPubStatusSerializer, self).update(instance, validated_data)


class SciPubGetSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(read_only=True, many=True)
    scipub_type = SciPubTypeSerializer(read_only=True)
    scipub_source = SciPubSourceSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    subject = SubjectsSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)

    class Meta:
        model = SciPub
        fields = '__all__'


class SciPubModeratorCommentsSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = SciPubModeratorComments
        fields = [
            "id",
            "comment",
            "created_by",
        ]


class SciPubInfoSerializer(serializers.ModelSerializer):
    scipub_comments = SciPubModeratorCommentsSerializer(
        many=True,
        read_only=True,
    )
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = SciPub
        fields = '__all__'


class SciPubModerationSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True)

    class Meta:
        model = SciPub
        fields = [
            "id",
            "scipub_status",
            "comment",
        ]

    def validate_scipub_status(self, data):
        allowed_statuses = (
            "declined",
            "returned",
            "published",
        )
        if data.status not in allowed_statuses:
            raise serializers.ValidationError(f"Change status to {data.status} is not allowed")
        return data

    def update(self, instance, validated_data):
        if validated_data.get("comment"):
            SciPubModeratorComments.objects.create(
                scipub=instance,
                comment=validated_data.get("comment"),
                created_by=self.context["request"].user,
            )
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPubModerationSerializer, self).update(instance, validated_data)


class SciPubCommentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(SciPubCommentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["modified_by"] = self.context['request'].user
        return super(SciPubCommentSerializer, self).update(instance, validated_data)

    class Meta:
        model = SciPubModeratorComments
        fields = [
            "id",
            "scipub",
            "comment",
        ]


class ArchiveSciPubSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = SciPub
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
            validated_data["scipub_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        elif validated_data.get("action") == "put_in":
            validated_data["scipub_status"] = StatusTypes.objects.get_or_create(status="archived")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(ArchiveSciPubSerializer, self).update(instance, validated_data)
