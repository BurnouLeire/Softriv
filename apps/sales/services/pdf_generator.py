# sales/services/pdf_generator.py
import os
from datetime import date
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone
from weasyprint import HTML, CSS
from decimal import Decimal
import models


class CotizacionPDFService:

    @staticmethod
    def generar_pdf(cotizacion_id):
        """
        Recibe el ID de la cotización y devuelve los Bytes del PDF listos.
        """
        try:
            # Optimización: traer todos los datos relacionados en una sola query
            cotizacion = models.Cotizacion.objects.select_related(
                'cliente',
                'sucursal',
                'vendedor',
                'certificate_customer'
            ).prefetch_related(
                'grupos__items__servicio__instrumento',
                'grupos__items__servicio__tipo_servicio'
            ).get(id=cotizacion_id)

        except models.Cotizacion.DoesNotExist:
            return None

        # 1. Preparar contexto para la plantilla
        context = CotizacionPDFService._preparar_contexto(cotizacion)

        # 2. Renderizar HTML desde Template
        template = get_template('pdf/cotizacion.html')
        html_renderizado = template.render(context)

        # 3. Convertir HTML a Bytes PDF
        css = CSS(string='''
            @page { 
                size: A4; 
                margin: 1.5cm 1cm 2cm 1cm;
                
                @bottom-right {
                    content: "Página " counter(page) " de " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }
                
                @top-left {
                    content: "LABORATORIO DE CALIBRACIÓN";
                    font-size: 8pt;
                    color: #666;
                }
            }
            
            /* Estilos para evitar cortes raros */
            h2, h3, h4 { page-break-after: avoid; }
            table { page-break-inside: avoid; }
            .grupo { page-break-inside: avoid; }
        ''')

        pdf_bytes = HTML(string=html_renderizado).write_pdf(stylesheets=[css])

        return pdf_bytes

    @staticmethod
    def _preparar_contexto(cotizacion):
        """
        Prepara el diccionario de contexto con cálculos adicionales
        """
        # Calcular totales generales
        total_general = Decimal('0.00')
        total_items = 0

        grupos_data = []
        for grupo in cotizacion.grupos.all().order_by('orden'):
            items_grupo = []
            subtotal_grupo = Decimal('0.00')

            for item in grupo.items.all().select_related(
                'servicio__instrumento',
                'servicio__tipo_servicio'
            ):
                subtotal_item = item.cantidad * item.precio_unitario
                subtotal_grupo += subtotal_item

                # Formatear configuración para mostrar en tabla
                config_texto = CotizacionPDFService._formatear_configuracion(
                    item.configuracion)

                items_grupo.append({
                    'servicio_nombre': item.servicio.tipo_servicio.nombre,
                    'instrumento': item.servicio.instrumento.nombre if item.servicio.instrumento else "N/A",
                    'configuracion': config_texto,
                    'marca': item.marca,
                    'modelo': item.modelo,
                    'serie': item.serie,
                    'cantidad': item.cantidad,
                    'precio_unitario': item.precio_unitario,
                    'subtotal': subtotal_item,
                    'notas': item.notas,
                })

            total_general += subtotal_grupo
            total_items += len(items_grupo)

            grupos_data.append({
                'nombre': grupo.nombre,
                'items': items_grupo,
                'subtotal': subtotal_grupo,
                'cantidad_items': len(items_grupo)
            })

        # Datos del cliente certificado (si existe)
        cliente_certificado = None
        if cotizacion.certificate_customer:
            cc = cotizacion.certificate_customer
            cliente_certificado = {
                'nombre': cc.name,
                'ruc': cc.ruc if hasattr(cc, 'ruc') else '',
                'direccion': cc.address if hasattr(cc, 'address') else '',
            }

        return {
            'cotizacion': {
                'codigo': cotizacion.codigo_empresa or cotizacion.numero,
                'numero': cotizacion.numero,
                'fecha': cotizacion.fecha.strftime('%d/%m/%Y'),
                'estado': cotizacion.get_estado_display(),
                'observaciones': cotizacion.observaciones,
            },
            'cliente': {
                'nombre': cotizacion.cliente.name,
                'ruc': getattr(cotizacion.cliente, 'ruc', ''),
                'direccion': cotizacion.sucursal.address if cotizacion.sucursal else '',
                'contacto': getattr(cotizacion.cliente, 'contact_name', ''),
                'telefono': getattr(cotizacion.cliente, 'phone', ''),
                'email': getattr(cotizacion.cliente, 'email', ''),
            },
            'sucursal': {
                'nombre': cotizacion.sucursal.name if cotizacion.sucursal else 'Principal',
                'direccion': cotizacion.sucursal.address if cotizacion.sucursal else '',
            },
            'vendedor': {
                'nombre': cotizacion.vendedor.get_full_name() or cotizacion.vendedor.username,
                'email': cotizacion.vendedor.email,
            },
            'cliente_certificado': cliente_certificado,
            'grupos': grupos_data,
            'totales': {
                'subtotal': total_general,
                'igv': total_general * Decimal('0.18'),  # 18% IGV Perú
                'total': total_general * Decimal('1.18'),
                'total_items': total_items,
            },
            'fecha_generacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
            'laboratorio': {
                'nombre': getattr(settings, 'LAB_NOMBRE', 'LABORATORIO DE CALIBRACIÓN S.A.C.'),
                'ruc': getattr(settings, 'LAB_RUC', '20123456789'),
                'direccion': getattr(settings, 'LAB_DIRECCION', 'Av. Principal 123, Lima - Perú'),
                'telefono': getattr(settings, 'LAB_TELEFONO', '(01) 123-4567'),
                'email': getattr(settings, 'LAB_EMAIL', 'contacto@labcalibracion.com'),
            }
        }

    @staticmethod
    def _formatear_configuracion(configuracion_dict):
        """
        Convierte el JSON de configuración en texto legible
        Ej: {'puntos_temp': 3, 'rango': '0-100°C'} -> "3 puntos, Rango: 0-100°C"
        """
        if not configuracion_dict:
            return ""

        partes = []
        for key, value in configuracion_dict.items():
            # Mapeo de nombres técnicos a legibles
            mapeo_nombres = {
                'puntos_temp': 'puntos temp',
                'puntos_humedad': 'puntos hum',
                'puntos_masa': 'puntos masa',
                'rango': 'rango',
                'unidad': 'unidad',
                'frecuencia': 'frecuencia',
            }
            nombre_legible = mapeo_nombres.get(key, key.replace('_', ' '))

            if isinstance(value, bool):
                partes.append(
                    nombre_legible if value else f"sin {nombre_legible}")
            elif value:
                partes.append(f"{nombre_legible}: {value}")

        return ", ".join(partes) if partes else ""
