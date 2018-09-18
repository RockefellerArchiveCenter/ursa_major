from django.db import models


class Bag(models.Model):
    id, models.CharField(max_length=255, primary_key=True, serialize=False)
    bagName = models.CharField(max_length=255, primary_key=True)
    urlpath = models.CharField(max_length=255, blank=True, null=True)
    accessiondata = models.CharField(max_length=40000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'bag'
