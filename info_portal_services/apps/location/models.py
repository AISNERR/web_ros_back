from django.db import models
from django.contrib.gis.db.models import PointField

class Location(models.Model):
    coordinates = PointField(srid=4326, null=True)