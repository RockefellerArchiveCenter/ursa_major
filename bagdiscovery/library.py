import os
from .models import Bag


class BagProcessor:

    def run(self, bag):
        bag_name = "{}.tar.gz".format(bag.bag_identifier)
        try:
            self.checkforbag(bag_name)
            self.movebag(bag_name)
            return True
        except Exception as e:
            print(e)
            return False

    def checkforbag(self, bag_name):
        bag_path = os.path.join(settings.LANDING_DIR, bag_name)
        if bag_path.exists():
            return True
        else:
            print("Bag {} not present".format(bag_name))
            return False

    def movebag(self, bag_name):
        try:
            os.rename(
                os.path.join(settings.LANDING_DIR, bag_name),
                os.path.join(settings.STORAGE_DIR, bag_name))
            print("Bag {} has been moved".format(bag_name))
            return True
        except Exception as e:
            print(e)
            return False


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
