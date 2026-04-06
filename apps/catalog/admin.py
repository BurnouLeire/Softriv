from django.contrib import admin
from .models import (
    TipoServicio, Magnitud, Procedimiento,
    Instrumento, CatalogoServicio, VarianteServicio, PrecioVariante, DimensionVariante,
    # TarifaPunto, TarifaRango
)


class CatalogoServicioInline(admin.TabularInline):
    model = CatalogoServicio
    extra = 1


class DimensionInline(admin.TabularInline):
    model = DimensionVariante
    extra = 1


class PrecioInline(admin.TabularInline):
    model = PrecioVariante
    extra = 1


@admin.register(VarianteServicio)
class VarianteServicioAdmin(admin.ModelAdmin):
    inlines = [DimensionInline, PrecioInline]


admin.site.register(TipoServicio)
admin.site.register(Magnitud)
admin.site.register(Procedimiento)
admin.site.register(Instrumento)
admin.site.register(CatalogoServicio)
# admin.site.register([, PrecioVariante, DimensionVariante])


# admin.site.register(TarifaPunto)
# admin.site.register(TarifaRango)
