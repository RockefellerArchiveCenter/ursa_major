import json
import random
import shutil
from os import listdir, makedirs
from os.path import isdir, join
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from ursa_major import settings

from .models import Accession, Bag
from .routines import BagDelivery, BagDiscovery, CleanupRoutine
from .views import (AccessionViewSet, BagDeliveryView, BagDiscoveryView,
                    BagViewSet, CleanupRoutineView)

data_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'json')
bag_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'bags')


class BagTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.src_dir = settings.SRC_DIR
        self.tmp_dir = settings.TMP_DIR
        self.dest_dir = settings.DEST_DIR
        self.derivative_creation_dir = settings.DERIVATIVE_CREATION_DIR
        for d in [self.src_dir, self.tmp_dir, self.dest_dir, self.derivative_creation_dir]:
            if isdir(d):
                shutil.rmtree(d)
        shutil.copytree(bag_fixture_dir, self.src_dir)
        for dir in [self.dest_dir, self.tmp_dir, settings.DERIVATIVE_CREATION_DIR]:
            makedirs(dir)
        self.create_objects()
        bag = random.choice(Bag.objects.all())
        bag.origin = "digitization"
        bag.save()

    def set_bag_status(self, status):
        """Helper function to set all bags to a desired process_status."""
        for bag in Bag.objects.all():
            bag.process_status = status
            bag.save()

    def create_objects(self):
        """Tests creation of Accessions and Bags via POST requests."""
        accession_count = 0
        transfer_count = 0
        for f in listdir(data_fixture_dir):
            with open(join(data_fixture_dir, f), 'r') as json_file:
                accession_data = json.load(json_file)
                request = self.factory.post(reverse('accession-list'), accession_data, format='json')
                response = AccessionViewSet.as_view(actions={"post": "create"})(request)
                self.assertEqual(response.status_code, 201, "Response error: {}".format(response.data))
                accession_count += 1
                transfer_count += len(accession_data['transfers'])
        self.assertEqual(len(Accession.objects.all()), accession_count, "Wrong number of accessions created")
        self.assertEqual(len(Bag.objects.all()), transfer_count, "Wrong number of transfers created")

    def test_discover_bags(self):
        """Ensures that BagDiscovery routine runs without errors."""
        self.set_bag_status(Bag.CREATED)
        discovered = BagDiscovery().run()
        self.assertTrue(discovered)
        self.assertTrue(Bag.objects.filter(process_status=Bag.DISCOVERED).exists())

        shutil.rmtree(self.src_dir)
        makedirs(self.src_dir)
        self.set_bag_status(Bag.CREATED)
        with self.assertRaises(Exception) as e:
            BagDiscovery().run()
        self.assertIn("Bag file does not exist.", str(e.exception))

    @patch('bagdiscovery.routines.requests.post')
    def test_deliver_bags(self, mock_post):
        """Ensures that BagDelivery routine runs without errors."""
        mock_post.reset_mock()
        self.set_bag_status(Bag.DISCOVERED)
        message, bag_id = BagDelivery().run()
        self.assertEqual(message, "All bag data delivered.")
        self.assertEqual(len(bag_id), 1)
        self.assertTrue(Bag.objects.filter(process_status=Bag.DELIVERED).exists())
        self.assertEqual(mock_post.call_count, 1)

    def test_cleanup_bags(self):
        """Ensures that CleanupRoutine runs without errors."""
        for bag in Bag.objects.all():
            CleanupRoutine(bag.bag_identifier).run()
        self.assertEqual(0, len(listdir(self.dest_dir)))

    def test_discover_view(self):
        """Ensures BagDiscoveryView executes BagDelivery routine."""
        self.set_bag_status(Bag.CREATED)
        request = self.factory.post(reverse('bagdiscovery'))
        response = BagDiscoveryView.as_view()(request)
        self.assertEqual(response.status_code, 200, "Response error: {}".format(response.data))

    @patch('bagdiscovery.routines.requests.post')
    def test_deliver_view(self, mock_post):
        """Ensures BagDeliveryView executes BagDelivery routine."""
        mock_post.reset_mock()
        self.set_bag_status(Bag.DISCOVERED)
        request = self.factory.post(reverse('bagdelivery'))
        response = BagDeliveryView.as_view()(request)
        self.assertEqual(response.status_code, 200, "Response error: {}".format(response.data))
        self.assertEqual(mock_post.call_count, 1)
        bag = Bag.objects.get(process_status=Bag.DELIVERED)
        mock_post.assert_called_with(
            settings.DELIVERY_URL,
            headers={"Content-Type": "application/json"},
            json={
                "bag_data": bag.data,
                "origin": bag.origin,
                "identifier": bag.bag_identifier})

    def test_cleanup_view(self):
        """Ensures that the CleanupRoutineView executes the CleanupRoutine."""
        for bag in Bag.objects.all():
            request = self.factory.post(reverse('cleanup'), {"identifier": bag.bag_identifier})
            response = CleanupRoutineView.as_view()(request)
            self.assertEqual(response.status_code, 200, "Response error: {}".format(response.data))

    def test_bag_creation(self):
        """Ensures that bag model instances are properly created via POST requests."""
        BAG_DATAS = [
            {
                "origin": "aurora",
                "bag_identifier": "123456"
            },
            {
                "origin": "digitization",
                "bag_identifier": "654321"
            },
            {
                "origin": "legacy_digital",
                "bag_identifier": "12345"
            }
        ]
        for bag_data in BAG_DATAS:
            request = self.factory.post(reverse('bag-list'), bag_data, format='json')
            response = BagViewSet.as_view(actions={"post": "create"})(request)
            for key, value in bag_data.items():
                self.assertEqual(response.data[key], bag_data[key])
            self.assertEqual(response.status_code, 201, "Response error: {}".format(response.data))

    def test_schema(self):
        """Tests the schema view."""
        schema = self.client.get(reverse('schema'))
        self.assertEqual(schema.status_code, 200, "Response error: {}".format(schema))

    def test_health_check(self):
        """Tests the health check endpoint."""
        status = self.client.get(reverse('api_health_ping'))
        self.assertEqual(status.status_code, 200, "Response error: {}".format(status))

    def tearDown(self):
        for d in [self.src_dir, self.dest_dir]:
            if isdir(d):
                shutil.rmtree(d)
