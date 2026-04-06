from django.contrib import admin
from .models import (
    CotizDetalle, Cotizacion,
    # TarifaPunto, TarifaRango
)
admin.site.register(Cotizacion)
admin.site.register(CotizDetalle)
