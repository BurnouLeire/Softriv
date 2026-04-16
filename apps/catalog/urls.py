# apps/catalog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiciosViewSet,
    # VarianteServicioViewSet,
    # PrecioVarianteViewSet,
    # DimensionVarianteViewSet,
    MagnitudViewSet,
    TipoServicioViewSet,
)

router = DefaultRouter()
router.register(r'servicios', ServiciosViewSet, basename='servicios')
#router.register(r'variantes', VarianteServicioViewSet, basename='variantes')
#router.register(r'precios', PrecioVarianteViewSet, basename='precios')
#router.register(r'dimensiones', DimensionVarianteViewSet, basename='dimensiones')
router.register(r'magnitudes', MagnitudViewSet, basename='magnitudes')
router.register(r'tipos-servicio', TipoServicioViewSet, basename='tipos-servicio')

urlpatterns = [
    path('', include(router.urls)),
]