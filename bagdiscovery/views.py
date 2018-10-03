import urllib.request
from django.shortcuts import render
from django.views.generic import TemplateView
# from .forms import URLForm
from .library import *
import magic


class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):

        if request.method == 'POST':

            # receive POST, parse for name
            print("recieved POST")
            parsejson(request)
            print("Bag store process has finished")

        else:
            print("This was not a POST")

        return render(request, template_name="bagdiscovery/index.html")


class bagView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "bagdiscovery/bagView.html"
        rows = getbags()
        return render(request, template_name, {'rows': rows})