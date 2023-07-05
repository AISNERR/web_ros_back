from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from apps.location.models import Location


class CreateLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'coordinates'
        fields = ['coordinates']


