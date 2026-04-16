# apps/sales/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Quote, Items, GrupoCotizacion

User = get_user_model()


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 1


@admin.register(GrupoCotizacion)
class GrupoCotizacionAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]


class GrupoInline(admin.TabularInline):
    model = GrupoCotizacion
    extra = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    inlines = [GrupoInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'vendedor':
            # Asumiendo que tienes un grupo "Vendedores" o un campo is_vendedor
            kwargs['queryset'] = User.objects.filter(groups__name='Vendedor')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# # Ocultar GrupoCotizacion del menú
# admin.site.register(GrupoCotizacion)
admin.site.register(Items)
# admin.site._registry[GrupoCotizacion].has_module_permission = lambda request: False
