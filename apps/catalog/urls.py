# apps/catalog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicesViewSet,
    MagnitudeViewSet,
    TypeServiceViewSet,
)

router = DefaultRouter()
router.register(r'servicios', ServicesViewSet, basename='servicios')
router.register(r'magnitudes', MagnitudeViewSet, basename='magnitudes')
router.register(r'tipos-servicio', TypeServiceViewSet, basename='tipos-servicio')

urlpatterns = [
    path('', include(router.urls)),
]