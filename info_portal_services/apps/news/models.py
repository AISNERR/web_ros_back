from django.db import models

from apps.tags.models import Tags
from apps.subjects.models import Subjects
from apps.status_model.models import StatusTypes
from apps.location.models import Location


class News(models.Model):
    title = models.CharField(max_length=300)
    text = models.TextField()
    status = models.ForeignKey(
        StatusTypes,
        on_delete=models.SET_NULL,
        related_name="news_in_status",
        null=True)
    tags = models.ManyToManyField(Tags, related_name='news_tags')
    image = models.ImageField(upload_to="news/%Y/%m/%d/", null=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="news_in_location",
        null=True)
    subject = models.ForeignKey(
        Subjects,
        on_delete=models.SET_NULL,
        related_name="marked_news",
        blank=True,
        null=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="news_created",
        blank=True,
        null=True
    )
    modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="news_modified",
        blank=True,
        null=True
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="news_approved",
        blank=True,
        null=True
    )
    published_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="news_published",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    text_short = models.TextField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = ['created_at']


class ReviewActions(models.Model):
    name = models.CharField(max_length=300, unique=True)


class PubReviews(models.Model):
    publication = models.OneToOneField(
        News,
        on_delete=models.CASCADE,
        related_name="news_reviews",
        unique=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="reviews_created",
        blank=True,
        null=True
    )
    action = models.ForeignKey(
        ReviewActions,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )


class ReviewComments(models.Model):
    comment = models.TextField()
    review = models.ForeignKey(
        PubReviews,
        on_delete=models.CASCADE,
        related_name="comments")


class NewsReviewComments(models.Model):
    comment = models.TextField()
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="review_comments")
