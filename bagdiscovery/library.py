import os
import json
from .models import Bag
import requests


def process_bag(bag):
    bag_name = "{}.tar.gz"format(bag.bag_identifier)
    try:
        checkforbag(bag_name)
        movebag(bag_name)
        return True
    except Exception as e:
        print(e)
        return False


def storebag(request, nameofbag):
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)

    bag = Bag()
    bag.accessiondata = json_bag
    # bag.urlpath = "storage/" + nameofbag
    bag.urlpath = os.path.abspath("storage/" + nameofbag)
    bag.bagName = nameofbag

    bag.save()


def checkforbag(bag_name):
    bag_path = os.path.join(settings.LANDING_DIR, bag_name)
    if bag_path.exists():
        return True
    else:
        print("Bag {} not present".format(bag_name))
        return False


def parsejson(request):
    json_data = json.loads(request.body.decode(encoding='UTF-8'))

    # print json_data['transfers']
    for each in json_data['transfers']:
        name = each['identifier'] + ".tar.gz"
        print(name)
        if (checkforbag(name)) == 'true':
            # if true move to storage directory
            movebag(name)
            # Then store name, accession data, and path in database.
            storebag(request, name)


def movebag(bag_name):
    try:
        os.rename(
            os.path.join(settings.LANDING_DIR, bag_name),
            os.path.join(settings.STORAGE_DIR, bag_name))
        print("Bag {} has been moved".format(bag_name))
        return True
    except Exception as e:
        print(e)
        return False


def fornaxpass(accessiondata):
    # defining the Fornax-endpoint
    API_ENDPOINT = ""

    # data to be sent to api
    data = {'accessiondata': accessiondata}

    # sending post request and saving response as response object
    r = requests.post(url=API_ENDPOINT, data=data)

    return r
