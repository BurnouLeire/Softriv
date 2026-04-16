# apps/sales/services/pdf_service.py
import os
import tempfile
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Intentar importar WeasyPrint
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint no está instalado")


class PDFGenerationError(Exception):
    pass


class PDFService:
    def __init__(self):
        if not WEASYPRINT_AVAILABLE:
            raise PDFGenerationError("WeasyPrint no está instalado")
        
        self.font_config = FontConfiguration()
    
    def generar_cotizacion_pdf(self, data, output_type='binary', output_path=None):
        """
        Genera PDF de cotización.
        
        Args:
            data (dict): Datos de la cotización
            output_type (str): 'binary', 'path', o 'temp'
            output_path (str): Ruta específica (solo para output_type='path')
            
        Returns:
            BytesIO or str: PDF generado
        """
        try:
            html_content = self._render_cotizacion_template(data)
            css = CSS(string=self._get_base_css(), font_config=self.font_config)
            
            pdf_file = HTML(string=html_content).write_pdf(
                stylesheets=[css],
                font_config=self.font_config
            )
            
            if output_type == 'binary':
                return BytesIO(pdf_file)
            
            elif output_type == 'path' and output_path:
                # Guardar en ruta específica
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(pdf_file)
                return output_path
            
            elif output_type == 'temp':
                # Guardar en archivo temporal (útil para Windows)
                temp_dir = self._get_temp_directory()
                filename = f"cotizacion_{data.get('codigo', 'temp')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(pdf_file)
                
                logger.info(f"PDF guardado en: {filepath}")
                return filepath
            
            else:
                raise PDFGenerationError(f"output_type '{output_type}' no válido")
                
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise PDFGenerationError(f"Error generando PDF: {str(e)}")
    
    def _get_temp_directory(self):
        """Obtiene un directorio temporal válido en Windows/Linux/Mac"""
        # Priorizar directorio configurado en settings
        if hasattr(settings, 'PDF_TEMP_DIR'):
            temp_dir = settings.PDF_TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            return temp_dir
        
        # Usar directorio temporal del sistema
        temp_dir = tempfile.gettempdir()
        
        # Crear subdirectorio para PDFs
        pdf_temp_dir = os.path.join(temp_dir, 'simet_pdfs')
        os.makedirs(pdf_temp_dir, exist_ok=True)
        
        return pdf_temp_dir
    
    def _render_cotizacion_template(self, data):
        """Renderiza el template HTML"""
        template = get_template('sales/pdf_templates/cotizacion_pdf.html')
        context = self._prepare_context(data)
        return template.render(context)
    
    def _prepare_context(self, data):
        """Prepara el contexto con valores por defecto"""
        laboratorio = {
            'nombre': getattr(settings, 'LABORATORIO_NOMBRE', 'LABORATORIO DE CALIBRACIÓN'),
            'direccion': getattr(settings, 'LABORATORIO_DIRECCION', 'Av. Principal'),
            'ruc': getattr(settings, 'LABORATORIO_RUC', '0999999999001'),
            'telefono': getattr(settings, 'LABORATORIO_TELEFONO', '04-5018070'),
            'email': getattr(settings, 'LABORATORIO_EMAIL', 'laboratorio@empresa.com'),
        }
        
        grupos = data.get('grupos', [])
        if not grupos and data.get('items'):
            grupos = [{
                'nombre': 'SERVICIOS DE CALIBRACIÓN',
                'cantidad_items': len(data.get('items', [])),
                'subtotal': data.get('totales', {}).get('subtotal', 0),
                'items': data.get('items', [])
            }]
        
        for grupo in grupos:
            for item in grupo.get('items', []):
                item.setdefault('marca', '')
                item.setdefault('modelo', '')
                item.setdefault('serie', '')
                item.setdefault('configuracion', '')
                item.setdefault('notas', '')
        
        return {
            'laboratorio': laboratorio,
            'cotizacion': {
                'codigo': data.get('codigo', 'N/A'),
                'numero': data.get('numero', 'N/A'),
                'fecha': data.get('fecha', timezone.now().isoformat()),
                'estado': data.get('estado', 'COTIZADO'),
                'observaciones': data.get('observaciones', ''),
            },
            'cliente': data.get('cliente', {}),
            'sucursal': data.get('sucursal', {'direccion': ''}),
            'vendedor': data.get('vendedor', {'nombre': 'No asignado', 'email': 'N/A'}),
            'grupos': grupos,
            'totales': data.get('totales', {'subtotal': 0, 'igv': 0, 'total': 0}),
            'validez_dias': data.get('validez_dias', 30),
            'forma_pago': data.get('forma_pago', 'Crédito 30 días'),
            'cliente_certificado': data.get('cliente_certificado'),
            'fecha_generacion': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    def _get_base_css(self):
        """Retorna CSS base"""
        return """
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #2c3e50;
            }
            .header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                border-bottom: 2px solid #1a5276;
                padding-bottom: 15px;
            }
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                font-size: 8pt;
                color: #95a5a6;
                text-align: center;
                padding: 8px 0;
                border-top: 1px solid #d5d8dc;
            }
        """


# apps/sales/services/pdf_service.py - Agrega esta clase al final del archivo
# apps/sales/services/pdf_service.py - Actualizar la clase CotizacionPDFGenerator
# apps/sales/services/pdf_service.py - Actualizar la parte de preparación de datos

class CotizacionPDFGenerator:
    """Generador específico para PDFs de cotización desde modelos"""
    
    def __init__(self, cotizacion):
        self.cotizacion = cotizacion
        self.pdf_service = PDFService()
    
    def generate(self, output_type='binary'):
        data = self._prepare_data_from_model()
        return self.pdf_service.generar_cotizacion_pdf(data, output_type)
    
    def _prepare_data_from_model(self):
        """Prepara los datos del modelo para el servicio PDF"""
        # Agrupar items
        grupos = self._agrupar_items()
        
        # Calcular totales
        subtotal = sum(float(g['subtotal']) for g in grupos)
        igv = subtotal * 0.18
        total = subtotal + igv
        
        # Obtener datos del cliente de manera segura
        cliente_data = self._get_cliente_data()
        
        # Obtener datos del vendedor
        vendedor_data = self._get_vendedor_data()
        
        # Datos de sucursal
        sucursal_direccion = getattr(self.cotizacion, 'direccion_entrega', None) or cliente_data.get('direccion', 'N/A')
        
        return {
            'codigo': self.cotizacion.numero,
            'numero': self.cotizacion.numero,
            'fecha': self.cotizacion.fecha.isoformat() if self.cotizacion.fecha else timezone.now().isoformat(),
            'estado': self.cotizacion.get_estado_display(),
            'observaciones': getattr(self.cotizacion, 'observaciones', '') or '',
            'cliente': cliente_data,
            'sucursal': {'direccion': sucursal_direccion},
            'vendedor': vendedor_data,
            'grupos': grupos,
            'totales': {
                'subtotal': subtotal,
                'igv': igv,
                'total': total,
            },
            'validez_dias': 30,
            'forma_pago': 'Crédito 30 días',
            'cliente_certificado': cliente_data if cliente_data.get('nombre') else None,
        }
    
    def _get_cliente_data(self):
        """Obtiene datos del cliente de manera segura"""
        cliente = self.cotizacion.cliente
        
        if not cliente:
            return {
                'nombre': 'N/A',
                'ruc': 'N/A',
                'direccion': 'N/A',
                'contacto': 'N/A',
                'telefono': 'N/A',
                'email': 'N/A',
            }
        
        # Intentar obtener diferentes nombres de campos comunes
        nombre = (
            getattr(cliente, 'nombre_completo', None) or
            getattr(cliente, 'nombre', None) or
            getattr(cliente, 'razon_social', None) or
            getattr(cliente, 'business_name', None) or
            str(cliente)
        )
        
        ruc = (
            getattr(cliente, 'ruc', None) or
            getattr(cliente, 'cedula', None) or
            getattr(cliente, 'identificacion', None) or
            getattr(cliente, 'tax_id', None) or
            'N/A'
        )
        
        direccion = (
            getattr(cliente, 'direccion', None) or
            getattr(cliente, 'address', None) or
            getattr(cliente, 'direccion_completa', None) or
            'N/A'
        )
        
        contacto = (
            getattr(cliente, 'contacto', None) or
            getattr(cliente, 'contact_name', None) or
            getattr(cliente, 'persona_contacto', None) or
            'N/A'
        )
        
        telefono = (
            getattr(cliente, 'telefono', None) or
            getattr(cliente, 'phone', None) or
            getattr(cliente, 'telefono_movil', None) or
            'N/A'
        )
        
        email = (
            getattr(cliente, 'email', None) or
            getattr(cliente, 'correo', None) or
            'N/A'
        )
        
        return {
            'nombre': nombre,
            'ruc': str(ruc),
            'direccion': direccion,
            'contacto': contacto,
            'telefono': telefono,
            'email': email,
        }
    
    def _get_vendedor_data(self):
        """Obtiene datos del vendedor de manera segura"""
        vendedor = self.cotizacion.vendedor
        
        if not vendedor:
            return {
                'nombre': 'No asignado',
                'email': 'N/A',
            }
        
        nombre = (
            getattr(vendedor, 'nombre_completo', None) or
            getattr(vendedor, 'get_full_name', None) and vendedor.get_full_name() or
            getattr(vendedor, 'username', None) or
            getattr(vendedor, 'first_name', '') + ' ' + getattr(vendedor, 'last_name', '') or
            str(vendedor)
        )
        
        email = (
            getattr(vendedor, 'email', None) or
            'N/A'
        )
        
        return {
            'nombre': nombre.strip() or 'No asignado',
            'email': email,
        }
    
    def _agrupar_items(self):
        """Agrupa los items de la cotización"""
        items_pdf = []
        
        for item in self.cotizacion.items.all():
            # Obtener descripción del servicio
            servicio_nombre = (
                getattr(item, 'servicio', None) or
                getattr(item, 'nombre_servicio', None) or
                getattr(item, 'tipo_servicio', None) or
                'Servicio de calibración'
            )
            
            # Obtener descripción del instrumento
            instrumento = (
                getattr(item, 'descripcion', None) or
                getattr(item, 'instrumento', None) or
                getattr(item, 'nombre', None) or
                'Instrumento no especificado'
            )
            
            items_pdf.append({
                'servicio_nombre': servicio_nombre,
                'instrumento': instrumento,
                'cantidad': getattr(item, 'cantidad', 1),
                'precio_unitario': float(getattr(item, 'precio_unitario', 0)),
                'subtotal': float(getattr(item, 'subtotal', 0)),
                'marca': getattr(item, 'marca', ''),
                'modelo': getattr(item, 'modelo', ''),
                'serie': getattr(item, 'serie', ''),
                'configuracion': getattr(item, 'configuracion', ''),
                'notas': getattr(item, 'notas', ''),
            })
        
        subtotal_grupo = sum(float(i['subtotal']) for i in items_pdf)
        
        return [{
            'nombre': 'SERVICIOS DE CALIBRACIÓN',
            'cantidad_items': len(items_pdf),
            'subtotal': subtotal_grupo,
            'items': items_pdf,
        }]