# apps/catalog/serializers/base.py
from rest_framework import serializers
from ..models import (
    Services, 
    # VarianteServicio, PrecioVariante,
    # DimensionVariante, 
    Magnitude, TypeService, MagnitudePrice

)

class ServicesSerializer(serializers.ModelSerializer):
    type_service_name = serializers.CharField(source='type_service.name', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    magnitude = serializers.SerializerMethodField()

    class Meta:
        model = Services
        fields = [
            'id',
            'code',
            'name',
            'type_service',
            'type_service_name',
            'instrument',
            'instrument_name',
            'magnitude',
            'precio_base',
            'active',
        ]

    def get_magnitude(self, obj):
        if not obj.instrument:
            return []

        magnitudes = [
            rel.magnitude
            for rel in obj.instrument.magnitudes.all()
            if rel.magnitude
        ]

        return InstrumentMagnitudeSerializer(magnitudes, many=True).data


class MagnitudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magnitude
        fields = '__all__'


class TypeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = '__all__'

class MagnitudePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagnitudePrice
        fields = [
            'id',
            'tag',
            'range_min',
            'range_max',
            'base_price',
            'min_price',
            'max_price',
            'accredited',
            'observation',
            'unit',
        ]

class InstrumentMagnitudeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    prices = serializers.SerializerMethodField()

    def get_prices(self, obj):
        prices = MagnitudePrice.objects.filter(magnitude=obj)
        return MagnitudePriceSerializer(prices, many=True).data