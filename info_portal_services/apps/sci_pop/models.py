from django.db import models

from apps.status_model.models import StatusTypes
from apps.tags.models import Tags
from apps.subjects.models import Subjects


class Authors(models.Model):
    full_name = models.CharField(max_length=255, unique=True)


class PopFormat(models.Model):
    title = models.CharField(max_length=255, unique=True)


class SciPop(models.Model):
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Authors, related_name='scipop_authors', )
    format = models.ForeignKey(
        PopFormat,
        on_delete=models.SET_NULL,
        related_name="pop_in_format",
        null=True
    )

    sci_pop_status = models.ForeignKey(
        StatusTypes,
        on_delete=models.SET_NULL,
        related_name="sci_pop_in_status",
        null=True,
    )

    date_video = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    material_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    video = models.URLField()
    description = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="sci_pop_created",
        blank=True,
        null=True
    )
    subject = models.ForeignKey(
        Subjects,
        on_delete=models.SET_NULL,
        related_name="scipop_in_subjects",
        null=True)
    tags = models.ManyToManyField(Tags, related_name='scipop_tags')

    class Meta:
        ordering = ['created_at']


class SciPopModeratorComments(models.Model):
    sci_pop = models.ForeignKey(
        SciPop,
        on_delete=models.CASCADE,
        related_name="sci_pop_comments",
    )
    comment = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="sci_pop_comments_created",
        blank=True,
        null=True,
    )
