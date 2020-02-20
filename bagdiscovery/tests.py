import json
import shutil
from os import listdir, makedirs
from os.path import isdir, join

import vcr
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from ursa_major import settings

from .models import Accession, Bag
from .routines import BagDelivery, BagDiscovery, CleanupRoutine
from .views import (AccessionViewSet, BagDeliveryView, BagDiscoveryView,
                    CleanupRoutineView)

data_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'json')
bag_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'bags')

process_vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['path', 'method', 'query'],
    filter_query_parameters=['username', 'password'],
    filter_headers=['Authorization'],
)


class BagTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.src_dir = settings.SRC_DIR
        self.tmp_dir = settings.TMP_DIR
        self.dest_dir = settings.DEST_DIR
        for d in [self.src_dir, self.tmp_dir, self.dest_dir]:
            if isdir(d):
                shutil.rmtree(d)
        shutil.copytree(bag_fixture_dir, self.src_dir)
        for dir in [self.dest_dir, self.tmp_dir]:
            makedirs(dir)

    def createobjects(self):
        print('*** Creating objects ***')
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

    def process_bags(self):
        print('*** Test routines ***')
        for routine, end_status in [(BagDiscovery, Bag.DISCOVERED), (BagDelivery, Bag.DELIVERED)]:
            with process_vcr.use_cassette('process_bags.json'):
                completed = routine().run()
                self.assertTrue(completed)
                for bag in Bag.objects.all():
                    self.assertEqual(bag.process_status, str(end_status))

    def cleanup_bags(self):
        for bag in Bag.objects.all():
            CleanupRoutine(bag.bag_identifier).run()
        self.assertEqual(0, len(listdir(self.dest_dir)))

    def run_view(self):
        print('*** Test views ***')
        # Reset bag process_status so the view executes the routine
        for bag in Bag.objects.all():
            bag.process_status = Bag.CREATED
            bag.save()
        for url_name, view in [('bagdiscovery', BagDiscoveryView), ('bagdelivery', BagDeliveryView)]:
            with process_vcr.use_cassette('process_bags.json'):
                request = self.factory.post(reverse(url_name))
                response = view.as_view()(request)
                self.assertEqual(response.status_code, 200, "Response error: {}".format(response.data))

    def cleanup_view(self):
        print('*** Test cleanup view ***')
        for bag in Bag.objects.all():
            request = self.factory.post(reverse('cleanup'), {"identifier": bag.bag_identifier})
            response = CleanupRoutineView.as_view()(request)
            self.assertEqual(response.status_code, 200, "Response error: {}".format(response.data))

    def schema(self):
        print('*** Getting schema view ***')
        schema = self.client.get(reverse('schema'))
        self.assertEqual(schema.status_code, 200, "Response error: {}".format(schema))

    def health_check(self):
        print('*** Getting status view ***')
        status = self.client.get(reverse('api_health_ping'))
        self.assertEqual(status.status_code, 200, "Response error: {}".format(status))

    def tearDown(self):
        for d in [self.src_dir, self.dest_dir]:
            if isdir(d):
                shutil.rmtree(d)

    def test_bags(self):
        self.createobjects()
        self.process_bags()
        self.cleanup_bags()
        self.run_view()
        self.cleanup_view()
        self.schema()
        self.health_check()
