import logging
import urllib
from django.db import IntegrityError
from django.shortcuts import render
from jsonschema.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from structlog import wrap_logger
from uuid import uuid4
from .library import BagDiscovery, CleanupRoutine, DataValidator
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

    def format_field_path(self, absolute_path):
        path = []
        for part in absolute_path:
            if type(part) is str:
                path.append(part)
            elif type(part) is int:
                path[-1] = path[-1] + "[{}]".format(part)
        return '.'.join(path)

    def create(self, request):
        self.log = logger
        self.log.bind(transaction_id=str(uuid4()), request_id=str(uuid4()))
        try:
            DataValidator(settings.SCHEMA_URL).validate(request.data)
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
        except ValidationError as e:
            return Response({"detail": "{}: {}".format(self.format_field_path(e.absolute_path), e.message)}, status=400)
        except IntegrityError as e:
            return Response({"detail": e.args[0]}, status=409)
        except Exception as e:
            return Response({"detail": e.message}, status=500)


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
        dirs = {"src": settings.TEST_SRC_DIR, "tmp": settings.TEST_TMP_DIR, "dest": settings.TEST_DEST_DIR} if request.POST.get('test') else None
        url = request.GET.get('post_service_url')
        url = (urllib.parse.unquote(url) if url else '')

        try:
            discover = BagDiscovery(url, dirs).run()
            return Response({"detail": discover}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)


class CleanupRoutineView(APIView):
    """Removes a transfer from the destination directory. Accepts POST requests only."""

    def post(self, request, format=None):
        dirs = {"src": settings.TEST_SRC_DIR, "dest": settings.TEST_DEST_DIR} if request.POST.get('test') else None
        identifier = request.data.get('identifier')

        try:
            discover = CleanupRoutine(identifier, dirs).run()
            return Response({"detail": discover}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
