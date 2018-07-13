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


def getBag(request):
    response = requests.get(request.GET.get('endpoint'))
    json_bag = str(response.json())
    storeBag(json_bag)


def storeBag(json_bag):
        db = MySQLdb.connect(user='urmn', db='bag', passwd='aurora', host='db')
        cursor = db.cursor()
        print('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
              + "'" + "Hi" + "' ," + "'" + time.strftime('%Y-%m-%d %H:%M:%S') + "'")

        cursor.execute('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
                       + "'" + time.strftime('%m-%d-%Y') + "' ," + "'" + time.strftime('%I:%M:%S %p') + "')")

        db.commit()
        db.close()
