import MySQLdb
import json
import uuid
import time
from .models import Bag


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)
    storeBag(json_bag)

    return 'Data is in the database!'


def storeBag(json_bag):
    bag = Bag()
    bag.time = time.strftime('%I:%M:%S %p')
    bag.date = time.strftime('%m-%d-%Y')
    bag.bag = json_bag
    bag.id = uuid.uuid4().__str__()

    bag.save()


def storeNewBag(json_bag):
    cleanBag = json_bag
    updatedBag = '"' + cleanBag + '"'

    bag = Bag()
    bag.time = time.strftime('%I:%M:%S %p')
    bag.date = time.strftime('%m-%d-%Y')
    bag.bag = updatedBag
    bag.id = uuid.uuid4().__str__()

    bag.save()


def getBags():
    db = MySQLdb.connect(user='urmn', db='bag', passwd='aurora', host='db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bag.bag")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result
