# apps/sales/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import APIView, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .services.services import crear_ot_desde_cotizacion
from .services.pdf_service import PDFService, PDFGenerationError  # 👈 NUEVO

from .models import Cotizacion, Items
from .serializers import (
    CotizacionSerializer,
    CotizacionListSerializer,
    CotizacionCreateSerializer,
    ItemsSerializer,
    ItemsCreateSerializer,
)


class CotizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cotizaciones.
    """

    def get_queryset(self):
        queryset = Cotizacion.objects.prefetch_related(
            'items', 'cliente', 'vendedor')

        # Filtros por query params
        cliente_id = self.request.query_params.get('cliente_id')
        estado = self.request.query_params.get('estado')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        search = self.request.query_params.get('search')

        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        if estado:
            queryset = queryset.filter(estado=estado.upper())

        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)

        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(cliente__nombre_completo__icontains=search) |
                Q(codigo_empresa__icontains=search)
            )

        return queryset.order_by('-fecha', '-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return CotizacionListSerializer
        elif self.action == 'create':
            return CotizacionCreateSerializer
        return CotizacionSerializer

    def create(self, request, *args, **kwargs):
        """Crear una nueva cotización"""
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        cotizacion = serializer.save()

        output_serializer = CotizacionSerializer(cotizacion)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        """Cambiar estado a ENVIADA"""
        cotizacion = self.get_object()

        if cotizacion.estado != Cotizacion.Estado.BORRADOR:
            return Response(
                {'error': 'Solo se pueden enviar cotizaciones en estado BORRADOR'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cotizacion.estado = Cotizacion.Estado.ENVIADA
        cotizacion.save()
        return Response(CotizacionSerializer(cotizacion).data)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Cambiar estado a APROBADA"""
        cotizacion = self.get_object()

        if cotizacion.estado != Cotizacion.Estado.ENVIADA:
            return Response(
                {'error': 'Solo se pueden aprobar cotizaciones enviadas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cotizacion.estado = Cotizacion.Estado.APROBADA
        cotizacion.save()
        order = crear_ot_desde_cotizacion(cotizacion)
        return Response({
            "cotizacion": CotizacionSerializer(cotizacion).data,
            "order_id": order.id
        }, status=status.HTTP_200_OK)

    
    

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Cambiar estado a RECHAZADA"""
        cotizacion = self.get_object()
        cotizacion.estado = Cotizacion.Estado.RECHAZADA
        cotizacion.save()
        return Response(CotizacionSerializer(cotizacion).data)
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        Generar PDF de la cotización.
        
        GET /api/cotizaciones/{id}/pdf/
        Query params opcionales:
            - download=true → Forzar descarga (attachment)
            - preview=true → Vista previa en navegador
        """
        from .services.pdf_service import CotizacionPDFGenerator, PDFGenerationError
        
        cotizacion = self.get_object()
        
        # Verificar que la cotización tenga datos mínimos
        if not cotizacion.cliente:
            return Response(
                {'error': 'La cotización no tiene un cliente asignado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar el generador específico
            pdf_generator = CotizacionPDFGenerator(cotizacion)
            pdf_bytes = pdf_generator.generate(output_type='binary')
            
            # Determinar si es descarga o vista previa
            download = request.query_params.get('download', 'false').lower() == 'true'
            preview = request.query_params.get('preview', 'false').lower() == 'true'
            
            if preview:
                disposition = 'inline'
            elif download:
                disposition = 'attachment'
            else:
                disposition = 'inline'  # Por defecto, vista previa
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'{disposition}; filename="cotizacion_{cotizacion.numero}.pdf"'
            
            return response
            
        except PDFGenerationError as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error inesperado generando PDF para cotización {cotizacion.id}: {str(e)}")
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """
        Generar PDF de una cotización existente.
        
        GET /api/sales/cotizaciones/{id}/generar_pdf/
        """
        from .services.pdf_service import CotizacionPDFGenerator, PDFGenerationError
        
        cotizacion = self.get_object()
        
        try:
            # Generar PDF desde el modelo
            pdf_generator = CotizacionPDFGenerator(cotizacion)
            pdf_bytes = pdf_generator.generate(output_type='binary')
            
            # Determinar si es descarga o vista previa
            download = request.query_params.get('download', 'false').lower() == 'true'
            
            if download:
                disposition = 'attachment'
                filename = f"cotizacion_{cotizacion.numero}_{timezone.now().strftime('%Y%m%d')}.pdf"
            else:
                disposition = 'inline'
                filename = f"cotizacion_{cotizacion.numero}.pdf"
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
            
            return response
            
        except PDFGenerationError as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    


class ItemsViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar items de cotización
    """
    serializer_class = ItemsSerializer

    def get_queryset(self):
        cotizacion_id = self.kwargs.get('cotizacion_pk')
        return Items.objects.filter(cotizacion_id=cotizacion_id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ItemsCreateSerializer
        return ItemsSerializer

    def create(self, request, cotizacion_pk=None):
        """Agregar un item a una cotización existente"""
        cotizacion = get_object_or_404(
            Cotizacion,
            id=cotizacion_pk,
            estado=Cotizacion.Estado.BORRADOR
        )

        serializer = ItemsCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = Items.objects.create(
            cotizacion=cotizacion,
            **serializer.validated_data
        )

        return Response(
            ItemsSerializer(item).data,
            status=status.HTTP_201_CREATED
        )
        




class AprobarCotizacionView(APIView):

    def post(self, request, pk):
        cotizacion = Cotizacion.objects.get(pk=pk)

        cotizacion.estado = 'APROBADA'
        cotizacion.save()

        crear_ot_desde_cotizacion(cotizacion)

        return Response({"ok": True})

# Agrega esto al final de tu views.py, fuera del ViewSet

class GenerarPDFCotizacionView(APIView):
    """
    Vista para generar PDF de cotización desde datos JSON.
    Útil para pruebas o para generación sin modelo existente.
    """
    
    def post(self, request):
        """
        POST /api/cotizaciones/generar-pdf/
        Body: JSON con los datos de la cotización
        """
        try:
            data = request.data
            
            # Validar datos mínimos
            if not data.get('cliente'):
                return Response(
                    {'error': 'Se requiere información del cliente'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pdf_service = PDFService()
            pdf_bytes = pdf_service.generar_cotizacion_pdf(
                data,
                output_type='binary'
            )
            
            # Determinar si es descarga
            download = request.query_params.get('download', 'false').lower() == 'true'
            
            if download:
                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="cotizacion_generada.pdf"'
            else:
                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="cotizacion_generada.pdf"'
            
            return response
            
        except PDFGenerationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )