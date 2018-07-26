import json
import urllib.request
from django.http import HttpResponse, request
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from .forms import URLForm

from .library import receiveBag , storeNewBag


class index(TemplateView):

    template_name = "discovery/index.html"

    def post(self, request):
        form = URLForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            myform = form.cleaned_data['endpoint']
            # print(myform)

            response = urllib.request.urlopen(myform)
            data = str(json.loads(response.read().decode(encoding='UTF-8')))
            # data = str(json.loads(response.read().decode()))
            print("This is the data     !     " + data)

            storeNewBag(data)

        else:
            receiveBag(request)

        return render(request, 'discovery/index.html')
