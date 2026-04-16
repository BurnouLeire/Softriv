# sales/management/commands/debug_pdf.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from sales.services.pdf_service import CotizacionPDFService

class Command(BaseCommand):
    help = 'Depura la generación de PDFs de cotizaciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='debug_cotizacion.pdf',
            help='Nombre del archivo PDF de salida'
        )
        parser.add_argument(
            '--data',
            type=str,
            help='Ruta a archivo JSON con datos de prueba'
        )
    
    def handle(self, *args, **options):
        output_file = options['output']
        data_file = options.get('data')
        
        self.stdout.write('🔧 Iniciando depuración de PDF...')
        
        # Cargar datos de prueba
        if data_file and os.path.exists(data_file):
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        else:
            test_data = self.get_test_data()
        
        try:
            # Generar PDF
            pdf_service = CotizacionPDFService(test_data)
            output_path = os.path.join(settings.BASE_DIR, output_file)
            pdf_service.generate_pdf(output_path=output_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ PDF generado exitosamente: {output_path}')
            )
            
            # Mostrar información del archivo
            file_size = os.path.getsize(output_path) / 1024
            self.stdout.write(f'📄 Tamaño: {file_size:.2f} KB')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error generando PDF: {str(e)}')
            )
            raise
    
    def get_test_data(self):
        """Retorna datos de prueba para depuración"""
        return {
            'laboratorio': {
                'nombre': 'LABORATORIO DE CALIBRACIÓN',
                'direccion': 'Av. Principal 123',
                'ruc': '0999999999001',
                'telefono': '04-5018070'
            },
            'cotizacion': {
                'codigo': 'RIV.LC.178.26',
                'fecha': '2026-04-15',
                'estado': 'COTIZADO'
            },
            'cliente': {
                'nombre': 'EMPRESA ABC',
                'ruc': '1799999999001',
                'direccion': 'Principal'
            },
            'grupos': [
                {
                    'nombre': 'CALIBRACIÓN DE PESAS',
                    'items': [
                        {
                            'servicio_nombre': 'Calibración de Peso',
                            'instrumento': 'Peso 20 kg',
                            'cantidad': 2,
                            'precio_unitario': 25.00,
                            'subtotal': 50.00
                        }
                    ]
                }
            ],
            'totales': {
                'subtotal': 300.00,
                'igv': 54.00,
                'total': 354.00
            }
        }