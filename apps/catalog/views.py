from rest_framework import viewsets
from .models import Servicios
from .serializers import ServiciosSerializer


class CatalogoViewSet(viewsets.ReadOnlyModelViewSet):
    # Optimizamos con select_related y prefetch_related para que no sea lento
    queryset = Servicios.objects.filter(activo=True).select_related(
        'magnitud', 'tipo_servicio'
    ).prefetch_related(
        'variantes__precios',
        'variantes__dimensiones'
    )
    serializer_class = ServiciosSerializer
