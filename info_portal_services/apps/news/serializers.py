from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User

from .models import News, PubReviews, ReviewComments, NewsReviewComments
from apps.location.serializers import CreateLocationSerializer
from apps.location.models import Location
from apps.status_model.models import StatusTypes
from apps.tags.serializers import TagsSerializer
from apps.subjects.serializers import SubjectsSerializer


class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.ReadOnlyField(source='first_name')
    lastName = serializers.ReadOnlyField(source='last_name')

    class Meta:
        model = User
        fields = ('id', 'firstName', 'lastName')


class NewsSerializer(serializers.ModelSerializer):
    location = CreateLocationSerializer(required=False, allow_null=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'tags', 'image', 'subject', 'location', 'text_short']

    def create(self, validated_data):
        tags = location = None
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            ls = CreateLocationSerializer(data=location_data)
            ls.is_valid(raise_exception=True)
            location = ls.save()

        if location:
            news = News.objects.create(location=location, **validated_data)
        else:
            news = News.objects.create(**validated_data)

        if tags:
            news.tags.set(tags)

        return news
    
    def update(self, instance, validated_data):
        if 'location' in validated_data:
            ls = CreateLocationSerializer(
                data=validated_data["location"])
            ls.is_valid(raise_exception=True)
            location = ls.save()
            instance.location = location

        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.tags.set(validated_data.get('tags', instance.tags))
        instance.text_short = validated_data.get('text_short', instance.text_short)
        instance.save()
        return instance


class NewsGetSerializer(serializers.ModelSerializer):
    subject = SubjectsSerializer(read_only=True)
    location = CreateLocationSerializer()
    tags = TagsSerializer(many=True, read_only=True)
    createdBy = UserSerializer(read_only=True, source='created_by')
    createdAt = serializers.ReadOnlyField(source='created_at')
    modifiedAt = serializers.ReadOnlyField(source='modified_at')
    approvedAt = serializers.ReadOnlyField(source='approved_at')
    publishedAt = serializers.ReadOnlyField(source='published_at')

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'tags', 'image', 'createdAt', 'createdBy',
                  'modifiedAt', 'approvedAt', 'publishedAt', 'subject', 'location',
                  'status', 'text_short']


class NewsGetListSerializer(serializers.ModelSerializer):
    createdBy = UserSerializer(read_only=True, source='created_by')
    createdAt = serializers.ReadOnlyField(source='created_at')
    tags = TagsSerializer(many=True, read_only=True)
    subject = SubjectsSerializer(read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'tags', 'image', 'createdAt', 'createdBy',
                  'subject', 'status', 'text_short']


class LocationSerializer(GeoFeatureModelSerializer):
    news = NewsGetListSerializer(
        source='news_in_location',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Location
        geo_field = 'coordinates'
        fields = ['news', 'coordinates']


class NewsUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['status']


class PubStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusTypes
        fields = ['id', 'status']


class PubReviewCommentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComments
        fields = ['id', 'comment']


class PubReviewGetSerializer(serializers.ModelSerializer):
    comments = PubReviewCommentShortSerializer(many=True, read_only=True)

    class Meta:
        model = PubReviews
        fields = ['id', 'publication', 'action', 'comments', 'created_by']


class PubReviewCreateSerializer(serializers.ModelSerializer):
    ACTION_STATUS_MAP = {
        'approve': 'approved',
        'decline': 'declined',
        'return': 'returned'
    }
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = PubReviews
        fields = ['publication', 'action', 'created_by']

    def create(self, validated_data):
        review = PubReviews.objects.create(**validated_data)

        pub_status = StatusTypes.objects.get(
            status=self.ACTION_STATUS_MAP[review.action.name]
        )
        review.publication.status = pub_status
        review.publication.save()

        return review


class PubReviewUpdateSerializer(serializers.ModelSerializer):
    ACTION_STATUS_MAP = {
        'approve': 'approved',
        'decline': 'declined',
        'return': 'returned'
    }

    class Meta:
        model = PubReviews
        fields = ['action']

    def update(self, review, validated_data):
        if 'action' in validated_data:
            review.action = validated_data["action"]
            pub_status = StatusTypes.objects.get(
                status=self.ACTION_STATUS_MAP[review.action.name]
            )
            review.publication.status = pub_status
            review.save()
            review.publication.save()

        return review


class PubReviewCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComments
        fields = ['id', 'comment', 'review']


class NewsReviewCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsReviewComments
        fields = ['id', 'comment', 'news']


class NewsReviewCommentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsReviewComments
        fields = ['id', 'comment']
