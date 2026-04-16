import os
from io import BytesIO
from django.template.loader import get_template
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from django.conf import settings

def generar_pdf_cotizacion(cotizacion):
    """
    Genera un PDF para la cotización usando xhtml2pdf,
    lo guarda en el campo archivo_pdf de la cotización
    y retorna la URL generada.
    """
    template = get_template('sales/pdf_cotizacion.html')

    # Agrupar los items por grupo, o en 'Sin Grupo' si no lo tienen
    grupos_dict = {}
    
    # Intentar obtener todos los items
    for item in cotizacion.items.select_related('grupo', 'servicio', 'servicio__instrumento'):
        grupo_nombre = item.grupo.nombre if item.grupo else "Detalle de Servicios"
        if grupo_nombre not in grupos_dict:
            grupos_dict[grupo_nombre] = []
        grupos_dict[grupo_nombre].append(item)

    context = {
        'cotizacion': cotizacion,
        'grupos': grupos_dict,
        'LAB_NOMBRE': getattr(settings, 'LAB_NOMBRE', 'LABORATORIO S.A.C.'),
        'LAB_RUC': getattr(settings, 'LAB_RUC', ''),
        'LAB_DIRECCION': getattr(settings, 'LAB_DIRECCION', ''),
        'LAB_TELEFONO': getattr(settings, 'LAB_TELEFONO', ''),
        'LAB_EMAIL': getattr(settings, 'LAB_EMAIL', ''),
    }

    html = template.render(context)
    result = BytesIO()

    # Convertir HTML a PDF
    # pisa.pisaDocument requiere un objeto de archivo para escribir el PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        pdf_content = result.getvalue()
        
        # Eliminar archivo anterior si existe (opcional, django-storages a veces sobrescribe o añade un hash)
        
        # Guardar el archivo en la BD -> se sube a Supabase
        filename = f"COT_{cotizacion.numero}.pdf"
        cotizacion.archivo_pdf.save(filename, ContentFile(pdf_content), save=True)
        return cotizacion.archivo_pdf.url
        
    return None
