from django.db import models

from apps.location.models import Location
from apps.status_model.models import StatusTypes
from apps.tags.models import Tags
from apps.subjects.models import Subjects


class PostInGallery(models.Model):
    title = models.CharField(max_length=300, blank=True)
    author = models.CharField(max_length=300, blank=True)
    alt_text = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="photo_gallery_created",
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to="photo_gallery/%Y/%m/%d/", null=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="photo_gallery_location",
        null=True)
    tags = models.ManyToManyField(Tags, related_name='gallery_tags')

    photo_gallery_status = models.ForeignKey(
        StatusTypes,
        on_delete=models.SET_NULL,
        related_name="photo_gallery_in_status",
        null=True,
    )
    subject = models.ForeignKey(
        Subjects,
        on_delete=models.SET_NULL,
        related_name="photo_gallery_in_subjects",
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class GalleryModeratorComments(models.Model):
    photo = models.ForeignKey(
        PostInGallery,
        on_delete=models.CASCADE,
        related_name="photo_gallery_comments",
    )
    comment = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="photo_gallery_comments_created",
        blank=True,
        null=True,
    )


