# apps/sales/management/commands/test_pdf_gen.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    help = 'Prueba la generación de PDF de cotizaciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Ruta específica para guardar el PDF'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('🔧 PROBANDO GENERACIÓN DE PDF')
        self.stdout.write('=' * 60)
        
        # Verificar WeasyPrint
        try:
            import weasyprint
            self.stdout.write(self.style.SUCCESS('✅ WeasyPrint instalado'))
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ WeasyPrint NO instalado'))
            return
        
        # Importar servicio
        try:
            from apps.sales.services.pdf_service import PDFService
            self.stdout.write(self.style.SUCCESS('✅ Servicio PDF importado'))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            return
        
        # Datos de prueba
        test_data = {
            'codigo': 'TEST-001',
            'fecha': timezone.now().isoformat(),
            'cliente': {
                'nombre': 'EMPRESA DE PRUEBA',
                'ruc': '0999999999001',
                'direccion': 'Calle Principal 123',
                'contacto': 'Juan Pérez',
                'telefono': '0999999999',
                'email': 'test@test.com'
            },
            'vendedor': {
                'nombre': 'María González',
                'email': 'maria@empresa.com'
            },
            'grupos': [
                {
                    'nombre': 'CALIBRACIÓN DE PESAS',
                    'cantidad_items': 2,
                    'subtotal': 50.00,
                    'items': [
                        {
                            'servicio_nombre': 'Calibración de Peso',
                            'instrumento': 'Peso 20 kg',
                            'cantidad': 2,
                            'precio_unitario': 25.00,
                            'subtotal': 50.00,
                            'marca': 'OIML',
                            'modelo': 'M1-20',
                            'serie': 'P-20001'
                        }
                    ]
                }
            ],
            'totales': {
                'subtotal': 50.00,
                'igv': 9.00,
                'total': 59.00
            }
        }
        
        # Generar PDF
        try:
            self.stdout.write('📄 Generando PDF...')
            pdf_service = PDFService()
            
            # Determinar ruta de salida
            output_path = options.get('output')
            if output_path:
                # Usar ruta especificada
                pdf_service.generar_cotizacion_pdf(
                    test_data, 
                    output_type='path',
                    output_path=output_path
                )
                self.stdout.write(self.style.SUCCESS(f'✅ PDF guardado en: {output_path}'))
            else:
                # Guardar en temporal y mostrar ruta
                filepath = pdf_service.generar_cotizacion_pdf(
                    test_data, 
                    output_type='temp'
                )
                
                file_size = os.path.getsize(filepath) / 1024
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ PDF GENERADO EXITOSAMENTE'))
                self.stdout.write(f'📁 Ubicación: {filepath}')
                self.stdout.write(f'📊 Tamaño: {file_size:.2f} KB')
                
                # Intentar abrir la carpeta en Windows
                try:
                    folder = os.path.dirname(filepath)
                    os.startfile(folder)
                    self.stdout.write(f'\n📂 Se abrió la carpeta que contiene el PDF')
                except:
                    pass
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()