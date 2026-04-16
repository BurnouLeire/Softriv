from django.contrib import admin
from .models import (
    TipoServicio, Magnitude, Procedimiento,
    Instrumentos, Servicios, MagnitudePrice
    # VarianteServicio, PrecioVariante, DimensionVariante,
    # TarifaPunto, TarifaRango
)
class MagnitudePriceInline(admin.TabularInline):
    model = MagnitudePrice
    extra = 1

class ServiciosInline(admin.TabularInline):
    model = Servicios
    extra = 1


# class DimensionInline(admin.TabularInline):
#     model = DimensionVariante
#     extra = 1


# class PrecioInline(admin.TabularInline):
#     model = PrecioVariante
#     extra = 1


@admin.register(Magnitude)
class MagnitudeAdmin(admin.ModelAdmin):
    inlines = [MagnitudePriceInline]


admin.site.register(TipoServicio)
admin.site.register(Procedimiento)
admin.site.register(Instrumentos)
admin.site.register(Servicios)
# admin.site.register([, PrecioVariante, DimensionVariante])


# admin.site.register(TarifaPunto)
# admin.site.register(TarifaRango)
