from django.db import models
from django.core.exceptions import ValidationError

# ── CATÁLOGOS ─────────────────────────


class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Magnitud(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Procedimiento(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.codigo


class Instrumento(models.Model):
    nombre = models.CharField(max_length=255)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    codigo_base = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre


# ── CATÁLOGO ─────────────────────────

class CatalogoServicio(models.Model):

    class PatronVariacion(models.TextChoices):
        FIJO = 'FIJO'
        PUNTOS = 'PUNTOS'
        RANGO = 'RANGO'
        COMBINADO = 'COMB'

    cod_facturacion = models.CharField(max_length=50, unique=True)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.PROTECT)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    instrumento = models.ForeignKey(Instrumento, on_delete=models.PROTECT)
    procedimiento = models.ForeignKey(
        Procedimiento, on_delete=models.PROTECT, null=True, blank=True)

    nombre = models.CharField(max_length=255, blank=True)
    patron = models.CharField(max_length=10, choices=PatronVariacion.choices)

    precio_base = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    precio_base_no_acreditado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    acreditado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.nombre = f"{self.tipo_servicio} de {self.instrumento}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cod_facturacion} - {self.nombre}"

    def calcular_precio(self, opciones, acreditado):
        from .services import calcular_precio_servicio
        return calcular_precio_servicio(self, opciones, acreditado)


# ── TARIFAS ─────────────────────────

class TarifaPunto(models.Model):

    class TipoEje(models.TextChoices):
        TEMP = 'TEMP'
        HUM = 'HUM'
        PH = 'PH'
        BRIX = 'BRIX'

    servicio = models.ForeignKey(CatalogoServicio, on_delete=models.CASCADE)
    tipo_eje = models.CharField(max_length=10, choices=TipoEje.choices)
    num_punto = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    acreditado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('servicio', 'tipo_eje', 'num_punto', 'acreditado')


class TarifaRango(models.Model):
    servicio = models.ForeignKey(CatalogoServicio, on_delete=models.CASCADE)
    codigo_rango = models.CharField(max_length=30)
    label = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    acreditado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('servicio', 'codigo_rango', 'acreditado')
