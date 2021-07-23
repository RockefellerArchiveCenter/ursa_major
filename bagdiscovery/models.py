from asterism.models import BasePackage
from django.db import models


class Accession(models.Model):
    data = models.JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)


class Bag(BasePackage):
    CREATED = 1
    DISCOVERED = 2
    DELIVERED = 3
    PROCESS_STATUS_CHOICES = (
        (CREATED, "Created"),
        (DISCOVERED, "Discovered"),
        (DELIVERED, "Delivered")
    )
    accession = models.ForeignKey(Accession, on_delete=models.CASCADE, null=True, blank=True)
