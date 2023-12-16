from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class CreatedByModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class DatedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
