from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.gis.db import models as geo_models


class ProjectTypes(models.Model):
    alias = models.CharField(max_length=50, unique=True)


class Project(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, null=True)
    project_type = models.ForeignKey(
        to=ProjectTypes,
        on_delete=models.CASCADE,
        related_name="projects_of_type",
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="projects_created",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class ProjectItem(PolymorphicModel):
    project = models.ForeignKey(Project, related_name="items",
                                on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="data_items_created",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OilSpillContour(ProjectItem):
    geom = geo_models.PolygonField(srid=4326)
