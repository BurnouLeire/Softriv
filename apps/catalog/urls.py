# apps/catalog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiciosViewSet,
    # VarianteServicioViewSet,
    # PrecioVarianteViewSet,
    # DimensionVarianteViewSet,
    MagnitudViewSet,
    TypeServiceViewSet,
)

router = DefaultRouter()
router.register(r'servicios', ServiciosViewSet, basename='servicios')

router.register(r'magnitudes', MagnitudViewSet, basename='magnitudes')
router.register(r'tipos-servicio', TypeServiceViewSet, basename='tipos-servicio')

urlpatterns = [
    path('', include(router.urls)),
]