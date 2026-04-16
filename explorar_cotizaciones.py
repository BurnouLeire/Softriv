# explorar_cotizaciones.py (crear en la raíz del proyecto)
import os
import sys
import django

# Configurar Django
sys.path.append('D:/dev/fastapi_curso/Simetdjango')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.sales.models import Cotizacion

def explorar_cotizaciones():
    """Explora las cotizaciones y muestra sus campos"""
    
    print("=" * 70)
    print("🔍 EXPLORANDO COTIZACIONES EN LA BASE DE DATOS")
    print("=" * 70)
    
    # Obtener todas las cotizaciones
    cotizaciones = Cotizacion.objects.all()
    
    if not cotizaciones.exists():
        print("❌ No hay cotizaciones en la base de datos")
        return
    
    print(f"\n📊 Total de cotizaciones: {cotizaciones.count()}\n")
    
    # Mostrar estructura del modelo
    primera = cotizaciones.first()
    print("📌 Campos del modelo Cotizacion:")
    for field in primera._meta.fields:
        print(f"   - {field.name}: {field.get_internal_type()}")
    
    print("\n" + "-" * 70)
    print(f"{'ID':<5} {'Código':<15} {'Cliente':<30} {'Items':<8} {'Estado':<12}")
    print("-" * 70)
    
    for cot in cotizaciones:
        items_count = cot.items.count()
        print(
            f"{cot.id:<5} "
            f"{cot.numero:<15} "
            f"{cot.cliente.nombre_completo[:28]:<30} "
            f"{items_count:<8} "
            f"{cot.get_estado_display():<12}"
        )
    
    print("-" * 70)
    
    # Preguntar si quiere ver detalles de alguna
    try:
        id_input = input("\n🔢 Ingresa un ID para ver detalles (o Enter para salir): ").strip()
        if id_input:
            cot = Cotizacion.objects.get(id=int(id_input))
            print(f"\n📋 DETALLES DE COTIZACIÓN #{cot.id}")
            print(f"   Código: {cot.numero}")
            print(f"   Cliente: {cot.cliente.nombre_completo}")
            print(f"   RUC: {cot.cliente.ruc}")
            print(f"   Dirección: {cot.cliente.direccion}")
            print(f"   Fecha: {cot.fecha}")
            print(f"   Estado: {cot.get_estado_display()}")
            print(f"   Items: {cot.items.count()}")
            
            # Mostrar items
            if cot.items.exists():
                print("\n   📦 ITEMS:")
                for idx, item in enumerate(cot.items.all(), 1):
                    print(f"      {idx}. {item.descripcion or 'Sin descripción'}")
                    print(f"         Cantidad: {item.cantidad}")
                    print(f"         Precio unitario: ${item.precio_unitario}")
                    print(f"         Subtotal: ${item.subtotal}")
            else:
                print("\n   ⚠️ Esta cotización no tiene items")
            
            # Preguntar si generar PDF
            generar = input("\n📄 ¿Generar PDF para esta cotización? (s/n): ").lower()
            if generar == 's':
                from apps.sales.services.pdf_service import CotizacionPDFGenerator
                generator = CotizacionPDFGenerator(cot)
                pdf_path = generator.generate(output_type='temp')
                print(f"\n✅ PDF generado: {pdf_path}")
                
                abrir = input("¿Abrir PDF? (s/n): ").lower()
                if abrir == 's':
                    os.startfile(pdf_path)
                    
    except Cotizacion.DoesNotExist:
        print(f"❌ No existe cotización con ese ID")
    except ValueError:
        print("❌ ID inválido")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explorar_cotizaciones()