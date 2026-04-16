# apps/catalog/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Servicios, 
    #VarianteServicio, PrecioVariante,
    #DimensionVariante, 
    Magnitude, TipoServicio, Instrumentos, Procedimiento
)
from .serializers import (
    ServiciosSerializer,
    ServicioWritableSerializer,
    #VarianteSerializer,
    #PrecioSerializer,
    #DimensionSerializer,
    MagnitudeSerializer,
    TipoServicioSerializer,
)


class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.filter(activo=True).prefetch_related(
        'variantes__precios',
        'variantes__dimensiones',
        'magnitud',
        'tipo_servicio',
        'instrumento'
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'nombre', 'magnitud__nombre']
    filterset_fields = ['magnitud', 'tipo_servicio', 'acreditado', 'activo']
    ordering_fields = ['code', 'nombre', 'precio_min', 'precio_max']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServicioWritableSerializer
        return ServiciosSerializer
    
    @action(detail=False, methods=['get'])
    def metadata(self, request):
        """Devuelve los catálogos necesarios para crear servicios"""
        return Response({
            'magnitudes': MagnitudeSerializer(
                Magnitude.objects.filter(activo=True), 
                many=True
            ).data,
            'tipos_servicio': TipoServicioSerializer(
                TipoServicio.objects.filter(activo=True), 
                many=True
            ).data,
            'instrumentos': [
                {
                    'id': i.id, 
                    'nombre': i.nombre, 
                    'magnitud_id': i.magnitud_id,
                    'codigo_base': i.codigo_base
                }
                for i in Instrumentos.objects.all()
            ],
            'procedimientos': [
                {'id': p.id, 'codigo': p.codigo, 'nombre': p.nombre}
                for p in Procedimiento.objects.all()
            ],
            'dimension_config': {
                'TEMPERATURA Y HUMEDAD': {
                    'required_dimensions': ['PUNTOS_TEMP'],
                    'optional_dimensions': ['PUNTOS_HUM', 'ENTORNO', 'INMERSION'],
                    'puntos_temp': {'min': 1, 'max': 10},
                    'puntos_hum': {'min': 1, 'max': 10},
                    'entorno_options': ['ESTUFA', 'AUTOCLAVE', 'BAÑO_MARIA', 'GENERAL'],
                    'inmersion_options': ['TOTAL', 'PARCIAL']
                },
                'PRESIÓN': {
                    'required_dimensions': [],
                    'optional_dimensions': ['SECUENCIA'],
                    'secuencia_options': ['B', 'C']
                },
                'MASA': {
                    'required_dimensions': ['TIPO_INSTRUMENTO'],
                    'optional_dimensions': ['RANGO_MASA', 'CLASE_PESO', 'VALOR_NOMINAL', 'CAPACIDAD'],
                    'tipo_options': ['BALANZA', 'PESA', 'TOLVA', 'TERMOBALANZA'],
                    'clase_options': ['E1', 'E2', 'F1', 'F2', 'M1', 'M2', 'M3']
                },
                'LONGITUD': {
                    'required_dimensions': ['TIPO_INSTRUMENTO'],
                    'optional_dimensions': [],
                    'tipo_options': ['CINTA', 'CINTA_AFORO', 'PIE_DE_REY', 'FLEXOMETRO', 'MICROMETRO', 'RELOJ_COMPARADOR']
                },
                'OTRAS MAGNITUDES': {
                    'required_dimensions': [],
                    'optional_dimensions': ['PUNTOS_TEMP', 'PUNTOS_PH', 'PUNTOS_BRIX', 'PUNTOS_CONDUCTIVIDAD'],
                }
            }
        })
    
    # @action(detail=True, methods=['get'])
    # def variantes(self, request, pk=None):
    #     """Obtiene todas las variantes de un servicio"""
    #     servicio = self.get_object()
    #     variantes = servicio.variantes.filter(activo=True)
    #     serializer = VarianteSerializer(variantes, many=True)
    #     return Response(serializer.data)


# class VarianteServicioViewSet(viewsets.ModelViewSet):
#     queryset = VarianteServicio.objects.filter(activo=True)
#     serializer_class = VarianteSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['servicio', 'acreditado', 'activo']


# class PrecioVarianteViewSet(viewsets.ModelViewSet):
#     queryset = PrecioVariante.objects.filter(activo=True)
#     serializer_class = PrecioSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['variante', 'activo']


# class DimensionVarianteViewSet(viewsets.ModelViewSet):
#     queryset = DimensionVariante.objects.all()
#     serializer_class = DimensionSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['variante', 'tipo_dimension']


class MagnitudViewSet(viewsets.ModelViewSet):
    queryset = Magnitude.objects.filter(activo=True)
    serializer_class = MagnitudeSerializer


class TipoServicioViewSet(viewsets.ModelViewSet):
    queryset = TipoServicio.objects.filter(activo=True)
    serializer_class = TipoServicioSerializer