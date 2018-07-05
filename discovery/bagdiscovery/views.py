from django.shortcuts import render

# Create your views here.

import json
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    if request.method == 'POST':
        print("This is a POST request")
        receiveBag(request)
    return render(request, 'discovery/index.html')


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    return json.dumps(json_data, indent=4, sort_keys=True)
