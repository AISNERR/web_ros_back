from django.db import models


class NewsRssGroups(models.Model):
    title = models.CharField(max_length=255)


class NewsRss(models.Model):
    title = models.CharField(max_length=255)
    group = models.ForeignKey(
        to=NewsRssGroups,
        on_delete=models.SET_NULL,
        related_name="news_rss_in_group",
        null=True,
        blank=True,
    )
    site = models.URLField()
    rss_source = models.URLField(blank=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="news_rss_created",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
