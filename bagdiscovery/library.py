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
