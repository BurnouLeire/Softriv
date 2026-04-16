# apps/sales/management/commands/generar_pdf_cotizacion.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.sales.models import Quote
from apps.sales.services.pdf_service import CotizacionPDFGenerator, PDFGenerationError
import os

class Command(BaseCommand):
    help = 'Genera PDF para una cotización existente en la base de datos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'cotizacion_id',
            type=int,
            help='ID de la cotización para generar el PDF'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Ruta específica para guardar el PDF (opcional)'
        )
        parser.add_argument(
            '--open',
            action='store_true',
            help='Abrir la carpeta después de generar el PDF'
        )
    
    def handle(self, *args, **options):
        cotizacion_id = options['cotizacion_id']
        
        self.stdout.write('=' * 60)
        self.stdout.write(f'📄 GENERANDO PDF PARA COTIZACIÓN #{cotizacion_id}')
        self.stdout.write('=' * 60)
        
        try:
            # Obtener la cotización
            cotizacion = Quote.objects.get(id=cotizacion_id)
            
            # Calcular subtotal
            subtotal = sum(item.subtotal for item in cotizacion.items.all())
            
            self.stdout.write(f'✅ Cotización encontrada: {cotizacion.numero}')
            self.stdout.write(f'   Cliente: {cotizacion.cliente.nombre_completo}')
            self.stdout.write(f'   Fecha: {cotizacion.fecha}')
            self.stdout.write(f'   Estado: {cotizacion.get_estado_display()}')
            self.stdout.write(f'   Items: {cotizacion.items.count()}')
            self.stdout.write(f'   Subtotal: ${subtotal:.2f}')
            
            # Generar PDF
            self.stdout.write('\n📝 Generando PDF...')
            
            pdf_generator = CotizacionPDFGenerator(cotizacion)
            
            # Determinar ruta de salida
            output_path = options.get('output')
            if output_path:
                # Usar ruta especificada
                pdf_path = pdf_generator.generate(output_type='path')
                # Mover a la ruta especificada si es diferente
                if pdf_path != output_path:
                    import shutil
                    shutil.move(pdf_path, output_path)
                    pdf_path = output_path
                self.stdout.write(self.style.SUCCESS(f'✅ PDF guardado en: {output_path}'))
            else:
                # Guardar en temporal
                pdf_path = pdf_generator.generate(output_type='temp')
                
                file_size = os.path.getsize(pdf_path) / 1024
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ PDF GENERADO EXITOSAMENTE'))
                self.stdout.write(f'📁 Ubicación: {pdf_path}')
                self.stdout.write(f'📊 Tamaño: {file_size:.2f} KB')
            
            # Abrir carpeta si se solicita
            if options['open']:
                try:
                    folder = os.path.dirname(pdf_path)
                    os.startfile(folder)
                    self.stdout.write(f'\n📂 Se abrió la carpeta que contiene el PDF')
                except Exception as e:
                    self.stdout.write(f'\n⚠️ No se pudo abrir la carpeta: {e}')
            
        except Quote.DoesNotExist:
            raise CommandError(f'No existe una cotización con ID {cotizacion_id}')
        except PDFGenerationError as e:
            raise CommandError(f'Error generando PDF: {e}')
        except Exception as e:
            raise CommandError(f'Error inesperado: {e}')