# apps/sales/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from apps.catalog.models import Servicios
from apps.customers.models import Branch
from django.db import transaction

User = get_user_model()


class Cotizacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR'
        ENVIADA = 'ENVIADA'
        APROBADA = 'APROBADA'
        RECHAZADA = 'RECHAZADA'

    # Campo flexible para el código técnico de la empresa
    codigo_empresa = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código Interno",
        help_text="Código técnico que usa la empresa (ej: SIMET-2024-001, COT-001, etc.)"
    )

    # El número técnico se genera o asigna manualmente
    numero = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Número amigable para mostrar al cliente",
        editable=False
    )
    cliente = models.ForeignKey('customers.Customer', on_delete=models.PROTECT)
    sucursal = models.ForeignKey(Branch, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    observaciones = models.TextField(blank=True)
    certificate_customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='certificates', blank=True, null=True
    )

    # NUEVO CAMPO: Guardará el archivo PDF en Supabase a través de django-storages
    archivo_pdf = models.FileField(
        upload_to='cotizaciones/pdfs/', 
        blank=True, 
        null=True, 
        help_text="PDF generado de la cotización guardado en Supabase"
    )

    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['fecha']),
        ]
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # detectar si es nueva
        if not self.numero:
            from datetime import date
            year = date.today().year

            with transaction.atomic():
                last = Cotizacion.objects.select_for_update().filter(
                    numero__endswith=f'-{year}'
                ).order_by('-numero').first()

                if last:
                    last_num = int(last.numero.split('-')[1])
                    next_num = last_num + 1
                else:
                    next_num = 1

                self.numero = f'RIV.LC-{next_num:04d}-{year}'

        super().save(*args, **kwargs)
        if is_new:
            GrupoCotizacion.objects.get_or_create(
                cotizacion=self,
                nombre="GENERAL",
                defaults={"orden": 0}
            )

    def __str__(self):
        return f"{self.cliente} - {self.numero}"


class GrupoCotizacion(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='grupos'
    )

    nombre = models.CharField(max_length=100)

    # Para ordenar en el PDF
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre}- {self.cotizacion.numero} - {self.cotizacion.cliente}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())


class Items(models.Model):
    """
    Detalle de la cotización. Cada línea representa un servicio configurado.
    """

    # cotizacion = models.ForeignKey(
    #     Cotizacion,
    #     on_delete=models.CASCADE,
    #     related_name='items'  # Cambié 'detalles' a 'items' para que sea más semántico
    # )
    grupo = models.ForeignKey(
        GrupoCotizacion,
        on_delete=models.CASCADE,
        related_name='items',
        null=False,
        blank=False
    )
    servicio = models.ForeignKey(
        Servicios,
        on_delete=models.PROTECT,
        verbose_name="Servicio"
    )

    # Configuración específica (puntos, rangos, etc.)
    configuracion = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuración específica: puntos_temp, puntos_humedad, rango_masa, etc."
    )

    cantidad = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Solo datos específicos del equipo del cliente (marca, modelo, serie)
    # El instrumento_desc ya no es necesario porque está en el servicio
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField(max_length=100, blank=True)

    # Notas adicionales
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales, comentarios, referencia a fotos"
    )

    class Meta:
        indexes = [
            models.Index(fields=['grupo']),
            models.Index(fields=['servicio']),
        ]
        verbose_name = "Item de Cotización"
        verbose_name_plural = "Items de Cotizaciones"

    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.cantidad * self.precio_unitario

    @property
    def instrumento_nombre(self):
        """Obtiene el nombre del instrumento desde el servicio"""
        return self.servicio.instrumento.nombre if self.servicio.instrumento else "N/A"

    def get_descripcion_completa(self):
        """Genera una descripción legible de la configuración"""
        base_desc = f"{self.servicio.tipo_servicio.nombre} de {self.servicio.instrumento.nombre}"

        if not self.configuracion:
            return base_desc

        detalles = []
        for key, value in self.configuracion.items():
            nombre_legible = key.replace('_', ' ').title()
            detalles.append(f"{nombre_legible}: {value}")

        config_text = ", ".join(detalles)
        return f"{base_desc} ({config_text})"

    def __str__(self):
        return f"{self.grupo.cotizacion} - {self.servicio}"
        
    def save(self, *args, **kwargs):
        if not self.grupo:
            from apps.sales.models import GrupoCotizacion
            self.grupo, _ = GrupoCotizacion.objects.get_or_create(nombre="GENERAL")
        super().save(*args, **kwargs)
