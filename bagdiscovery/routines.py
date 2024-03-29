import json
import os
import shutil

import rac_schema_validator
import requests
from asterism.file_helpers import (copy_file_or_dir, move_file_or_dir,
                                   tar_extract_all)

from ursa_major import settings

from .helpers import validate_bag_data
from .models import Bag


class BagDiscoveryException(Exception):
    pass


class CleanupException(Exception):
    pass


class BaseRoutine(object):
    """Base routine which contains main run method."""

    def run(self):
        if not Bag.objects.filter(process_status=self.in_process_status).exists():
            bag = Bag.objects.filter(process_status=self.start_status).first()
            if bag:
                bag.process_status = self.in_process_status
                bag.save()
                try:
                    message = self.process_bag(bag)
                except Exception as e:
                    bag.process_status = self.start_status
                    bag.save()
                    raise Exception(str(e), bag.bag_identifier)
                bag.process_status = self.end_status
                bag.save()
            else:
                message = self.idle_message
        else:
            message = "Service currently running"
            bag = None
        return (message, [bag.bag_identifier] if bag else None)

    def process_bag(self, bag):
        raise NotImplementedError("You must implement a process_bag method")


class BagDiscovery(BaseRoutine):
    """Discovers and stores bags, and delivers data to another service."""
    start_status = Bag.CREATED
    in_process_status = Bag.DISCOVERING
    end_status = Bag.DISCOVERED
    idle_message = "No bags to discover."

    def __init__(self):
        self.src_dir = settings.SRC_DIR
        self.tmp_dir = settings.TMP_DIR
        self.dest_dir = settings.DEST_DIR
        self.derivative_creation_dir = settings.DERIVATIVE_CREATION_DIR
        for dir in [os.path.join(settings.BASE_DIR, self.src_dir),
                    os.path.join(settings.BASE_DIR, self.tmp_dir),
                    os.path.join(settings.BASE_DIR, self.dest_dir),
                    os.path.join(settings.BASE_DIR, self.derivative_creation_dir)]:
            if not os.path.isdir(dir):
                raise BagDiscoveryException("Directory does not exist", dir)
        for dir in [os.path.join(settings.BASE_DIR, self.dest_dir), os.path.join(
                settings.BASE_DIR, self.tmp_dir)]:
            if not os.access(dir, os.W_OK):
                raise BagDiscoveryException("Directory not writable", dir)

    def process_bag(self, bag):
        self.bag_name = "{}.tar.gz".format(bag.bag_identifier)
        if os.path.exists(os.path.join(self.src_dir, self.bag_name)):
            self.unpack_bag()
            self.save_bag_data(bag)
            self.move_bag(bag)
            return "All bags discovered."
        else:
            raise Exception("Bag file does not exist.")

    def unpack_bag(self):
        extracted = tar_extract_all(
            os.path.join(self.src_dir, self.bag_name), self.tmp_dir)
        if not extracted:
            raise BagDiscoveryException("Error unpacking bag.", self.bag_name)

    def save_bag_data(self, bag):
        try:
            with open(os.path.join(
                    self.tmp_dir, bag.bag_identifier,
                    "{}.json".format(bag.bag_identifier))) as json_file:
                bag_data = json.load(json_file)
                validate_bag_data(bag_data, "{}_bag.json".format(bag_data.get("origin", "aurora")))
                bag.data = bag_data
                bag.save()
        except rac_schema_validator.exceptions.ValidationError as e:
            raise BagDiscoveryException(
                "Invalid bag data: {}".format(e), bag.bag_identifier)
        except Exception as e:
            raise BagDiscoveryException(
                "Error saving bag data: {}".format(e),
                bag.bag_identifier)

    def move_bag(self, bag):
        try:
            current_path = os.path.join(
                settings.BASE_DIR, self.tmp_dir, bag.bag_identifier,
                self.bag_name)
            if bag.origin == "digitization":
                derivative_path = os.path.join(settings.DERIVATIVE_CREATION_DIR, self.bag_name)
                if os.path.exists(derivative_path):
                    raise BagDiscoveryException(f"Error copying bag: {derivative_path} exists", bag.bag_identifier)
                else:
                    copy_file_or_dir(current_path, derivative_path)
            new_path = os.path.join(self.dest_dir, self.bag_name)
            moved = move_file_or_dir(current_path, new_path)
            if moved:
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


class BagDelivery(BaseRoutine):
    start_status = Bag.DISCOVERED
    in_process_status = Bag.DELIVERING
    end_status = Bag.DELIVERED
    idle_message = "No bags to deliver."

    def process_bag(self, bag):
        self.deliver_data(bag, settings.DELIVERY_URL)
        if bag.origin == "digitization":
            self.deliver_data(bag, settings.DERIVATIVE_DELIVERY_URL)
        return "All bag data delivered."

    def deliver_data(self, bag, url):
        try:
            r = requests.post(
                url,
                json={
                    "bag_data": bag.data,
                    "origin": bag.origin,
                    "identifier": bag.bag_identifier},
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.text:
                raise Exception(r.text)
            else:
                raise e


class CleanupRoutine:
    """Removes files from the destination directory. Also removes files
    from the source directory if a bag's origin is not Aurora."""

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
                bag = Bag.objects.get(bag_identifier=self.identifier)
                if bag.origin != "aurora":
                    os.remove("{}.tar.gz".format(os.path.join(settings.SRC_DIR, self.identifier)))
                return ("Transfer removed.", self.identifier)
            return ("Transfer was not found.", self.identifier)
        except Exception as e:
            raise CleanupException(e, self.identifier)
