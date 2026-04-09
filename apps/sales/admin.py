from django.contrib import admin
from .models import Cotizacion, CotizacionItems


class CotizacionDetalleInline(admin.StackedInline):
    """Versión más vertical (cada detalle ocupa más espacio)"""
    model = CotizacionItems
    extra = 1


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha', 'estado']
    inlines = [CotizacionDetalleInline]


@admin.register(CotizacionItems)
class CotizacionDetalleAdmin(admin.ModelAdmin):
    list_display = ['id', 'cotizacion',
                    'servicio', 'cantidad', 'precio_unitario']
    list_select_related = ['cotizacion', 'servicio']  # Optimiza consultas
