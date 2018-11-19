import json
from os.path import isdir, join
from os import makedirs, listdir, remove
import shutil
import vcr

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from .cron import BagStore
from .models import Accession, Bag
from .library import BagDiscovery, CleanupRoutine
from .views import AccessionViewSet, BagDiscoveryView, CleanupRoutineView
from ursa_major import settings

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
        self.src_dir = settings.TEST_SRC_DIR
        self.tmp_dir = settings.TEST_TMP_DIR
        self.dest_dir = settings.TEST_DEST_DIR
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
                self.assertEqual(response.status_code, 200, "Wrong HTTP code")
                accession_count += 1
                transfer_count += len(accession_data['transfers'])
        self.assertEqual(len(Accession.objects.all()), accession_count, "Wrong number of accessions created")
        self.assertEqual(len(Bag.objects.all()), transfer_count, "Wrong number of transfers created")

    def process_bags(self):
        with process_vcr.use_cassette('process_bags.json'):
            processor = BagDiscovery('http://fornax-web:8003/sips/', dirs={"src": self.src_dir, "tmp": self.tmp_dir, "dest": self.dest_dir}).run()
            self.assertTrue(processor)
            for bag in Bag.objects.all():
                self.assertTrue(bag.data)

    def cleanup_bags(self):
        for bag in Bag.objects.all():
            CleanupRoutine(bag.bag_identifier, dirs={"dest": self.dest_dir}).run()
        self.assertEqual(0, len(listdir(self.dest_dir)))

    def run_view(self):
        with process_vcr.use_cassette('process_bags.json'):
            print('*** Test run view ***')
            request = self.factory.post(reverse('bagdiscovery'), {"test": True})
            response = BagDiscoveryView.as_view()(request)
            self.assertEqual(response.status_code, 200, "Wrong HTTP code")

    def cleanup_view(self):
        print('*** Test cleanup view ***')
        for bag in Bag.objects.all():
            request = self.factory.post(reverse('cleanup'), {"test": True, "identifier": bag.bag_identifier})
            response = CleanupRoutineView.as_view()(request)
            self.assertEqual(response.status_code, 200, "Wrong HTTP code")

    def schema(self):
        print('*** Getting schema view ***')
        schema = self.client.get(reverse('schema-json', kwargs={"format": ".json"}))
        self.assertEqual(schema.status_code, 200, "Wrong HTTP code")

    def health_check(self):
        print('*** Getting status view ***')
        status = self.client.get(reverse('api_health_ping'))
        self.assertEqual(status.status_code, 200, "Wrong HTTP code")

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
