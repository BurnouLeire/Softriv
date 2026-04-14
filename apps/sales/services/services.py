from apps.work_orders.models import Order, OrderItem

def crear_ot_desde_cotizacion(cotizacion):

    order = Order.objects.create(
        sales=cotizacion,
       # cliente_nombre=cotizacion.cliente.razon_social,
        #cliente_ruc=cotizacion.cliente.ruc,
        #sucursal_nombre=cotizacion.sucursal.nombre,
        code=f"OT-{cotizacion.numero}",
    )

    for item in cotizacion.items.all():
        OrderItem.objects.create(
            order=order,
            servicio_nombre=item.get_descripcion_completa(),
            configuracion=item.configuracion,
            cantidad=item.cantidad,
            notas=item.notas,
        )

    return order
def versionar_ot(cotizacion, ot_anterior):

    nueva_version = ot_anterior.version + 1

    nueva_ot = crear_ot_desde_cotizacion(cotizacion)
    nueva_ot.version = nueva_version
    nueva_ot.reemplaza_a = ot_anterior
    nueva_ot.save()

    return nueva_ot
