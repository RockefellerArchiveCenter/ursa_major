import os
from pathlib import Path
import MySQLdb
import json
from .models import Bag
import requests


def storebag(request, nameofbag):
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)

    bag = Bag()
    bag.accessiondata = json_bag
    # bag.urlpath = "storage/" + nameofbag
    bag.urlpath = os.path.abspath("storage/" + nameofbag)
    bag.bagName = nameofbag

    bag.save()


def getbags():
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mysql.bag")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result


def checkforbag(nameofbag):
    my_file = Path("landing/" + nameofbag)
    if my_file.exists():
        return 'true'
    else:
        print("File is not present")


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


def movebag(nameofbag):
    os.rename("landing/" + nameofbag, "storage/" + nameofbag)


def getaccessiondata(nameofbag):
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT accessiondata FROM mysql.bag WHERE bagName = '" + nameofbag + ".zip'")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result


def fornaxpass(accessiondata):
    # defining the Fornax-endpoint
    API_ENDPOINT = ""

    # data to be sent to api
    data = {'accessiondata': accessiondata}

    # sending post request and saving response as response object
    r = requests.post(url=API_ENDPOINT, data=data)

    return r
