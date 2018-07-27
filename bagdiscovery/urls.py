from django.urls import path
from .views import index, bagView


urlpatterns = [
    path('', index.as_view(), name="index"),
    path('bag/', bagView.as_view(), name="bagView"),

]

