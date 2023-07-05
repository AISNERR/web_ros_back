from django.db import models

from apps.tags.models import Tags
from apps.subjects.models import Subjects
from apps.status_model.models import StatusTypes


class Source(models.Model):
    title = models.CharField(max_length=255, unique=True)


class Authors(models.Model):
    title = models.CharField(max_length=255, unique=True)


class PubType(models.Model):
    title = models.CharField(max_length=255, unique=True)


class SciPub(models.Model):
    title = models.CharField(max_length=255)
    date_published = models.DateTimeField(blank=True, null=True)
    source_date = models.CharField(max_length=255)
    authors = models.ManyToManyField(Authors, related_name='scipub_authors',)
    file_pdf = models.FileField(upload_to='pdf_file/', verbose_name="file", blank=True, null=True)
    scipub_type = models.ForeignKey(
        PubType,
        on_delete=models.SET_NULL,
        related_name="pub_in_type",
        null=True
    )
    scipub_status = models.ForeignKey(
        StatusTypes,
        on_delete=models.SET_NULL,
        related_name="pub_in_status",
        null=True,
    )
    summary = models.CharField(max_length=255)
    scipub_source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        related_name="pub_in_source",
        null=True
    )
    release = models.CharField(max_length=255, blank=True, null=True)
    url_reference = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="sci_pub_created",
        blank=True,
        null=True
    )
    subject = models.ForeignKey(
        Subjects,
        on_delete=models.SET_NULL,
        related_name="scipub_in_subjects",
        null=True)
    tags = models.ManyToManyField(Tags, related_name='scipub_tags')
    modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="scipub_modified",
        null=True,
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )
    
    class Meta:
        ordering = ['created_at']


class SciPubModeratorComments(models.Model):
    scipub = models.ForeignKey(
        SciPub,
        on_delete=models.CASCADE,
        related_name="scipub_comments",
    )
    comment = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="scipub_comments_created",
        blank=True,
        null=True,
    )