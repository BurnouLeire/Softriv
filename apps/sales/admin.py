# apps/sales/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Quote, Items,  QuoteGroup

User = get_user_model()


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 1


@admin.register(QuoteGroup)
class QuoteGroupAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]


class QuoteGroupInline(admin.TabularInline):
    model = QuoteGroup
    extra = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    inlines = [QuoteGroupInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'vendedor':
            kwargs['queryset'] = User.objects.filter(groups__name='Vendedor')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# # Ocultar GrupoCotizacion del menú
# admin.site.register(GrupoCotizacion)
admin.site.register(Items)
# admin.site._registry[GrupoCotizacion].has_module_permission = lambda request: False
