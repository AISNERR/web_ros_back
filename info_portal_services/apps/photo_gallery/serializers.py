from rest_framework import serializers

from .models import PostInGallery, GalleryModeratorComments
from apps.news.serializers import UserSerializer
from apps.location.serializers import CreateLocationSerializer
from apps.tags.serializers import TagsSerializer
from apps.subjects.serializers import SubjectsSerializer
from ..status_model.models import StatusTypes


class GalleryCreateSerializer(serializers.ModelSerializer):
    location = serializers.CharField(max_length=510)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = PostInGallery
        fields = ['id', 'title', 'author', 'alt_text', 'tags', 'image', 'subject', 'location', 'created_by', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data["photo_gallery_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            ls = CreateLocationSerializer(data=location_data)
            ls.is_valid(raise_exception=True)
            location = ls.save()
            validated_data['location'] = location
        validated_data["created_by"] = self.context['request'].user
        return super(GalleryCreateSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            ls = CreateLocationSerializer(data=location_data)
            ls.is_valid(raise_exception=True)
            location = ls.save()
            validated_data['location'] = location
        validated_data["photo_gallery_status"] = StatusTypes.objects.get_or_create(status="created")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(GalleryCreateSerializer, self).update(instance, validated_data)


class GalleryGetSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    location = CreateLocationSerializer(read_only=True)

    class Meta:
        model = PostInGallery
        fields = '__all__'


class GalleryCommentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(GalleryCommentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["modified_by"] = self.context['request'].user
        return super(GalleryCommentSerializer, self).update(instance, validated_data)

    class Meta:
        model = GalleryModeratorComments
        fields = [
            "id",
            "photo",
            "comment",
        ]


class GalleryModeratorCommentsSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = GalleryModeratorComments
        fields = [
            "id",
            "comment",
            "created_by",
        ]


class GalleryInfoSerializer(serializers.ModelSerializer):
    photo_gallery_comments = GalleryModeratorCommentsSerializer(
        many=True,
        read_only=True,
    )
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    location = CreateLocationSerializer(required=False, allow_null=True)

    class Meta:
        model = PostInGallery
        fields = '__all__'


class GalleryStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostInGallery
        fields = []

    def update(self, instance, validated_data):
        validated_data["photo_gallery_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        return super(GalleryStatusSerializer, self).update(instance, validated_data)


class GalleryModerationSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True)

    class Meta:
        model = PostInGallery
        fields = [
            "id",
            "photo_gallery_status",
            "comment",
        ]

    def validate_photo_gallery_status(self, data):
        allowed_statuses = (
            "declined",
            "returned",
            "published",
        )
        if data.status not in allowed_statuses:
            raise serializers.ValidationError(f"Change photo_gallery status to {data.status} is not allowed")
        return data

    def update(self, instance, validated_data):
        if validated_data.get("comment"):
            GalleryModeratorComments.objects.create(
                photo=instance,
                comment=validated_data.get("comment"),
                created_by=self.context["request"].user,
            )
        validated_data["modified_by"] = self.context['request'].user
        return super(GalleryModerationSerializer, self).update(instance, validated_data)


class ArchiveGallerySerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = PostInGallery
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
            validated_data["photo_gallery_status"] = StatusTypes.objects.get_or_create(status="ready_for_review")[0]
        elif validated_data.get("action") == "put_in":
            validated_data["photo_gallery_status"] = StatusTypes.objects.get_or_create(status="archived")[0]
        validated_data["modified_by"] = self.context['request'].user
        return super(ArchiveGallerySerializer, self).update(instance, validated_data)
