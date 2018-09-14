import urllib.request
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm
from .library import *
import magic


class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):
        # Write byte stream to file on local system
        # writeFileToTemp(request)

        print(checkForBag())

        # Check that file for its type even if it doesnt have an extension (Currently checks static file)
        fileType = magic.from_file('storage/testss', mime=True)
        print("The file type was " + fileType)
        # This is the post from the form on the page
        if request.method == 'POST':
            receiveBag(request)
            print(searchForBag())
        # This is from a POST request. Use fileType to determine if file is a zip.
        elif fileType == "application/zip":
            # creates a zipfile object from the bytestream and prints it out in the console
            createZip(request.body)
        else:
            print("This was not a zip and should be worked on")
            # receiveBag(request)

        return render(request, template_name="bagdiscovery/index.html")


class bagView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "bagdiscovery/bagView.html"
        rows = getBags()
        return render(request, template_name, {'rows': rows})