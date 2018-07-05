from django.shortcuts import render

# Create your views here.

import MySQLdb
import json
from django.http import HttpResponse
from django.shortcuts import render
import uuid


def index(request):
    if request.method == 'POST':
        # print(receiveBag(request))
        # print(uuid.uuid4())

        json_data = json.loads(request.body.decode(encoding='UTF-8'))
        json_bag = json.dumps(json_data)

        # print('INSERT INTO bag VALUES (' + " ' " + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' "
        #                + ')')

        db = MySQLdb.connect(user='username', db='bagrepo', passwd='password', host='localhost')
        cursor = db.cursor()
        cursor.execute('INSERT INTO bag VALUES (' + " '" + uuid.uuid4().__str__() + " ' , '[" + json_bag + "]' "
                       + ')')
        db.commit()
        db.close()

    return render(request, 'discovery/index.html')


def receiveBag(request):
    print("I have received a POST request!")

    return 'Data is in the database!'
