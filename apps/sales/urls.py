# apps/sales/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import QuoteViewSet, ItemsViewSet, GenerarPDFCotizacionView, SubItemViewSet

app_name = 'sales'

# Router principal para cotizaciones
router = DefaultRouter()
router.register(r'cotizaciones', QuoteViewSet, basename='cotizacion')
router.register(r'items', ItemsViewSet, basename='items')
router.register(r'subitems', SubItemViewSet, basename='subitem')

# Router anidado para detalles de cotización
cotizacion_router = nested_routers.NestedSimpleRouter(
    router,
    r'cotizaciones',
    lookup='cotizacion'
)
# cotizacion_router.register(
#     r'detalles',
#     ItemsViewSet,
#     basename='cotizacion-detalle'
# )

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cotizacion_router.urls)),
    path('cotizaciones/generar-pdf/', GenerarPDFCotizacionView.as_view(), name='generar-pdf-cotizacion'),
    path('subitems/', SubItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='subitem-list'),
    path('subitems/<int:pk>/', SubItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='subitem-detail'),
]
