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
    DISCOVERING = 4
    DELIVERING = 5
    PROCESS_STATUS_CHOICES = (
        (CREATED, "Created"),
        (DISCOVERED, "Discovered"),
        (DELIVERED, "Delivered"),
        (DISCOVERING, "Discovering"),
        (DELIVERING, "Delivering")
    )
    accession = models.ForeignKey(Accession, on_delete=models.CASCADE, null=True, blank=True)
    process_status = models.IntegerField(choices=PROCESS_STATUS_CHOICES, default=CREATED)
