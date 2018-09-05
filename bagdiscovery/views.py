import io
import json
import urllib.request
import zipfile
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import URLForm, ZIPForm
from .library import receiveBag, storeNewBag, getBags
import gzip


class index(TemplateView):

    template_name = "bagdiscovery/index.html"

    def post(self, request):
        rows = getBags()
        form = URLForm(request.POST)

        # This is the post from the form on the page

        if request.method == 'POST' and form.is_valid():
            myform = form.cleaned_data['endpoint']
            response = urllib.request.urlopen(myform)
            data = str(json.loads(response.read().decode(encoding='UTF-8')))
            storeNewBag(data)

        # This is from a POST request

        else:
            print("-------------------------")
            r = request.body

            zf = zipfile.ZipFile(io.BytesIO(r), "r")

            for x in zf.namelist():
                print(x)
                print(zf.read(x).decode('utf-8'))
                print("-------------------------")

            # for fileinfo in zf.infolist():
            #     print(zf.read(fileinfo).decode('utf-8'))

            # receiveBag(request)

        return render(request, template_name="bagdiscovery/index.html")


class bagView(TemplateView):

    def get(self, request, *args, **kwargs):
        template_name = "bagdiscovery/bagView.html"
        rows = getBags()
        return render(request, template_name, {'rows': rows})