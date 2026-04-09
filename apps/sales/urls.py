# apps/sales/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import CotizacionViewSet, ItemsViewSet

app_name = 'sales'

# Router principal para cotizaciones
router = DefaultRouter()
router.register(r'cotizaciones', CotizacionViewSet, basename='cotizacion')

# Router anidado para detalles de cotización
cotizacion_router = nested_routers.NestedSimpleRouter(
    router,
    r'cotizaciones',
    lookup='cotizacion'
)
cotizacion_router.register(
    r'detalles',
    ItemsViewSet,
    basename='cotizacion-detalle'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cotizacion_router.urls)),
]
