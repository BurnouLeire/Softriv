# apps/sales/tests/test_pdf_service.py (nota: tests con 's')
import os
import json
import tempfile
from django.test import TestCase
from django.conf import settings

# CORREGIR LA IMPORTACIÓN - usar la ruta completa
from apps.sales.services.pdf_service import PDFService, PDFGenerationError

class PDFServiceTestCase(TestCase):
    """Pruebas para el servicio de generación de PDFs"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Cargar datos del fixture si existe
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'datos_prueba.json')
        
        if os.path.exists(fixture_path):
            with open(fixture_path, 'r', encoding='utf-8') as f:
                self.test_data = json.load(f)
        else:
            # Datos por defecto
            self.test_data = self._get_default_test_data()
    
    def _get_default_test_data(self):
        """Retorna datos de prueba por defecto"""
        return {
            'codigo': 'TEST-001',
            'numero': '001',
            'fecha': '2026-04-15',
            'cliente': {
                'nombre': 'EMPRESA TEST',
                'ruc': '1799999999001',
                'direccion': 'Calle Test 123',
                'contacto': 'Juan Pérez',
                'telefono': '0999999999',
                'email': 'test@test.com'
            },
            'vendedor': {
                'nombre': 'Vendedor Test',
                'email': 'vendedor@test.com'
            },
            'grupos': [
                {
                    'nombre': 'SERVICIOS DE CALIBRACIÓN',
                    'cantidad_items': 1,
                    'subtotal': 100.00,
                    'items': [
                        {
                            'servicio_nombre': 'Calibración de Peso',
                            'instrumento': 'Peso 20 kg',
                            'cantidad': 2,
                            'precio_unitario': 50.00,
                            'subtotal': 100.00,
                            'marca': 'OIML',
                            'modelo': 'M1',
                            'serie': '12345'
                        }
                    ]
                }
            ],
            'totales': {
                'subtotal': 100.00,
                'igv': 18.00,
                'total': 118.00
            },
            'observaciones': 'Prueba de generación de PDF'
        }
    
    def test_pdf_generation(self):
        """Prueba básica de generación de PDF"""
        try:
            pdf_service = PDFService()
            pdf_bytes = pdf_service.generar_cotizacion_pdf(
                self.test_data,
                output_type='binary'
            )
            
            # Verificar que se generó contenido
            self.assertIsNotNone(pdf_bytes)
            self.assertGreater(len(pdf_bytes.getvalue()), 0)
            
            print("✅ PDF generado exitosamente")
            
        except PDFGenerationError as e:
            # Si WeasyPrint no está instalado, saltamos la prueba
            self.skipTest(f"WeasyPrint no está disponible: {e}")
        except Exception as e:
            self.fail(f"Error inesperado: {e}")
    
    def test_pdf_save_to_file(self):
        """Prueba guardar PDF a archivo"""
        try:
            pdf_service = PDFService()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                filepath = pdf_service.generar_cotizacion_pdf(
                    self.test_data,
                    output_type='path'
                )
                
                self.assertTrue(os.path.exists(filepath))
                self.assertGreater(os.path.getsize(filepath), 0)
                
                print(f"✅ PDF guardado en: {filepath}")
                
                # Limpiar
                os.unlink(filepath)
                
        except PDFGenerationError as e:
            self.skipTest(f"WeasyPrint no está disponible: {e}")