from rest_framework import serializers

from apps.news.serializers import UserSerializer
from .models import Layers, LayerTypes, LayerGroups, Services, LayersViewSet


class ServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = [
            'id',
            'name',
            'description',
            'url',
            'service_type',
        ]


class LayerTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayerTypes
        fields = [
            'id',
            'name',
        ]


class LayerGroupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayerGroups
        fields = [
            'id',
            'name',
            'description',
            'visible',
        ]


class LayersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Layers
        fields = [
            'id',
            'name',
            'description',
            'url',
            'layer_type_id',
            'layer_group_id',
            'service_id',
            'visible',
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context['request'].user
        return super(LayersSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["modified_by"] = self.context['request'].user
        return super(LayersSerializer, self).update(instance, validated_data)


class LayerGetSerializer(serializers.ModelSerializer):
    layer_type_id = LayerTypesSerializer(read_only=True)
    layer_group_id = LayerGroupsSerializer(read_only=True)
    service_id = ServicesSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Layers
        fields = [
            'id',
            'name',
            'description',
            'url',
            'layer_type_id',
            'layer_group_id',
            'service_id',
            'visible',
            'created_at',
            'updated_at',
            'created_by',
        ]


class LayersViewSetCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LayersViewSet
        fields = [
            'id',
            'name',
            'layers',
            'layers_tree',
        ]


class LayersViewSetGetSerializer(serializers.ModelSerializer):
    layers = LayerGetSerializer(read_only=True, many=True)

    class Meta:
        model = LayersViewSet
        fields = [
            'id',
            'name',
            'layers',
            'layers_tree',
        ]
