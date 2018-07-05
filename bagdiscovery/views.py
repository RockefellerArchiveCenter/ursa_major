from django.shortcuts import render

# Create your views here.

import MySQLdb
import json
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    if request.method == 'POST':
        print(receiveBag(request))
    return render(request, 'discovery/index.html')


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    json_bag = json.dumps(json_data)
    db = MySQLdb.connect(user='username', db='dbname', passwd='password', host='localhost')
    cursor = db.cursor()
    cursor.execute('INSERT INTO t1 VALUES (' + " ' " + json_bag + " ' " + ')')
    db.commit()
    db.close()

    return 'Data is in the database!'
