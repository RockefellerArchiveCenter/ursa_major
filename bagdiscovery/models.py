from django.contrib.postgres.fields import JSONField
from django.db import models


class Accession(models.Model):
    archivesspace_identifier = models.CharField(max_length=255, null=True, blank=True)
    data = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)


class Bag(models.Model):
    bag_identifier = models.CharField(max_length=255, unique=True)
    bag_path = models.CharField(max_length=255, null=True, blank=True)
    archivesspace_identifier = models.CharField(max_length=255, null=True, blank=True)
    archivesspace_parent_identifier = models.CharField(max_length=255, null=True, blank=True)
    accession = models.ForeignKey(Accession, on_delete=models.CASCADE)
    data = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
