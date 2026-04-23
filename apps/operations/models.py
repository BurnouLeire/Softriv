from django.db import models
from apps.sales.models import Quote
from django.conf import settings

class WorkOrder(models.Model):
    class Status(models.TextChoices):
        # El primer valor es para la DB, el segundo es lo que ve el USUARIO
        PENDING = 'PENDING', 'Pendiente'
        IN_PROGRESS = 'IN_PROGRESS', 'En Proceso'
        PARTIAL = 'PARTIAL', 'Parcial'
        COMPLETED = 'COMPLETED', 'Finalizada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    quote = models.ForeignKey(
        Quote,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name="Cotización" # <-- El usuario ve esto
    )
    
    replaces = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replaced_by',
        verbose_name="Reemplaza a"
    )

    code = models.CharField("Código", max_length=50, unique=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Campos de Agenda
    start_date = models.DateTimeField("Fecha Inicio", null=True, blank=True)
    end_date = models.DateTimeField("Fecha Fin", null=True, blank=True)
    
    created_at = models.DateTimeField("Creado el", auto_now_add=True)

     # ASIGNACIÓN: ¿Quién es el responsable técnico?
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Técnico Asignado",
        related_name="assigned_orders"
    )

    # PRIORIDAD: Para resaltar en el calendario
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Baja'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'Alta'
        URGENT = 'URGENT', 'Urgente'

    priority = models.CharField(
        "Prioridad",
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL
    )

    # UBICACIÓN: ¿Es en laboratorio o en sitio (cliente)?
    is_onsite = models.BooleanField("¿Es en sitio?", default=False)
    location_address = models.TextField("Dirección de ejecución", blank=True)

    # TIEMPO REAL: Para comparar programado vs real después
    actual_start = models.DateTimeField("Inicio Real", null=True, blank=True)
    actual_end = models.DateTimeField("Fin Real", null=True, blank=True)

    class Meta:
        # Esto traduce el nombre de la tabla en el panel administrativo
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        db_table = "operations_work_orders"

    def __str__(self):
        return self.code

class WorkOrderItem(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Orden de Trabajo"
    )

    service_name = models.CharField("Nombre del Servicio", max_length=255)
    configuration = models.JSONField("Configuración Técnica", default=dict, blank=True)
    quantity = models.PositiveSmallIntegerField("Cantidad", default=1)
    notes = models.TextField("Notas/Observaciones", blank=True)

    class Meta:
        verbose_name = "Ítem de Orden"
        verbose_name_plural = "Ítems de Orden"
        db_table = "operations_work_order_items"


class OutsourcingRequest(models.Model):
    """Solicitud de Servicio para laboratorios externos"""
    # Se conecta al ítem de la OT que Ventas marcó como subcontratado
    work_order_item = models.OneToOneField(
        'WorkOrderItem', 
        on_delete=models.CASCADE,
        related_name='outsourcing_request'
    )
    
    # Datos que llena Calidad
    provider = models.ForeignKey('providers.Provider', on_delete=models.PROTECT)
    request_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField("Fecha estimada de retorno", null=True, blank=True)
    
    # Seguimiento de logística
    tracking_number = models.CharField("Guía de envío", max_length=100, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[('SENT', 'Enviado'), ('RECEIVED', 'Recibido'), ('COMPLETED', 'Validado')],
        default='SENT'
    )

    # Documentación técnica
    service_request_pdf = models.FileField(upload_to='requests/pdfs/', null=True, blank=True)
