from rest_framework import serializers
from .models import (
    Servicios, VarianteServicio, PrecioVariante,
    DimensionVariante, Magnitud, TipoServicio
)


class PrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioVariante
        fields = ['precio', 'activo']


class DimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimensionVariante
        fields = ['tipo_dimension', 'valor_entero', 'valor_texto']


class VarianteSerializer(serializers.ModelSerializer):
    # Traemos los precios y dimensiones dentro de la variante
    precios = PrecioSerializer(many=True, read_only=True)
    dimensiones = DimensionSerializer(many=True, read_only=True)
    code_variant = serializers.CharField(source="cod_variante", read_only=True)
    description = serializers.CharField(source="descripcion", read_only=True)
    acredited = serializers.BooleanField(source="acreditado", read_only=True)
    class Meta:
        model = VarianteServicio
        fields = ['id', 'code_variant', 'description',
                  'acredited', 'precios', 'dimensiones']


class ServiciosSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nombre", read_only=True)
    magnitude = serializers.CharField(source="magnitud.nombre", read_only=True)
    service_type = serializers.CharField(source="tipo_servicio.nombre", read_only=True)
    acredited = serializers.CharField(source="acreditado", read_only=True)
    variants = VarianteSerializer(source="variantes", many=True, read_only=True)

    class Meta:
        model = Servicios
        fields = [
            'id',
            'code',
            'name',
            'magnitude',
            'service_type',
            'acredited',
            'activo',
            'variants'
        ]

class MagnitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magnitud
        fields = '__all__'


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = '__all__'