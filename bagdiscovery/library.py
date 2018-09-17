import os
from pathlib import Path
import MySQLdb
import json
from .models import Bag


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