# apps/catalog/serializers/base.py
from rest_framework import serializers
from ..models import (
    Services, 
    # VarianteServicio, PrecioVariante,
    # DimensionVariante, 
    Magnitude, TypeService
)

class ServicesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nombre", read_only=True)
    magnitude = serializers.CharField(source="magnitud.nombre", read_only=True)
    service_type = serializers.CharField(source="tipo_servicio.nombre", read_only=True)
    instrumento_nombre = serializers.CharField(source="instrumento.nombre", read_only=True)

    class Meta:
        model = Services
        fields = [
            'id',
            'code',
            'name',
            'magnitude',
            'service_type',
            'instrumento_nombre',
        ]


class MagnitudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magnitude
        fields = '__all__'


class TypeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = '__all__'