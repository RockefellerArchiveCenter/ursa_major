from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from .library import *
from .models import Accession, Bag
from .serializers import AccessionSerializer, AccessionListSerializer, BagSerializer, BagListSerializer
from ursa_major import settings
import magic
from os.path import join


class AccessionViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return data about an accession, identified by a primary key.

    list:
    Return paginated data about all accessions.

    create:
    Create a new accession. Also creates Bags for each transfer identified in the `transfers` key.

    update:
    Update an existing accession, identified by a primary key.
    """
    model = Accession
    queryset = Accession.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AccessionListSerializer
        return AccessionSerializer

    def create(self, request):
        accession = Accession.objects.create(
            data=request.data
        )
        for transfer in request.data['transfers']:
            # get data from Aurora?
            transfer = Bag.objects.create(
                bag_identifier=transfer['identifier'],
                accession=accession,
            )
        serialized = AccessionSerializer(accession, context={'request': request})
        return Response(serialized.data)


class BagViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return data about a bag, identified by a primary key. Accepts the parameter `id`, which will return all bags matching that id.

    list:
    Return paginated data about all bags.

    create:
    Create a new bag.

    update:
    Update an existing bag, identified by a primary key.
    """
    model = Bag
    queryset = Bag.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BagListSerializer
        return BagSerializer
