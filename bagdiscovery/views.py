import urllib.request
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm
from .library import *
import magic


class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):

        # This is the post from the form on the page
        if request.method == 'POST':

            print(parseJSON(request))
            nameOfBag = parseJSON(request)

            if (checkForBag(nameOfBag)) == 'true':
                moveBag(nameOfBag)
                storeBag(request, nameOfBag)

        else:
            print("This was not a POST")

        return render(request, template_name="bagdiscovery/index.html")


class bagView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "bagdiscovery/bagView.html"
        rows = getBags()
        return render(request, template_name, {'rows': rows})