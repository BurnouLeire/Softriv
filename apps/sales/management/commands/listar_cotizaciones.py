# apps/sales/management/commands/listar_cotizaciones.py
from django.core.management.base import BaseCommand
from apps.sales.models import Cotizacion

class Command(BaseCommand):
    help = 'Lista todas las cotizaciones disponibles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número máximo de cotizaciones a mostrar'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        
        self.stdout.write('=' * 80)
        self.stdout.write('📋 LISTA DE COTIZACIONES')
        self.stdout.write('=' * 80)
        
        cotizaciones = Cotizacion.objects.all().order_by('-id')[:limit]
        
        if not cotizaciones.exists():
            self.stdout.write(self.style.WARNING('No hay cotizaciones en la base de datos'))
            return
        
        # Calcular total para cada cotización
        self.stdout.write(f"\n{'ID':<5} {'Código':<15} {'Cliente':<30} {'Fecha':<12} {'Estado':<10} {'Items':<8} {'Subtotal':<12}")
        self.stdout.write('-' * 95)
        
        for cot in cotizaciones:
            # Calcular subtotal sumando items
            subtotal = sum(item.subtotal for item in cot.items.all())
            
            self.stdout.write(
                f"{cot.id:<5} "
                f"{cot.numero:<15} "
                f"{cot.cliente.nombre_completo[:28]:<30} "
                f"{cot.fecha.strftime('%Y-%m-%d'):<12} "
                f"{cot.get_estado_display():<10} "
                f"{cot.items.count():<8} "
                f"${subtotal:<11.2f}"
            )
        
        total_cotizaciones = Cotizacion.objects.count()
        self.stdout.write('-' * 95)
        self.stdout.write(f"Total de cotizaciones en BD: {total_cotizaciones}")
        self.stdout.write(f"Mostrando las últimas {min(limit, total_cotizaciones)}")