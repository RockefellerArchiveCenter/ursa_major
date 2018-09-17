import urllib.request
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm
from .library import *
import magic


class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):

        if request.method == 'POST':

            # receive POST, parse for name
            print(parseJSON(request))
            nameOfBag = parseJSON(request)

            # check if bag with same name is in landing directory,
            if (checkForBag(nameOfBag)) == 'true':
                # if true move to storage directory
                moveBag(nameOfBag)
                # Then store name, accession data, and path in database.
                storeBag(request, nameOfBag)

                # Get accession data and POST to fornax. Need to move this from the view.
                print(getAccessionData())
                accessiondata = getAccessionData()
                fornaxPass(accessiondata)

        else:
            print("This was not a POST")

        return render(request, template_name="bagdiscovery/index.html")


class bagView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "bagdiscovery/bagView.html"
        rows = getBags()
        return render(request, template_name, {'rows': rows})