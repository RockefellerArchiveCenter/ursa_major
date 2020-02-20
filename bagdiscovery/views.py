from asterism.views import prepare_response
from django.db import IntegrityError
from jsonschema.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Accession, Bag
from .routines import BagDelivery, BagDiscovery, CleanupRoutine, validate_data
from .serializers import (AccessionListSerializer, AccessionSerializer,
                          BagListSerializer, BagSerializer)


class AccessionViewSet(ModelViewSet):
    """
    retrieve:
    Return data about an accession, identified by a primary key.

    list:
    Return paginated data about all accessions.

    create:
    Create a new accession. Also creates Bags for each transfer identified in
    the `transfers` key.

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
        try:
            validate_data(request.data)
            accession = Accession.objects.create(
                data=request.data
            )
            transfer_ids = []
            for t in request.data['transfers']:
                Bag.objects.create(
                    bag_identifier=t['identifier'],
                    accession=accession,
                    process_status=Bag.CREATED,
                )
                transfer_ids.append(t['identifier'])
            return Response(prepare_response(
                ("Accession stored and transfer objects created", transfer_ids)),
                status=201)
        except ValidationError as e:
            return Response(prepare_response(
                "Invalid accession data: {}: {}".format(list(e.path), e.message)),
                status=400)
        except IntegrityError as e:
            return Response(prepare_response(e), status=409)
        except Exception as e:
            return Response(prepare_response(e), status=500)


class BagViewSet(ModelViewSet):
    """
    retrieve:
    Return data about a bag, identified by a primary key. Accepts the parameter
    `id`, which will return all bags matching that id.

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


class BaseRoutineView(APIView):
    """Base view for routines. Accepts POST request only."""

    def post(self, request, format=None):
        try:
            response = self.routine().run()
            return Response(prepare_response(response), status=200)
        except Exception as e:
            return Response(prepare_response(e), status=500)


class BagDiscoveryView(BaseRoutineView):
    """Discovers transfers delivered in accessions and prepares them for
    delivery to the next service. Accepts POST requests only."""
    routine = BagDiscovery


class BagDeliveryView(BaseRoutineView):
    """Runs the AssembleSIPs cron job. Accepts POST requests only."""
    routine = BagDelivery


class CleanupRoutineView(APIView):
    """Removes a transfer from the destination directory. Accepts POST requests
    only."""

    def post(self, request, format=None):
        try:
            identifier = request.data.get('identifier')
            response = CleanupRoutine(identifier).run()
            return Response(prepare_response(response), status=200)
        except Exception as e:
            return Response(prepare_response(e), status=500)
