from django.db import models

from apps.subjects.models import Subjects
from apps.tags.models import Tags
from apps.status_model.models import StatusTypes


class EventFormats(models.Model):
    event_format = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True, null=True, blank=False)


class EventTypes(models.Model):
    event_type = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True, null=True, blank=False)


class Events(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField()
    short_description = models.TextField()
    place = models.CharField(max_length=300)
    event_format = models.ForeignKey(
        to=EventFormats,
        on_delete=models.SET_NULL,
        related_name="event_format_in_events",
        null=True,
    )
    event_type = models.ForeignKey(
        to=EventTypes,
        on_delete=models.SET_NULL,
        related_name="event_type_in_events",
        null=True,
    )
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    event_source = models.URLField()
    organizer = models.CharField(max_length=300)
    address = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="events/%Y/%m/%d/", null=True, blank=True)
    tags = models.ManyToManyField(Tags, related_name="events_tags")
    event_status = models.ForeignKey(
        StatusTypes,
        on_delete=models.SET_NULL,
        related_name="events_in_status",
        null=True,
    )
    subject = models.ForeignKey(
        Subjects,
        on_delete=models.SET_NULL,
        related_name="events_subject",
        null=True,
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="events_created",
        null=True,
    )
    modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="events_modified",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True)
    modified_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['created_at']


class EventModeratorComments(models.Model):
    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        related_name="event_comments",
    )
    comment = models.TextField()
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="event_comments_created",
        blank=True,
        null=True,
    )
