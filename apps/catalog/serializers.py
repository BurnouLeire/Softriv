from rest_framework import serializers
from .models import (
    CatalogoServicio, VarianteServicio, PrecioVariante,
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

    class Meta:
        model = VarianteServicio
        fields = ['id', 'cod_variante', 'descripcion',
                  'acreditado', 'precios', 'dimensiones']


class CatalogoServicioSerializer(serializers.ModelSerializer):
    # Expandimos las variantes para que el cotizador tenga todo a la mano
    variantes = VarianteSerializer(many=True, read_only=True)
    magnitud_nombre = serializers.ReadOnlyField(source='magnitud.nombre')
    tipo_servicio_nombre = serializers.ReadOnlyField(
        source='tipo_servicio.nombre')

    class Meta:
        model = CatalogoServicio
        fields = [
            'id', 'cod_facturacion', 'nombre', 'magnitud_nombre',
            'tipo_servicio_nombre', 'acreditado', 'variantes'
        ]
