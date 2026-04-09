# apps/sales/admin.py
from django.contrib import admin
from .models import Cotizacion, Items, GrupoCotizacion


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 1
    fields = ['grupo', 'servicio', 'cantidad', 'precio_unitario']


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha', 'estado']
    inlines = [ItemsInline]


# Esto oculta GrupoCotizacion del menú principal
admin.site.register(GrupoCotizacion)
admin.site._registry[GrupoCotizacion].has_module_permission = lambda request: False
