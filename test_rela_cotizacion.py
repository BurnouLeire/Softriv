# test_real_cotizacion.py (crear en la raíz del proyecto)
import os
import sys
import django

# Configurar Django
sys.path.append('D:/dev/fastapi_curso/Simetdjango')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.sales.models import Cotizacion
from apps.sales.services.pdf_service import CotizacionPDFGenerator

def probar_cotizaciones_reales():
    """Prueba generar PDF para cotizaciones reales"""
    
    print("=" * 60)
    print("📄 PROBANDO PDF CON COTIZACIONES REALES")
    print("=" * 60)
    
    # Obtener cotizaciones
    cotizaciones = Cotizacion.objects.all().order_by('-id')[:5]  # Últimas 5
    
    if not cotizaciones.exists():
        print("❌ No hay cotizaciones en la base de datos")
        return
    
    print(f"\n📋 Se encontraron {cotizaciones.count()} cotizaciones:\n")
    
    for idx, cotizacion in enumerate(cotizaciones, 1):
        print(f"{idx}. ID: {cotizacion.id} - Código: {cotizacion.numero} - Cliente: {cotizacion.cliente.nombre_completo}")
    
    # Seleccionar una cotización
    try:
        cotizacion_id = int(input("\n🔢 Ingresa el ID de la cotización para generar PDF: "))
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        
        print(f"\n✅ Cotización seleccionada: {cotizacion.numero}")
        print(f"   Cliente: {cotizacion.cliente.nombre_completo}")
        print(f"   Items: {cotizacion.items.count()}")
        print(f"   Total: ${cotizacion.total:.2f}")
        
        # Generar PDF
        print("\n📝 Generando PDF...")
        generator = CotizacionPDFGenerator(cotizacion)
        pdf_path = generator.generate(output_type='temp')
        
        print(f"\n✅ PDF generado exitosamente!")
        print(f"📁 Ubicación: {pdf_path}")
        print(f"📊 Tamaño: {os.path.getsize(pdf_path) / 1024:.2f} KB")
        
        # Preguntar si quiere abrir el archivo
        abrir = input("\n¿Deseas abrir el PDF? (s/n): ").lower()
        if abrir == 's':
            os.startfile(pdf_path)
            
    except Cotizacion.DoesNotExist:
        print(f"❌ No existe cotización con ID {cotizacion_id}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    probar_cotizaciones_reales()