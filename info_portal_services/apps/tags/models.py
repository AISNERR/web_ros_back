from django.db import models


class Tags(models.Model):
    title = models.CharField(max_length=300, unique=True)
