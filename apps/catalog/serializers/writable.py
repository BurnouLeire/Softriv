# apps/catalog/serializers/writable.py
from rest_framework import serializers
from ..models import (
    Servicios, 
    #VarianteServicio,
    #PrecioVariante,
    #DimensionVariante, 
    Magnitude, TypeService, Instruments, Procedures,
)


# class DimensionWritableSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DimensionVariante
#         fields = ['tipo_dimension', 'valor_entero', 'valor_texto']


class PrecioWritableSerializer(serializers.ModelSerializer):
    vigente_desde = serializers.DateField(required=False)
    vigente_hasta = serializers.DateField(required=False, allow_null=True)
    
    # class Meta:
    #     model = PrecioVariante
    #     fields = ['precio', 'vigente_desde', 'vigente_hasta', 'activo']
    
    def create(self, validated_data):
        # Si no se especifica vigente_desde, usa la fecha actual
        if 'vigente_desde' not in validated_data:
            from datetime import date
            validated_data['vigente_desde'] = date.today()
        return super().create(validated_data)


# class VarianteWritableSerializer(serializers.ModelSerializer):
#     dimensiones = DimensionWritableSerializer(many=True, required=False)
#     precios = PrecioWritableSerializer(many=True, required=False)
#     procedimiento_id = serializers.PrimaryKeyRelatedField(
#         queryset=Procedimiento.objects.all(),
#         source='procedimiento',
#         required=False,
#         allow_null=True
#     )
    
#     class Meta:
#         model = VarianteServicio
#         fields = [
#             'cod_variante', 'descripcion', 'acreditado', 'activo',
#             'procedimiento_id', 'dimensiones', 'precios'
#         ]
    
#     def create(self, validated_data):
#         dimensiones_data = validated_data.pop('dimensiones', [])
#         precios_data = validated_data.pop('precios', [])
        
#         variante = VarianteServicio.objects.create(**validated_data)
        
#         # Crear dimensiones
#         for dim_data in dimensiones_data:
#             DimensionVariante.objects.create(variante=variante, **dim_data)
        
#         # Crear precios
#         for precio_data in precios_data:
#             if 'vigente_desde' not in precio_data:
#                 from datetime import date
#                 precio_data['vigente_desde'] = date.today()
#             PrecioVariante.objects.create(variante=variante, **precio_data)
        
#         return variante


class ServicioWritableSerializer(serializers.ModelSerializer):
    #variantes = VarianteWritableSerializer(many=True, required=False)
    
    # Relaciones
    magnitud_id = serializers.PrimaryKeyRelatedField(   
        queryset=Magnitude.objects.filter(active=True),
        source='magnitud'
    )
    tipo_servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeService.objects.filter(active=True),
        source='tipo_servicio'
    )
    instrumento_id = serializers.PrimaryKeyRelatedField(
        queryset=Instruments.objects.filter(is_measurable=True),
        source='instrumento'
    )
    procedimiento_base_id = serializers.PrimaryKeyRelatedField(
        queryset=Procedures.objects.filter(active=True),
        source='procedimiento_base',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Servicios
        fields = [
            'code', 'name', 'acreditado', 'active',
            'magnitud_id', 'tipo_servicio_id', 'instrumento_id',
            'procedimiento_base_id', 'precio_min', 'precio_max',
            #'variantes'
        ]
    
    def create(self, validated_data):
        #variantes_data = validated_data.pop('variantes', [])
        
        # Crear el servicio
        servicio = Servicios.objects.create(**validated_data)
        
        # # Crear las variantes asociadas
        # for variante_data in variantes_data:
        #     variante_data['servicio'] = servicio
        #     variante_serializer = VarianteWritableSerializer(data=variante_data)
        #     variante_serializer.is_valid(raise_exception=True)
        #     variante_serializer.save()
        
        return servicio
    
    def update(self, instance, validated_data):
        #variantes_data = validated_data.pop('variantes', None)
        
        # Actualizar campos del servicio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # # Si se envían variantes, reemplazar las existentes
        # if variantes_data is not None:
        #     # Eliminar variantes existentes
        #     instance.variantes.all().delete()
            
        #     # Crear nuevas variantes
        #     for variante_data in variantes_data:
        #         variante_data['servicio'] = instance
        #         variante_serializer = VarianteWritableSerializer(data=variante_data)
        #         variante_serializer.is_valid(raise_exception=True)
        #         variante_serializer.save()
        
        return instance