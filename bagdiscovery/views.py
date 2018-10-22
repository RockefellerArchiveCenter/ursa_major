from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .library import *
from .models import Accession, Bag
from .serializers import AccessionSerializer, AccessionListSerializer, BagSerializer, BagListSerializer
from ursa_major import settings


class AccessionViewSet(ModelViewSet):
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
    queryset = Accession.objects.all().order_by('-created')

    def get_serializer_class(self):
        if self.action == 'list':
            return AccessionListSerializer
        return AccessionSerializer

    def create(self, request):
        if isdatavalid(request.data):
            accession = Accession.objects.create(
                data=request.data
            )

            for transfer in request.data['transfers']:
                transfer = Bag.objects.create(
                    bag_identifier=transfer['identifier'],
                    accession=accession,
                )
            serialized = AccessionSerializer(accession, context={'request': request})
            return Response(serialized.data)
        else:
            return Response({"detail": "Invalid accession data"}, status=500)


class BagViewSet(ModelViewSet):
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

    def get_serializer_class(self):
        if self.action == 'list':
            return BagListSerializer
        return BagSerializer

    def get_queryset(self):
        queryset = Bag.objects.all().order_by('-created')
        bag_identifier = self.request.GET.get('id')
        if bag_identifier:
            queryset = queryset.filter(bag_identifier=bag_identifier)
        return queryset
