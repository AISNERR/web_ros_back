from django.db import models

class StatusTypes(models.Model):
    status = models.CharField(max_length=300, unique=True)
