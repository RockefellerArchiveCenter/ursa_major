import json
import os
import shutil
import tarfile
from .models import Bag
from ursa_major import settings


class BagDiscoveryException(Exception): pass


class BagDiscovery:
    def __init__(self, dirs=None):
        if dirs:
            self.landing_dir = dirs['landing']
            self.storage_dir = dirs['storage']
        else:
            self.landing_dir = settings.LANDING_DIR
            self.storage_dir = settings.STORAGE_DIR
        if not os.path.isdir(os.path.join(settings.BASE_DIR, self.storage_dir)):
            os.makedirs(os.path.join(settings.BASE_DIR, self.storage_dir))

    def run(self):
        bags = Bag.objects.filter(bag_path__isnull=True)
        for bag in bags:
            self.bag_name = "{}.tar.gz".format(bag.bag_identifier)

            if os.path.exists(os.path.join(self.landing_dir, self.bag_name)):
                try:
                    self.unpack_bag()
                except Exception as e:
                    raise BagDiscoveryException("Error unpacking bag: {}".format(e))

                try:
                    self.save_bag_data(bag)
                except Exception as e:
                    raise BagDiscoveryException("Error saving bag data: {}".format(e))

                try:
                    self.move_bag(bag)
                except Exception as e:
                    raise BagDiscoveryException("Error moving bag: {}".format(e))
            else:
                continue
        return True

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
        os.rename(
            os.path.join(settings.BASE_DIR, self.landing_dir, bag.bag_identifier, self.bag_name),
            os.path.join(settings.BASE_DIR, new_path))
        bag.bag_path = new_path
        bag.save()
        print("Bag {} has been moved".format(self.bag_name))


def isdatavalid(data):
    requiredKeys = ("extent_files", "url", "acquisition_type", "use_restrictions",
                    "use_restrictions", "extent_size",  "start_date", "end_date",
                    "process_status", "accession_number", "access_restrictions",
                    "rights_statements", "title", "creators", "transfers", "external_identifiers",
                    "organization", "created", "appraisal_note", "description", "resource",
                    "language", "last_modified", "accession_date")

    keylist = data.keys()
    if (set(keylist) - set(requiredKeys)) == set() and (set(requiredKeys) - set(keylist)) == set():
        return True
    else:
        return False
