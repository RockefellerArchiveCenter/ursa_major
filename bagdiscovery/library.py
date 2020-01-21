import json
import jsonschema
import os
import requests
import shutil
import tarfile

from .models import Bag
from ursa_major import settings


class BagDiscoveryException(Exception): pass
class CleanupException(Exception): pass


def validate_data(data):
    with open(os.path.join(settings.BASE_DIR, settings.SCHEMA_PATH), "r") as jf:
        schema = json.load(jf)
        jsonschema.validate(instance=data, schema=schema)


class BagDiscovery:
    """Discovers and stores bags, and delivers data to another service."""
    def __init__(self, url, dirs=None):
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
        bags = Bag.objects.filter(bag_path__isnull=True)
        bag_ids = []
        for bag in bags:
            self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
            if os.path.exists(os.path.join(self.src_dir, self.bag_name)):
                self.unpack_bag()
                self.save_bag_data(bag)
                self.move_bag(bag)
                if self.url:
                    self.deliver_data(bag, self.url)
                bag_ids.append(bag.bag_identifier)
            else:
                continue
        return ("All bags discovered and stored.", bag_ids)

    def unpack_bag(self):
        try:
            tf = tarfile.open(os.path.join(self.src_dir, self.bag_name), 'r')
            tf.extractall(os.path.join(self.tmp_dir))
            tf.close()
        except Exception as e:
            raise BagDiscoveryException("Error unpacking bag: {}".format(e), bag.bag_identifier)

    def save_bag_data(self, bag):
        try:
            with open(os.path.join(self.tmp_dir, bag.bag_identifier, "{}.json".format(bag.bag_identifier))) as json_file:
                bag_data = json.load(json_file)
                validate_data(bag_data)
                bag.data = bag_data
                bag.save()
        except jsonschema.exceptions.ValidationError as e:
            raise BagDiscoveryException("Invalid bag data: {}: {}".format(list(e.path), e.message))
        except Exception as e:
            raise BagDiscoveryException("Error saving bag data: {}".format(e), bag.bag_identifier)

    def move_bag(self, bag):
        try:
            new_path = os.path.join(self.dest_dir, self.bag_name)
            shutil.move(
                os.path.join(settings.BASE_DIR, self.tmp_dir, bag.bag_identifier, self.bag_name),
                os.path.join(settings.BASE_DIR, new_path))
            bag.bag_path = new_path
            bag.save()
            shutil.rmtree(os.path.join(settings.BASE_DIR, self.tmp_dir, bag.bag_identifier))
        except Exception as e:
            raise BagDiscoveryException("Error moving bag: {}".format(e), bag.bag_identifier)

    def deliver_data(self, bag, url):
        r = requests.post(
            url,
            data=json.dumps(bag.data),
            headers={"Content-Type": "application/json"},
        )
        if r.status_code != 200:
            raise BagDiscoveryException("Error sending metadata to {}: {} {}".format(url, r.status_code, r.reason))
        return True


class CleanupRoutine:
    """Removes files from the destination directory."""
    def __init__(self, identifier, dirs):
        self.identifier = identifier
        self.dest_dir = dirs['dest'] if dirs else settings.DEST_DIR
        if not self.identifier:
            raise CleanupException("No identifier submitted, unable to perform CleanupRoutine.", None)

    def run(self):
        try:
            self.filepath = "{}.tar.gz".format(os.path.join(self.dest_dir, self.identifier))
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)
                return ("Transfer removed.", self.identifier)
            return ("Transfer was not found.", self.identifier)
        except Exception as e:
            raise CleanupException(e, self.identifier)
