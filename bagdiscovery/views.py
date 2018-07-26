import json
import urllib.request
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm

from .library import receiveBag, storeNewBag


class index(TemplateView):

    template_name = "discovery/index.html"

    def post(self, request):
        form = URLForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            myform = form.cleaned_data['endpoint']
            response = urllib.request.urlopen(myform)
            data = str(json.loads(response.read().decode(encoding='UTF-8')))
            storeNewBag(data)
        else:
            receiveBag(request)

        return render(request, 'discovery/index.html')
