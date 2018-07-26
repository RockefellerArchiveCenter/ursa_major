import MySQLdb
import json
import uuid
import time
import requests


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)
    storeBag(json_bag)

    return 'Data is in the database!'


def storeBag(json_bag):
        db = MySQLdb.connect(user='urmn', db='bag', passwd='aurora', host='db')
        cursor = db.cursor()
        print('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
              + "'" + "Hi" + "' ," + "'" + time.strftime('%Y-%m-%d %H:%M:%S') + "'")

        cursor.execute('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
                       + "'" + time.strftime('%m-%d-%Y') + "' ," + "'" + time.strftime('%I:%M:%S %p') + "')")

        db.commit()
        db.close()


def storeNewBag(json_bag):
    db = MySQLdb.connect(user='urmn', db='bag', passwd='aurora', host='db')
    cursor = db.cursor()
    cleanBag = json_bag
    print(cleanBag)
    updatedBag = '"' + cleanBag + '"'
    print(updatedBag)
    print('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , " " " + updatedBag + " " " , "
          + "'" + time.strftime('%m-%d-%Y') + "' ," + "'" + time.strftime('%I:%M:%S %p') + "')")

    cursor.execute('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , " " " + updatedBag + " " " , "
                   + "'" + time.strftime('%m-%d-%Y') + "' ," + "'" + time.strftime('%I:%M:%S %p') + "')")

    db.commit()
    db.close()
