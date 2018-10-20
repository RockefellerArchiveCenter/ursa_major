import os
from ursa_major import settings


class BagProcessor:
    def __init__(self, dirs=None):
        if dirs:
            self.landing_dir = dirs['landing']
            self.storage_dir = dirs['storage']
        else:
            self.landing_dir = settings.LANDING_DIR
            self.storage_dir = settings.STORAGE_DIR

    def run(self, bag):
        self.bag = bag
        self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
        if self.checkforbag():
            return self.movebag()

    def checkforbag(self):
        if os.path.exists(os.path.join(self.landing_dir, self.bag_name)):
            return True
        else:
            print("Bag {} not present".format(self.bag_name))
            return False

    def movebag(self):
        if not os.path.isdir(os.path.join(settings.BASE_DIR, self.storage_dir)):
            os.makedirs(os.path.join(settings.BASE_DIR, self.storage_dir))
        try:
            new_path = os.path.join(self.storage_dir, self.bag_name)
            os.rename(
                os.path.join(settings.BASE_DIR, self.landing_dir, self.bag_name),
                os.path.join(settings.BASE_DIR, new_path))
            self.bag.bag_path = new_path
            print("Bag {} has been moved".format(self.bag_name))
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
