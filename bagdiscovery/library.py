import os
from pathlib import Path
import MySQLdb
import json
from .models import Bag
import requests


def storeBag(request, nameOfBag):
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)

    bag = Bag()
    bag.accessiondata = json_bag
    # bag.urlpath = "storage/" + nameOfBag
    bag.urlpath = os.path.abspath("storage/" + nameOfBag)
    bag.bagName = nameOfBag

    bag.save()


def getBags():
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mysql.bag")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result


def checkForBag(nameOfBag):
    my_file = Path("landing/" + nameOfBag)
    if my_file.exists():
        return 'true'
    else:
        print("File is not present")


def parseJSON(request):
    json_data = json.loads(request.body.decode(encoding='UTF-8'))

    # print json_data['transfers']
    for each in json_data['transfers']:
        name = each['identifier'] + ".tar.gz"
        print(name)
        if (checkForBag(name)) == 'true':
            # if true move to storage directory
            moveBag(name)
            # Then store name, accession data, and path in database.
            storeBag(request, name)

        # print(name)
    # name = json_data['transfers'][0]['identifier']
    # name2 = json_data['transfers'][1]['identifier']
    # print('The name of the bag is ' + name)
    # return name + " " + name2


def moveBag(nameOfBag):
    os.rename("landing/" + nameOfBag, "storage/" + nameOfBag)


def getAccessionData(nameOfBag):
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT accessiondata FROM mysql.bag WHERE bagName = '" + nameOfBag + ".zip'")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result


def fornaxPass(accessiondata):
    # defining the Fornax-endpoint
    API_ENDPOINT = ""

    # data to be sent to api
    data = {'accessiondata': accessiondata}

    # sending post request and saving response as response object
    r = requests.post(url=API_ENDPOINT, data=data)

    return r
