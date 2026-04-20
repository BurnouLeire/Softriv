# apps/sales/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from apps.catalog.models import Services
from apps.customers.models import Branch
from django.db import transaction

User = get_user_model()


class Quote(models.Model):
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
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, verbose_name="Cliente")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="Sucursal")
    seller = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Vendedor")
    date = models.DateField(auto_now_add=True)
    state = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    observations = models.TextField(blank=True)
    certificate_customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='certificates', blank=True, null=True
    )

    # NUEVO CAMPO: Guardará el archivo PDF en Supabase a través de django-storages
    archivo_pdf = models.FileField(
        upload_to='quotes/pdfs/', 
        blank=True, 
        null=True, 
        help_text="PDF generado de la cotización guardado en Supabase"
    )

    class Meta:
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['date']),
        ]
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # detectar si es nueva
        if not self.numero:
            from datetime import date
            year = date.today().year

            with transaction.atomic():
                last = Quote.objects.select_for_update().filter(
                    numero__endswith=f'-{year}'
                ).order_by('-numero').first()

                if last:
                    last_num = int(last.numero.split('-')[1])
                    next_num = last_num + 1
                else:
                    next_num = 1

                self.numero = f'RIV.LC-{next_num:04d}-{year}'

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.customer} - {self.numero}"


class QuoteGroup(models.Model):
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='groups',
        null=True,
    )

    name = models.CharField(max_length=100)

    # Para ordenar en el PDF
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name}- {self.quote.numero} - {self.quote.customer}"

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
    group = models.ForeignKey(
        QuoteGroup,
        verbose_name="Grupo",
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=False
    )
    service = models.ForeignKey(
        Services,
        verbose_name="Servicio",
        on_delete=models.PROTECT,
    )

    # Configuración específica (puntos, rangos, etc.)
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuración específica: puntos_temp, puntos_humedad, rango_masa, etc."
    )

    quantity = models.PositiveSmallIntegerField(
        "Cantidad",
        default=1,
        validators=[MinValueValidator(1)]
    )

    unit_price = models.DecimalField(
        "Precio Unitario",
        max_digits=10,
        decimal_places=2
    )

    # Solo datos específicos del equipo del cliente (marca, modelo, serie)
    # El instrumento_desc ya no es necesario porque está en el servicio
    brand = models.CharField("Marca",max_length=100, blank=True)
    model = models.CharField("Modelo",max_length=100, blank=True)
    serial = models.CharField("Serie",max_length=100, blank=True)

    # Notas adicionales
    notes = models.TextField(
        "Notas",
        blank=True,
        help_text="Notas adicionales, comentarios, referencia a fotos"
    )
    is_outsourced = models.BooleanField("¿Subcontratado?", default=False)
    external_provider = models.ForeignKey(
        'providers.Provider',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Enviar a (Lab Externo)"

    )

    class Meta:
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['service']),
        ]
        verbose_name = "Item of Quote"
        verbose_name_plural = "Items of Quotes"

    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.unit_price

    @property
    def instrument_name(self):
        """Obtiene el nombre del instrumento desde el servicio"""
        return self.service.instrument.nombre if self.service.instrument else "N/A"

    def get_descripcion_completa(self):
        """Genera una descripción legible de la configuración"""
        base_desc = f"{self.service.type_service.nombre} de {self.service.instrument.nombre}"

        if not self.configuration:
            return base_desc

        detalles = []
        for key, value in self.configuration.items():
            nombre_legible = key.replace('_', ' ').title()
            detalles.append(f"{nombre_legible}: {value}")

        config_text = ", ".join(detalles)
        return f"{base_desc} ({config_text})"

    def __str__(self):
        return f"{self.group.quote} - {self.service}"
        
    def save(self, *args, **kwargs):
        if not self.group:
            from apps.sales.models import QuoteGroup
            self.group, _ = QuoteGroup.objects.get_or_create(nombre="GENERAL")
        super().save(*args, **kwargs)
class SubItem (models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE, related_name='subitems')
    service = models.ForeignKey(Services, on_delete=models.PROTECT)
    configuration = models.JSONField(default=dict, blank=True)
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    class Meta:
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['service']),
        ]
        verbose_name = "SubItem de Cotización"
        verbose_name_plural = "SubItems de Cotizaciones"
    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.unit_price
    @property
    def instrument_name(self):
        """Obtiene el nombre del instrumento desde el servicio"""
        return self.service.instrument.name if self.service.instrument else "N/A"
    def get_descripcion_completa(self):
        """Genera una descripción legible de la configuración"""
        base_desc = f"{self.service.type_service.nombre} de {self.service.instrument.name}"
        if not self.configuration:
            return base_desc
        detalles = []
        for key, value in self.configuration.items():
            nombre_legible = key.replace('_', ' ').title()
            detalles.append(f"{nombre_legible}: {value}")
        config_text = ", ".join(detalles)
        return f"{base_desc} ({config_text})"
    def __str__(self):
        return f"{self.item.group.quote} - {self.servicio}"
    def save(self, *args, **kwargs):
        if not self.item:
            from apps.sales.models import Items
            self.item, _ = Items.objects.get_or_create(nombre="GENERAL")
        super().save(*args, **kwargs)