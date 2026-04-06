# from decimal import Decimal
# from .models import CatalogoServicio, TarifaPunto, TarifaRango


# def calcular_precio_servicio(servicio, opciones, acreditado):

#     precio_total = Decimal('0')
#     desglose = []
#     partes_desc = [servicio.nombre]

#     # RANGO
#     if 'rango' in opciones:
#         tarifa = TarifaRango.objects.get(
#             servicio=servicio,
#             codigo_rango=opciones['rango'],
#             acreditado=acreditado
#         )
#         precio_total += tarifa.precio
#         desglose.append({"concepto": tarifa.label, "precio": tarifa.precio})
#         partes_desc.append(tarifa.label)

#     # PUNTOS
#     for tipo_eje, num_punto in opciones.items():
#         if tipo_eje == 'rango':
#             continue

#         tarifa = TarifaPunto.objects.get(
#             servicio=servicio,
#             tipo_eje=tipo_eje,
#             num_punto=num_punto,
#             acreditado=acreditado
#         )

#         precio_total += tarifa.precio
#         partes_desc.append(f"{num_punto} puntos {tipo_eje}")

#     # FIJO
#     if not opciones:
#         precio_total = servicio.precio_base or Decimal('0')

#     return {
#         "precio": precio_total,
#         "descripcion": " | ".join(partes_desc),
#         "desglose": desglose
#     }
