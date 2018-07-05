from django.shortcuts import render

# Create your views here.

import MySQLdb
import json
from django.http import HttpResponse
from django.shortcuts import render
import uuid
import datetime
import time



def index(request):
    if request.method == 'POST':
        receiveBag(request)
    return render(request, 'discovery/index.html')


def receiveBag(request):
    now = datetime.datetime.now()
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)
    "Current year: %d" % now.year

    db = MySQLdb.connect(user='username', db='bagrepo', passwd='password', host='localhost')
    cursor = db.cursor()
    print('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
          + "'" + "Hi" + "' ," + "'" + time.strftime('%Y-%m-%d %H:%M:%S') + "'")

    cursor.execute('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' , "
                   + "'" + time.strftime('%m-%d-%Y') + "' ," + "'" + time.strftime('%I:%M:%S') + "')")

    db.commit()
    db.close()

    return 'Data is in the database!'
