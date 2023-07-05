from rest_framework import serializers

from apps.news.serializers import UserSerializer
from .models import NewsRss, NewsRssGroups


class NewsRssGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsRssGroups
        fields = [
            "id",
            "title",
        ]


class NewsRssSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = NewsRss
        fields = [
            "id",
            "title",
            "group",
            "site",
            "rss_source",
            "created_by",
        ]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(NewsRssSerializer, self).create(validated_data)
