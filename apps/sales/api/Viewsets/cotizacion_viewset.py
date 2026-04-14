# sales/api/viewsets/cotizacion_viewset.py
import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sales.models import Cotizacion  # CORREGIDO: import relativo correcto
from sales.serializers import CotizacionSerializer  # CORREGIDO: ruta correcta
from sales.services.pdf_generator import CotizacionPDFService
from sales.services.supabase_storage import SupabaseStorageService

logger = logging.getLogger(__name__)


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer

    @action(detail=True, methods=['post'], url_path='generar-pdf')
    def generar_pdf_supabase(self, request, pk=None):
        """
        POST /api/sales/cotizaciones/15/generar-pdf/
        Genera PDF y lo sube a Supabase Storage
        """
        try:
            cotizacion = self.get_object()

            # 1. Generar PDF
            logger.info(f"Generando PDF para cotización {cotizacion.id}")
            pdf_bytes = CotizacionPDFService.generar_pdf(cotizacion.id)

            if not pdf_bytes:
                logger.error("PDF generado está vacío")
                return Response(
                    {"error": "No se pudo generar el PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"PDF generado: {len(pdf_bytes)} bytes")

            # 2. Subir a Supabase
            codigo = cotizacion.codigo_empresa or cotizacion.numero
            nombre_archivo = f"COT-{codigo.replace('/', '-')}"

            logger.info(f"Subiendo PDF a Supabase: {nombre_archivo}")
            url_pdf = SupabaseStorageService.subir_pdf(
                pdf_bytes,
                nombre_archivo,
                bucket='test-public'
            )

            logger.info(f"PDF subido exitosamente: {url_pdf}")

            # 3. Responder (sin guardar en modelo si el campo no existe)
            return Response({
                "mensaje": "PDF generado y subido exitosamente",
                "url_pdf": url_pdf,
                "cotizacion_id": cotizacion.id,
                "codigo": codigo,
                "tamano_bytes": len(pdf_bytes)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Error en generar_pdf_supabase: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
