import logging
import urllib
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from structlog import wrap_logger
from uuid import uuid4
from .library import BagDiscovery, isdatavalid
from .models import Accession, Bag
from .serializers import AccessionSerializer, AccessionListSerializer, BagSerializer, BagListSerializer
from ursa_major import settings

logger = wrap_logger(logger=logging.getLogger(__name__))


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
        self.log = logger
        self.log.bind(transaction_id=str(uuid4()), request_id=str(uuid4()))
        if isdatavalid(request.data):
            accession = Accession.objects.create(
                data=request.data
            )
            self.log.debug("Accession saved", object=accession)
            for transfer in request.data['transfers']:
                transfer = Bag.objects.create(
                    bag_identifier=transfer['identifier'],
                    accession=accession,
                )
                self.log.debug("Bag saved", object=transfer)
            serialized = AccessionSerializer(accession, context={'request': request})
            return Response(serialized.data)
        else:
            self.log.error("Invalid accession data")
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


class BagDiscoveryView(APIView):
    """Runs the AssembleSIPs cron job. Accepts POST requests only."""

    def post(self, request, format=None):
        dirs = None
        url = request.GET.get('post_service_url', '')
        url = (urllib.parse.unquote(url) if url else '')

        print(url, 'this URL was passed FROM zodiac built FROM service URL')

        if request.POST.get('test'):
            dirs = {"landing": settings.TEST_LANDING_DIR, "storage": settings.TEST_STORAGE_DIR}
        try:
            discover = BagDiscovery(url, dirs).run()
            return Response({"detail": discover}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
