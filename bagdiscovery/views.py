from django.http import HttpResponse, request
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from .library import receiveBag, getBag

#
# class index(View):
#
#     def get(self, request):
#         getBag(request)
#         return render(request, 'discovery/index.html')
#
#     def post(self, request):
#         receiveBag(request)
#         return render(request, 'discovery/index.html')


class index(TemplateView):

    template_name = "discovery/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    # def get(self, request):
    #     getBag(request)
    #     return render(request, 'discovery/index.html')

    def post(self, request):
        receiveBag(request)
        return render(request, 'discovery/index.html')
