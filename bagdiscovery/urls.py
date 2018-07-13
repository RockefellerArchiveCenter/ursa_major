from django.urls import path
from django.views.generic import TemplateView

from .views import index
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', index.as_view(), name="index"),

]

