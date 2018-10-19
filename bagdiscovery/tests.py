from os.path import isdir
from os import listdir, remove
import shutil

from django.test import TestCase
from .cron import bagStore
from .models import *
from .library import *
from . import settings

data_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'json')
bag_fixture_dir = join(settings.BASE_DIR, 'fixtures', 'bags')


class BagTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        for d in [settings.TEST_LANDING_DIR, settings.TEST_STORAGE_DIR]
        if isdir(d):
            shutil.rmtree(d)

        def test_createaccessions(self):
            for f in listdir(data_fixture_dir):
                with open(join(data_fixture_dir, f), 'r') as json_file:
                    accession_data = json.load(json_file)
                    request = self.factory.post(reverse('accession-list'), accession_data, format='json')
                    response = AccessionViewSet.as_view(actions={"post": "create"})(request)
                    self.assertEqual(response.status_code, 200, "Wrong HTTP code")
                    print('Created accession')

        def test_processbags(self):
            shutil.copytree(bag_fixture_dir, settings.TEST_LANDING_DIR)
            process = bagStore().do()
            self.assertNotEqual(False, process)
