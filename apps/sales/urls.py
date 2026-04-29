# apps/sales/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    QuoteViewSet, 
    ItemsViewSet, 
    GenerarPDFCotizacionView, 
    SubItemViewSet,
    QuoteGroupViewSet  # Ya lo tienes importado
)

app_name = 'sales'

# ============================================
# ROUTER PRINCIPAL
# ============================================
router = DefaultRouter()
router.register(r'cotizaciones', QuoteViewSet, basename='cotizacion')
router.register(r'items', ItemsViewSet, basename='items')
router.register(r'subitems', SubItemViewSet, basename='subitem')

# ============================================
# ROUTER ANIDADO: Grupos dentro de Cotizaciones
# ============================================
# Ejemplo: /api/cotizaciones/5/grupos/
cotizacion_router = nested_routers.NestedSimpleRouter(
    router,
    r'cotizaciones',
    lookup='cotizacion'
)
cotizacion_router.register(
    r'grupos',  # Nombre en español para la URL
    QuoteGroupViewSet,
    basename='cotizacion-grupos'
)

# ============================================
# ROUTER ANIDADO: Items dentro de Grupos
# ============================================
# Ejemplo: /api/cotizaciones/5/grupos/2/items/
grupo_router = nested_routers.NestedSimpleRouter(
    cotizacion_router,
    r'grupos',
    lookup='grupo'
)
grupo_router.register(
    r'items',
    ItemsViewSet,
    basename='grupo-items'
)

# ============================================
# ROUTER ANIDADO: SubItems dentro de Items
# ============================================
# Ejemplo: /api/cotizaciones/5/grupos/2/items/3/subitems/
item_router = nested_routers.NestedSimpleRouter(
    grupo_router,
    r'items',
    lookup='item'
)
item_router.register(
    r'subitems',
    SubItemViewSet,
    basename='item-subitems'
)

# ============================================
# URLS FINALES
# ============================================
urlpatterns = [
    # Routers principales
    path('', include(router.urls)),
    
    # Routers anidados
    path('', include(cotizacion_router.urls)),
    path('', include(grupo_router.urls)),
    path('', include(item_router.urls)),
    
    # Endpoints especiales
    path(
        'cotizaciones/generar-pdf/', 
        GenerarPDFCotizacionView.as_view(), 
        name='generar-pdf-cotizacion'
    ),
]