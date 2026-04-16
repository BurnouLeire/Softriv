# apps/sales/management/commands/test_pdf.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sales.services.pdf_service import PDFService

class Command(BaseCommand):
    help = 'Prueba la generación de PDFs'
    
    def handle(self, *args, **options):
        self.stdout.write('Probando generación de PDF...')
        
        # Datos de prueba
        test_data = {
            'codigo': 'TEST-001',
            'cliente': {
                'nombre': 'Cliente de Prueba',
                'ruc': '0999999999001',
                'direccion': 'Calle Principal 123',
                'contacto': 'Juan Pérez',
                'telefono': '0999999999',
                'email': 'juan@test.com'
            },
            'grupos': [{
                'nombre': 'SERVICIOS DE PRUEBA',
                'items': [{
                    'servicio_nombre': 'Calibración de Prueba',
                    'instrumento': 'Instrumento Test',
                    'cantidad': 1,
                    'precio_unitario': 100.00,
                    'subtotal': 100.00
                }]
            }],
            'totales': {
                'subtotal': 100.00,
                'igv': 18.00,
                'total': 118.00
            }
        }
        
        try:
            pdf_service = PDFService()
            pdf_bytes = pdf_service.generar_cotizacion_pdf(test_data, output_type='binary')
            
            # Guardar para inspección
            with open('test_output.pdf', 'wb') as f:
                f.write(pdf_bytes.getvalue())
            
            self.stdout.write(self.style.SUCCESS('✅ PDF generado exitosamente: test_output.pdf'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))