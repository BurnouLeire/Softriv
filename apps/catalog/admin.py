from django.contrib import admin
from .models import (
    TipoServicio, Magnitud, Procedimiento,
    Instrumento, CatalogoServicio,
    TarifaPunto, TarifaRango
)


class CatalogoServicioInline(admin.TabularInline):
    model = CatalogoServicio
    extra = 1


admin.site.register(TipoServicio)
admin.site.register(Magnitud)
admin.site.register(Procedimiento)
admin.site.register(Instrumento)
admin.site.register(CatalogoServicio)


admin.site.register(TarifaPunto)
admin.site.register(TarifaRango)
