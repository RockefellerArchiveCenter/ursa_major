"""ursa_major URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from asterism.views import PingView
from django.contrib import admin
from django.urls import include, re_path
from rest_framework import routers

from bagdiscovery.views import (AccessionViewSet, BagDeliveryView,
                                BagDiscoveryView, BagViewSet,
                                CleanupRoutineView)

router = routers.DefaultRouter()
router.register(r'bags', BagViewSet, 'bag')
router.register(r'accessions', AccessionViewSet, 'accession')


urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path('admin/', admin.site.urls),
    re_path(r'^bagdiscovery/', BagDiscoveryView.as_view(), name="bagdiscovery"),
    re_path(r'^bagdelivery/', BagDeliveryView.as_view(), name="bagdelivery"),
    re_path(r'^cleanup/', CleanupRoutineView.as_view(), name="cleanup"),
    re_path(r'^status/', PingView.as_view(), name="ping"),
]
