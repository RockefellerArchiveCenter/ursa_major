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
    bag.urlpath = "storage/" + nameOfBag
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
    name = json_data['name']
    print('The name of the bag is ' + name)
    return name + ".zip"


def moveBag(nameOfBag):
    os.rename("landing/" + nameOfBag, "storage/" + nameOfBag)


def getAccessionData():
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT accessiondata FROM mysql.bag WHERE bagName = 'test.zip'")
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
