import json
import logging
import os
import shutil
from structlog import wrap_logger
from uuid import uuid4
import tarfile

import requests
from django.core.serializers.json import DjangoJSONEncoder

from .models import Bag
from ursa_major import settings

logger = wrap_logger(logger=logging.getLogger(__name__))


class BagDiscoveryException(Exception): pass


class BagDiscovery:
    def __init__(self, url, dirs=None):
        self.log = logger
        self.url = url
        self.landing_dir = dirs['landing'] if dirs else settings.LANDING_DIR
        self.storage_dir = dirs['storage'] if dirs else settings.STORAGE_DIR
        if not os.path.isdir(os.path.join(settings.BASE_DIR, self.storage_dir)):
            raise BagDiscoveryException("Storage directory does not exist.")
        if not os.access(os.path.join(settings.BASE_DIR, self.storage_dir), os.W_OK):
            raise BagDiscoveryException("Storage directory not writable.")

    def run(self):
        self.log.bind(request_id=str(uuid4()))
        self.log.debug("Found {} bags to process".format(len(Bag.objects.filter(bag_path__isnull=True))))
        bags = Bag.objects.filter(bag_path__isnull=True)
        bag_count = 0
        for bag in bags:
            self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
            self.log.bind(object=bag.bag_identifier)

            if os.path.exists(os.path.join(self.landing_dir, self.bag_name)):
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
                        raise BagDiscoveryException("Error sending POST of metadata to Fornax: {}".format(e))

                bag_count += 1

            else:
                continue

        return "{} bags discovered and stored.".format(bag_count)

    def unpack_bag(self):
        tf = tarfile.open(os.path.join(self.landing_dir, self.bag_name), 'r')
        tf.extractall(os.path.join(self.landing_dir))
        tf.close()
        os.remove(os.path.join(self.landing_dir, self.bag_name))

    def save_bag_data(self, bag):
        with open(os.path.join(self.landing_dir, bag.bag_identifier, "{}.json".format(bag.bag_identifier))) as json_file:
            bag_data = json.load(json_file)
            bag.data = bag_data
            bag.save()

    def move_bag(self, bag):
        new_path = os.path.join(self.storage_dir, self.bag_name)
        shutil.move(
            os.path.join(settings.BASE_DIR, self.landing_dir, bag.bag_identifier, self.bag_name),
            os.path.join(settings.BASE_DIR, new_path))
        bag.bag_path = new_path
        bag.save()
        shutil.rmtree(os.path.join(settings.BASE_DIR, self.landing_dir, bag.bag_identifier))

    def post_to_fornax(self, bag, url):
        r = requests.post(
            url,
            data=json.dumps(bag.data),
            headers={"Content-Type": "application/json"},
        )
        if r.status_code != 200:
            raise BagDiscoveryException(r.status_code, r.reason)
        return True


def isdatavalid(data):
    requiredKeys = ("extent_files", "url", "acquisition_type", "use_restrictions",
                    "extent_size",  "start_date", "end_date", "process_status", "accession_number",
                    "rights_statements", "title", "creators", "transfers", "access_restrictions",
                    "organization", "created", "appraisal_note", "description", "resource",
                    "language", "last_modified", "accession_date")

    keylist = data.keys()
    if (set(keylist) - set(requiredKeys)) == set() and (set(requiredKeys) - set(keylist)) == set():
        return True
    else:
        return False
