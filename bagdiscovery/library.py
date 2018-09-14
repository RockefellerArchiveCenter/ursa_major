import io
import os
import zipfile
from pathlib import Path
import MySQLdb
import json
from .models import Bag
import magic


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)
    storeBag(json_bag)

    return 'Data is in the database!'


def storeBag(json_bag):
    bag = Bag()
    bag.accessiondata = json_bag
    bag.urlpath = "example"

    bag.save()


def getBags():
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mysql.bag")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result


def searchForBag():
    db = MySQLdb.connect(user='root', db='mysql', passwd='example', host='ursa_major_db')
    cursor = db.cursor()
    cursor.execute("SELECT urlpath FROM mysql.bag")
    result = cursor.fetchall()

    db.commit()
    db.close()

    return result

# writes zip file to directory called storage
def writeFileToTemp(request):
    r = request.body
    print(type(r))

    f = open('landing/testss', 'wb')
    f.write(r)
    f.close()
    return f

def createZip(r):
    zf = zipfile.ZipFile(io.BytesIO(r), "r")

    for x in zf.namelist():
            print("----------------------")
            print(x)
            if "zip" or "tar" not in x:
                print(zf.read(x).decode('utf-8'))
                print("----------------------")
            else:
                print("This is a compressed file and its insides are gummy")
                print("----------------------")

def checkForBag():
    my_file = Path("landing/testss")
    if my_file.exists():
        print("File is right here bby")
        moveBag()
        path = (os.path.dirname(os.path.abspath("storage/testss")))
        print(path)
    return "the file has been moved!"


def moveBag():
    os.rename("landing/testss", "storage/testss")


