from django.db import models


# class Bag(models.Model):
#     id = models.CharField(max_length=255, primary_key=True)
#     bag = models.CharField(max_length=4500, blank=True, null=True)
#     date = models.CharField(max_length=400, blank=True, null=True)
#     time = models.CharField(max_length=4500, blank=True, null=True)
#
#     class Meta:
#         managed = True
#         db_table = 'bag'
#

class Bag(models.Model):
    accessiondata = models.CharField(max_length=255, primary_key=True)
    urlpath = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'bag'
