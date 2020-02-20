import json
import os
import shutil
import tarfile

import jsonschema
import requests
from ursa_major import settings

from .models import Bag


class BagDiscoveryException(Exception):
    pass


class CleanupException(Exception):
    pass


def validate_data(data):
    with open(os.path.join(settings.BASE_DIR, settings.SCHEMA_PATH), "r") as jf:
        schema = json.load(jf)
        jsonschema.validate(instance=data, schema=schema)


class BagDiscovery:
    """Discovers and stores bags, and delivers data to another service."""

    def __init__(self):
        self.src_dir = settings.SRC_DIR
        self.tmp_dir = settings.TMP_DIR
        self.dest_dir = settings.DEST_DIR
        for dir in [os.path.join(settings.BASE_DIR, self.src_dir),
                    os.path.join(settings.BASE_DIR, self.tmp_dir),
                    os.path.join(settings.BASE_DIR, self.dest_dir)]:
            if not os.path.isdir(dir):
                raise BagDiscoveryException("Directory does not exist", dir)
        for dir in [os.path.join(settings.BASE_DIR, self.dest_dir), os.path.join(
                settings.BASE_DIR, self.tmp_dir)]:
            if not os.access(dir, os.W_OK):
                raise BagDiscoveryException("Directory not writable", dir)

    def run(self):
        bag_ids = []
        for bag in Bag.objects.filter(process_status=Bag.CREATED):
            self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
            if os.path.exists(os.path.join(self.src_dir, self.bag_name)):
                self.unpack_bag()
                self.save_bag_data(bag)
                self.move_bag(bag)
                bag_ids.append(bag.bag_identifier)
                bag.process_status = bag.DISCOVERED
                bag.save()
            else:
                continue
        return ("All bags discovered.", bag_ids)

    def unpack_bag(self):
        try:
            tf = tarfile.open(os.path.join(self.src_dir, self.bag_name), 'r')
            tf.extractall(os.path.join(self.tmp_dir))
            tf.close()
        except Exception as e:
            raise BagDiscoveryException(
                "Error unpacking bag: {}".format(e), self.bag_name)

    def save_bag_data(self, bag):
        try:
            with open(os.path.join(self.tmp_dir, bag.bag_identifier, "{}.json".format(bag.bag_identifier))) as json_file:
                bag_data = json.load(json_file)
                validate_data(bag_data)
                bag.data = bag_data
                bag.save()
        except jsonschema.exceptions.ValidationError as e:
            raise BagDiscoveryException(
                "Invalid bag data: {}: {}".format(
                    list(
                        e.path), e.message))
        except Exception as e:
            raise BagDiscoveryException(
                "Error saving bag data: {}".format(e),
                bag.bag_identifier)

    def move_bag(self, bag):
        try:
            new_path = os.path.join(self.dest_dir, self.bag_name)
            shutil.move(
                os.path.join(
                    settings.BASE_DIR,
                    self.tmp_dir,
                    bag.bag_identifier,
                    self.bag_name),
                os.path.join(settings.BASE_DIR, new_path))
            bag.bag_path = new_path
            bag.save()
            shutil.rmtree(
                os.path.join(
                    settings.BASE_DIR,
                    self.tmp_dir,
                    bag.bag_identifier))
        except Exception as e:
            raise BagDiscoveryException(
                "Error moving bag: {}".format(e),
                bag.bag_identifier)


class BagDelivery:

    def run(self):
        bag_ids = []
        for bag in Bag.objects.filter(process_status=Bag.DISCOVERED):
            try:
                self.deliver_data(bag, settings.DELIVERY_URL)
                bag_ids.append(bag.bag_identifier)
                bag.process_status = Bag.DELIVERED
                bag.save()
            except Exception as e:
                raise BagDiscoveryException(
                    "Error sending metadata to {}: {} {}".format(
                        settings.DELIVERY_URL, e))
        return ("All bag data delivered.", bag_ids)

    def deliver_data(self, bag, url):
        r = requests.post(
            url,
            data={
                "bag_data": json.dumps(bag.data),
                "origin": bag.origin,
                "identifier": bag.bag_identifier},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()


class CleanupRoutine:
    """Removes files from the destination directory."""

    def __init__(self, identifier):
        self.identifier = identifier
        if not self.identifier:
            raise CleanupException(
                "No identifier submitted, unable to perform CleanupRoutine.", None)

    def run(self):
        try:
            self.filepath = "{}.tar.gz".format(
                os.path.join(settings.DEST_DIR, self.identifier))
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)
                return ("Transfer removed.", self.identifier)
            return ("Transfer was not found.", self.identifier)
        except Exception as e:
            raise CleanupException(e, self.identifier)
