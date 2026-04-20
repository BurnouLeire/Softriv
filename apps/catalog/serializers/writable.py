# apps/catalog/serializers/writable.py
from rest_framework import serializers
from ..models import (
    Services, Magnitude, TypeService, Instruments, Procedures,
)

class ServiceWritableSerializer(serializers.ModelSerializer):
    # Relaciones corregidas según los nombres en tu modelo Services
    type_service_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeService.objects.filter(active=True),
        source='type_service' # Coincide con models.Services.type_service
    )
    
    instrument_id = serializers.PrimaryKeyRelatedField(
        queryset=Instruments.objects.all(),
        source='instrument', # Coincide con models.Services.instrument
        required=False,
        allow_null=True
    )

    class Meta:
        model = Services
        fields = [
            'code', 
            'name', 
            'active',
            'type_service_id', 
            'instrument_id',
            'precio_base',
            'observaciones_internas'
        ]
    
    def create(self, validated_data):
        #variantes_data = validated_data.pop('variantes', [])
        
        # Crear el servicio
        servicio = Services.objects.create(**validated_data)
        return servicio
    
    def update(self, instance, validated_data):
        #variantes_data = validated_data.pop('variantes', None)
        
        # Actualizar campos del servicio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance