from django.db import models


# ─────────────────────────
# CATÁLOGOS BASE
# ─────────────────────────

class TypeService(models.Model):
    """Define las categorías de servicios y su COMPORTAMIENTO en el negocio"""
    
    BEHAVIOR_CHOICES = [
        ('medible', 'Medible (con instrumento y magnitud)'),
        ('tiempo', 'Por tiempo (días/horas)'),
        ('gasto', 'Gasto real (viáticos)'),
        ('mixto', 'Mixto (puede ser ambos)'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    behavior = models.CharField(max_length=20, choices=BEHAVIOR_CHOICES, default='medible')
    requires_instrument = models.BooleanField(default=True)
    requires_magnitude = models.BooleanField(default=True)
    uses_range_prices = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Type of Service"
        verbose_name_plural = "Types of Services"
    
    def __str__(self):
        return self.name

class Magnitude (models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.nombre
class MagnitudePrice (models.Model):
    magnitude = models.ForeignKey(Magnitude, on_delete=models.PROTECT)
    tag = models.CharField(max_length=100)
    range_min = models.CharField(max_length=100)
    range_max = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    accredited = models.BooleanField(default=False)
    observation = models.TextField(blank=True)

    
    class Meta:
        # Aquí defines el nombre exacto de la tabla
        db_table = 'catalog_magnitude_price'

    def __str__(self):
        return self.magnitude.nombre
    


class Unidades(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    simbolo = models.CharField(max_length=10, unique=True)
    

    def __str__(self):
        return self.nombre


class Procedures(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
class ProceduresMagnitudes(models.Model):
    procedure = models.ForeignKey(Procedures, on_delete=models.PROTECT)
    magnitude = models.ForeignKey(Magnitude, on_delete=models.PROTECT)
    
    
    class Meta:
        db_table = 'catalog_procedures_magnitudes'
        unique_together = ['procedure', 'magnitude']  # Evitar duplicados
        ordering = ['procedure']
    def __str__(self):
        return f"{self.procedure} - {self.magnitude}"


class Instruments(models.Model):
    name = models.CharField(max_length=255)
   # magnitud = models.ForeignKey(Magnitude, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField(max_length=50, blank=True)
    is_measurable=models.BooleanField(default=True)



    def __str__(self):
        return self.name   

class InstrumentMagnitudes(models.Model):
    """Relaciona un INSTRUMENTO con las MAGNITUDES que puede MEDIR"""
    instrument = models.ForeignKey(Instruments, on_delete=models.CASCADE, related_name='magnitudes')
    magnitude = models.ForeignKey(Magnitude, on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=1)  # Para saber si es parámetro 1, 2, 3...
    obligatory = models.BooleanField(default=False)  # Si siempre se debe medir
    observations = models.TextField(blank=True)
    
    class Meta:
        db_table = 'catalog_instrument_magnitudes'
        unique_together = ['instrument', 'magnitude']  # Evitar duplicados
        ordering = ['order']
    def __str__(self):
        return f"{self.instrument} - {self.magnitude}"

# ─────────────────────────
# CATÁLOGO PRINCIPAL
# ─────────────────────────

class Servicios(models.Model):
    code = models.CharField(max_length=50, unique=True)
    tipo_servicio = models.ForeignKey(TypeService, on_delete=models.PROTECT)
    instrumento = models.ForeignKey(Instruments, on_delete=models.PROTECT, null=True, blank=True, related_name='servicios')
    name = models.CharField(max_length=255, blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    acreditado = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    observaciones_internas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.name:
            if self.instrumento:
                self.name = f"{self.tipo_servicio.name} de {self.instrumento.name}"
            else:
                self.name = self.tipo_servicio.name
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
