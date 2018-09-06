import io
import json
import urllib.request
import zipfile
from pathlib import Path
import os
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm, ZIPForm
from .library import *
import gzip
import magic

class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):
        rows = getBags()
        form = URLForm(request.POST)

        # Write byte stream to file on local system
        writeFileToTemp(request)

        # Check that file for its type even if it doesnt have an extension
        fileType = magic.from_file('test', mime=True)
        print("The file type was " + fileType)

        # This is the post from the form on the page

        if request.method == 'POST' and form.is_valid():
            myform = form.cleaned_data['endpoint']
            response = urllib.request.urlopen(myform)
            data = str(json.loads(response.read().decode(encoding='UTF-8')))
            storeNewBag(data)

        # This is from a POST request. Use fileType to determine if file is a zip.

        elif fileType == "application/zip":
            # creates a zipfile object from the bytesteam and prints it out in the console
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