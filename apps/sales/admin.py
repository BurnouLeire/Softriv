# apps/sales/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Cotizacion, Items, GrupoCotizacion

User = get_user_model()


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 1
    fields = ['grupo', 'servicio', 'cantidad', 'precio_unitario']


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha', 'estado']
    inlines = [ItemsInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'vendedor':
            # Asumiendo que tienes un grupo "Vendedores" o un campo is_vendedor
            kwargs['queryset'] = User.objects.filter(groups__name='Vendedor')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Ocultar GrupoCotizacion del menú
admin.site.register(GrupoCotizacion)
admin.site._registry[GrupoCotizacion].has_module_permission = lambda request: False
