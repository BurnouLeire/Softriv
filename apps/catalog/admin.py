from django.contrib import admin
from .models import (
    TypeService, Magnitude, Procedures,
    Instruments, Servicios, MagnitudePrice, InstrumentMagnitudes, ProceduresMagnitudes
    # VarianteServicio, PrecioVariante, DimensionVariante,
    # TarifaPunto, TarifaRango
)

class MagnitudePriceInline(admin.TabularInline):
    model = MagnitudePrice
    extra = 1

class ServiciosInline(admin.TabularInline):
    model = Servicios
    extra = 1
class InstrumentMagnitudesInline(admin.TabularInline):
    model = InstrumentMagnitudes
    extra = 1

class ProceduresMagnitudesInline(admin.TabularInline):
    model = ProceduresMagnitudes
@admin.register(Magnitude)
class MagnitudeAdmin(admin.ModelAdmin):
    inlines = [MagnitudePriceInline]

@admin.register(Procedures)
class ProceduresAdmin(admin.ModelAdmin):
    inlines = [ProceduresMagnitudesInline]

@admin.register(Instruments)
class InstrumentsAdmin(admin.ModelAdmin):
    inlines = [InstrumentMagnitudesInline]

admin.site.register(TypeService)
admin.site.register(Servicios)
# admin.site.register([, PrecioVariante, DimensionVariante])

