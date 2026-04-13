from django.db import models
from apps.sales.models import Cotizacion
# Create your models here.

class Order (models.Model):
    class Status(models.TextChoices):
        PENDIENTE = 'PENDIENTE'
        EN_PROCESO = 'EN_PROCESO'
        PARCIAL = 'PARCIAL'
        FINALIZADA = 'FINALIZADA'
        CANCELADA = 'CANCELADA'

    sales = models.ForeignKey(
        Cotizacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orders'
    )
    reemplaza_a = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    code= models.CharField(max_length=50,unique=True)
    status= models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDIENTE
    )

    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    servicio_nombre = models.CharField(max_length=255)

    configuracion = models.JSONField(default=dict, blank=True)

    cantidad = models.PositiveSmallIntegerField()

    notas = models.TextField(blank=True)

