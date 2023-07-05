from django.db import models


class Subjects(models.Model):
    title = models.CharField(max_length=300, unique=True)
