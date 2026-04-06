from django.db import models
from django.contrib.auth import get_user_model
from apps.catalog.models import VarianteServicio

User = get_user_model()


# ─────────────────────────
# CABECERA
# ─────────────────────────

class Cotizacion(models.Model):

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR'
        ENVIADA = 'ENVIADA'
        APROBADA = 'APROBADA'
        RECHAZADA = 'RECHAZADA'

    numero = models.CharField(max_length=20, unique=True, blank=True)

    cliente = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT
    )

    vendedor = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    fecha = models.DateField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR
    )

    observaciones = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['fecha']),
        ]

    def save(self, *args, **kwargs):
        if not self.numero:
            from datetime import date
            year = date.today().year

            count = Cotizacion.objects.filter(
                numero__startswith=f'COT-{year}'
            ).count()

            self.numero = f'COT-{year}-{count + 1:04d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero}-{self.cliente}"


# ─────────────────────────
# DETALLE
# ─────────────────────────

class CotizDetalle(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    variante = models.ForeignKey(
        VarianteServicio,
        on_delete=models.PROTECT
    )

    cantidad = models.PositiveSmallIntegerField(default=1)

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Snapshot del instrumento del cliente
    instrumento_desc = models.CharField(max_length=255)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField(max_length=100, blank=True)

    observaciones = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['cotizacion']),
        ]

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cotizacion.numero} - {self.variante}"
