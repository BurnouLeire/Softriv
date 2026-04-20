# apps/sales/serializers.py
from rest_framework import serializers
from .models import Quote, Items, QuoteGroup
from django.db import transaction

class ItemsSerializer(serializers.ModelSerializer):
    """Serializer para los items de cotización"""

    servicio_id = serializers.IntegerField(
        source='servicio.id', read_only=True)
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)
    instrumento_nombre = serializers.SerializerMethodField()
    magnitud_nombre = serializers.CharField(
        source='servicio.magnitud.nombre', read_only=True)

    class Meta:
        model = Items
        fields = [
            'id',
            'servicio_id',
            'servicio_nombre',
            'instrumento_nombre',
            'magnitud_nombre',
            'configuracion',
            'cantidad',
            'precio_unitario',
            'marca',
            'modelo',
            'serie',
            'notas',
            'subtotal',
        ]
        read_only_fields = ['subtotal']

    def get_instrumento_nombre(self, obj):
        return obj.instrumento_nombre


class ItemsCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar items"""
    servicio_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Items
        fields = [
            'id',
            'servicio_id',
            'configuracion',
            'cantidad',
            'precio_unitario',
            'marca',
            'modelo',
            'serie',
            'notas',
        ]

    def validate_servicio_id(self, value):
        from apps.catalog.models import CatalogoServicio
        if not CatalogoServicio.objects.filter(id=value, activo=True).exists():
            raise serializers.ValidationError(
                "El servicio no existe o está inactivo")
        return value


class CotizacionSerializer(serializers.ModelSerializer):
    """Serializer completo de cotización (con items anidados)"""
    items = ItemsSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(
        source='cliente.nombre_completo', read_only=True)
    vendedor_nombre = serializers.CharField(
        source='vendedor.get_full_name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            'id',
            'numero',
            'codigo_empresa',
            'cliente_id',
            'cliente_nombre',
            'sucursal_id',
            'vendedor_id',
            'vendedor_nombre',
            'fecha',
            'estado',
            'observaciones',
            'items',
            'subtotal',
            'archivo_pdf',
        ]

    def get_subtotal(self, obj):
        """Calcula el subtotal sin IVA"""
        return sum(item.subtotal for item in obj.items.all())


class CotizacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear cotización con items"""
    items = ItemsCreateSerializer(many=True)

    class Meta:
        model = Quote
        fields = [
            'cliente_id',
            'sucursal_id',
            'observaciones',
            'items',
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un item")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        request = self.context.get('request')
        vendedor = request.user if request and request.user.is_authenticated else None

        with transaction.atomic():

            cotizacion = Quote.objects.create(
                cliente_id=validated_data['cliente_id'],
                sucursal_id=validated_data.get('sucursal_id'),
                vendedor=vendedor,
                observaciones=validated_data.get('observaciones', ''),
                estado=Quote.Estado.BORRADOR
            )

            # 🔥 Crear grupo GENERAL
            grupo_general = QuoteGroup.objects.create(
                cotizacion=cotizacion,
                nombre="GENERAL",
                orden=0
            )

            # Crear items dentro del grupo
            for item_data in items_data:
                servicio_id = item_data.pop('servicio_id')

                Items.objects.create(
                    grupo=grupo_general,
                    servicio_id=servicio_id,
                    **item_data
                )

        return cotizacion


class CotizacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados - SIN IVA"""
    cliente_nombre = serializers.CharField(
        source='cliente.nombre_completo', read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            'id',
            'numero',
            'codigo_empresa',
            'cliente_id',
            'cliente_nombre',
            'fecha',
            'estado',
            'observaciones',
            'total_items',
            'subtotal',
            'archivo_pdf',
        ]

    def get_total_items(self, obj):
        return obj.items.count()

    def get_subtotal(self, obj):
        """Solo el subtotal, sin IVA"""
        return sum(item.subtotal for item in obj.items.all())
