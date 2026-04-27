# apps/catalog/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Services, 
    Magnitude,
    TypeService, 
    TypeInstruments, 
    Procedures
)
from .serializers import (
    ServicesSerializer,
    ServiceWritableSerializer,
    MagnitudeSerializer,
    TypeServiceSerializer,
)


class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all().prefetch_related(
        'type_service',
        'instrument__magnitudes__magnitude'
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name', 'instrument__magnitudes__magnitude__nombre']
    filterset_fields = {
        'instrument__magnitudes__magnitude': ['exact'],
        'type_service': ['exact'],
        'active': ['exact'],
    }
    ordering_fields = ['code', 'name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceWritableSerializer
        return ServicesSerializer
    
    @action(detail=False, methods=['get'])
    def metadata(self, request):
        """Devuelve los catálogos necesarios para crear servicios"""
        return Response({
            'magnitudes': MagnitudeSerializer(
                Magnitude.objects.filter(active=True), 
                many=True
            ).data,
            'type_services': TypeServiceSerializer(
                TypeService.objects.filter(active=True), 
                many=True
            ).data,
            'instruments': [
                {
                    'id': i.id, 
                    'name': i.name, 
                    'code': i.code
                }
                for i in TypeInstruments.objects.all()
            ],
            'procedimientos': [
                {'id': p.id, 'codigo': p.code, 'nombre': p.name}
                for p in Procedures.objects.all()
            ],
            
        })

class MagnitudeViewSet(viewsets.ModelViewSet):
    queryset = Magnitude.objects.filter(active=True)
    serializer_class = MagnitudeSerializer


class TypeServiceViewSet(viewsets.ModelViewSet):
    queryset = TypeService.objects.filter(requires_instrument=True)
    serializer_class = TypeServiceSerializer