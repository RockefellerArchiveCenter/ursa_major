import json
import logging
import os
import requests
import shutil
from structlog import wrap_logger
from uuid import uuid4
import tarfile

from bravado_core.spec import Spec
from bravado_core.validate import validate_object
from django.core.serializers.json import DjangoJSONEncoder

from .models import Bag
from ursa_major import settings

logger = wrap_logger(logger=logging.getLogger(__name__))


class BagDiscoveryException(Exception): pass
class CleanupException(Exception): pass


class BagDiscovery:
    """Discovers and stores bags, and delivers data to another service."""
    def __init__(self, url, dirs=None):
        self.log = logger
        self.url = url
        self.src_dir = dirs['src'] if dirs else settings.SRC_DIR
        self.tmp_dir = dirs['tmp'] if dirs else settings.TMP_DIR
        self.dest_dir = dirs['dest'] if dirs else settings.DEST_DIR
        for dir in [os.path.join(settings.BASE_DIR, self.src_dir),
                    os.path.join(settings.BASE_DIR, self.tmp_dir),
                    os.path.join(settings.BASE_DIR, self.dest_dir)]:
            if not os.path.isdir(dir):
                raise BagDiscoveryException("Directory does not exist", dir)
        for dir in [os.path.join(settings.BASE_DIR, self.dest_dir), os.path.join(settings.BASE_DIR, self.tmp_dir)]:
            if not os.access(dir, os.W_OK):
                raise BagDiscoveryException("Directory not writable", dir)

    def run(self):
        self.log.bind(request_id=str(uuid4()))
        self.log.debug("Found {} bags to process".format(len(Bag.objects.filter(bag_path__isnull=True))))
        bags = Bag.objects.filter(bag_path__isnull=True)
        bag_count = 0
        for bag in bags:
            self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
            self.log.bind(object=bag.bag_identifier)

            if os.path.exists(os.path.join(self.src_dir, self.bag_name)):
                try:
                    self.unpack_bag()
                    self.log.debug("Bag unpacked")
                except Exception as e:
                    self.log.error("Error unpacking bag: {}".format(e))
                    raise BagDiscoveryException("Error unpacking bag: {}".format(e))
                try:
                    self.save_bag_data(bag)
                    self.log.debug("Bag data saved")
                except Exception as e:
                    self.log.error("Error saving bag data: {}".format(e))
                    raise BagDiscoveryException("Error saving bag data: {}".format(e))
                try:
                    self.move_bag(bag)
                    self.log.debug("Bag moved to storage")
                except Exception as e:
                    self.log.error("Error moving bag: {}".format(e))
                    raise BagDiscoveryException("Error moving bag: {}".format(e))

                if self.url:
                    try:
                        self.post_to_fornax(bag, self.url)
                    except Exception as e:
                        raise BagDiscoveryException("Error sending metadata to Fornax: {}".format(e))

                bag_count += 1

            else:
                continue

        return "{} bags discovered and stored.".format(bag_count)

    def unpack_bag(self):
        tf = tarfile.open(os.path.join(self.src_dir, self.bag_name), 'r')
        tf.extractall(os.path.join(self.tmp_dir))
        tf.close()

    def save_bag_data(self, bag):
        with open(os.path.join(self.tmp_dir, bag.bag_identifier, "{}.json".format(bag.bag_identifier))) as json_file:
            bag_data = json.load(json_file)
            bag.data = bag_data
            bag.save()

    def move_bag(self, bag):
        new_path = os.path.join(self.dest_dir, self.bag_name)
        shutil.move(
            os.path.join(settings.BASE_DIR, self.tmp_dir, bag.bag_identifier, self.bag_name),
            os.path.join(settings.BASE_DIR, new_path))
        bag.bag_path = new_path
        bag.save()
        shutil.rmtree(os.path.join(settings.BASE_DIR, self.tmp_dir, bag.bag_identifier))

    def post_to_fornax(self, bag, url):
        r = requests.post(
            url,
            data=json.dumps(bag.data),
            headers={"Content-Type": "application/json"},
        )
        if r.status_code != 200:
            raise BagDiscoveryException(r.status_code, r.reason)
        return True


class CleanupRoutine:
    """Removes files from the destination directory."""
    def __init__(self, identifier, dirs):
        self.identifier = identifier
        self.dest_dir = dirs['dest'] if dirs else settings.DEST_DIR
        if not self.identifier:
            raise CleanupException("No identifier submitted, unable to perform CleanupRoutine.")

    def run(self):
        try:
            self.filepath = "{}.tar.gz".format(os.path.join(self.dest_dir, self.identifier))
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)
                return "Transfer {} removed.".format(self.identifier)
            return "Transfer {} was not found.".format(self.identifier)
        except Exception as e:
            raise CleanupException(str(e))


class DataValidator:
    def __init__(self, schema_url):
        bravado_config = {
            'validate_swagger_spec': False,
            'validate_requests': False,
            'validate_responses': False,
            'use_models': True,
        }
        spec_dict = requests.get(schema_url).json()
        self.spec = Spec.from_dict(spec_dict, config=bravado_config)
        self.Accession = spec_dict['definitions']['Accession']

    def validate(self, data):
        validate_object(self.spec, self.Accession, data)
