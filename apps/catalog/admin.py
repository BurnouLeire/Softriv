from django.contrib import admin
from .models import (
    TypeService,
    Magnitude,
    Procedures,
    Instruments,
    Services,
    MagnitudePrice,
    InstrumentMagnitudes,
    ProceduresMagnitudes,
    Units
   
)

class MagnitudePriceInline(admin.TabularInline):
    model = MagnitudePrice
    extra = 1

class ServicesInline(admin.TabularInline):
    model = Services
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
admin.site.register(Services)
admin.site.register(Units)

