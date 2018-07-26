from django.urls import path
from django.views.generic import TemplateView
from .views import index, bagView
from . import views


urlpatterns = [
    path('', index.as_view(), name="index"),
    path('bag/', bagView.as_view(), name="bagView"),

]

