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
from .library import BagDiscovery
from .views import AccessionViewSet, BagDiscoveryView
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
        for d in [settings.TEST_LANDING_DIR, settings.TEST_STORAGE_DIR]:
            if isdir(d):
                shutil.rmtree(d)

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

    def processbags(self):
        with process_vcr.use_cassette('process_bags.json'):
            shutil.copytree(bag_fixture_dir, settings.TEST_LANDING_DIR)
            processor = BagDiscovery('http://fornax-web:8003/sips/', dirs={"landing": settings.TEST_LANDING_DIR, "storage": settings.TEST_STORAGE_DIR}).run()
            self.assertTrue(processor)
            for bag in Bag.objects.all():
                self.assertTrue(bag.data)

    def run_view(self):
        with process_vcr.use_cassette('process_bags.json'):
            print('*** Test run view ***')
            request = self.factory.post(reverse('bagdiscovery'), {"test": True})
            response = BagDiscoveryView.as_view()(request)
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
        for d in [settings.TEST_LANDING_DIR, settings.TEST_STORAGE_DIR]:
            if isdir(d):
                shutil.rmtree(d)

    def test_bags(self):
        self.createobjects()
        self.processbags()
        self.run_view()
        self.schema()
        self.health_check()
