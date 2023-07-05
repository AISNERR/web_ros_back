from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from rest_framework_gis.serializers import GeoModelSerializer

from .models import ProjectItem, OilSpillContour, ProjectTypes, Project


class ProjectTypesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectTypes
        fields = ("id", "alias")


class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ("id", "title", "description", "project_type")


class OilSpillContourSerializer(GeoModelSerializer):
    class Meta:
        model = OilSpillContour
        geo_field = "geom"
        fields = ("id", "project", "geom")


class ProjectItemSerializer(PolymorphicSerializer):
    resource_type_field_name = 'item_type'
    model_serializer_mapping = {
        OilSpillContour: OilSpillContourSerializer
    }
    
    def to_resource_type(self, model_or_instance):
        return model_or_instance._meta.object_name.lower()
