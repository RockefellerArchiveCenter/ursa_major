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
from django.contrib import admin
from django.conf.urls import url
from django.urls import include
from bagdiscovery.views import AccessionViewSet, BagViewSet, BagDiscoveryView, BagDeliveryView, CleanupRoutineView
from rest_framework import routers
from rest_framework.schemas import get_schema_view

router = routers.DefaultRouter()
router.register(r'bags', BagViewSet, 'bag')
router.register(r'accessions', AccessionViewSet, 'accession')

schema_view = get_schema_view(
  title="Ursa Major API",
  description="Endpoints for Ursa Major microservice application.",
)


urlpatterns = [
    url(r'^', include(router.urls)),
    url('admin/', admin.site.urls),
    url(r'^bagdiscovery/', BagDiscoveryView.as_view(), name="bagdiscovery"),
    url(r'^bagdelivery/', BagDeliveryView.as_view(), name="bagdelivery"),
    url(r'^cleanup/', CleanupRoutineView.as_view(), name="cleanup"),
    url(r'^status/', include('health_check.api.urls')),
    url(r'^schema/', schema_view, name='schema'),
]
