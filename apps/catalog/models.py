from django.db import models


# ─────────────────────────
# CATÁLOGOS BASE
# ─────────────────────────

class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Magnitud(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    precio_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_maximo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class Unidades(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    simbolo = models.CharField(max_length=10, unique=True)


    def __str__(self):
        return self.nombre


class Procedimiento(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.codigo


class Instrumentos(models.Model):
    nombre = models.CharField(max_length=255)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    codigo_base = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre


# ─────────────────────────
# CATÁLOGO PRINCIPAL
# ─────────────────────────

class Servicios(models.Model):
    code = models.CharField(max_length=50, unique=True)

    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.PROTECT)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    instrumento = models.ForeignKey(Instrumentos, on_delete=models.PROTECT)

    procedimiento_base = models.ForeignKey(
        Procedimiento,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    nombre = models.CharField(max_length=255, blank=True)

    acreditado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    # Si usas camelCase en Python y snake_case en DB
    precio_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,        # Permite que en la DB se guarde como NULL
        blank=True,       # Permite que en formularios de Django se deje vacío
        #  db_column='precio_max'
    )
    # Si usas camelCase en Python y snake_case en DB
    precio_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,        # Permite que en la DB se guarde como NULL
        blank=True,       # Permite que en formularios de Django se deje vacío
        # db_column='precio_max'
    )

    class Meta:
        indexes = [
            models.Index(fields=['code']),
        ]

    def save(self, *args, **kwargs):
        self.nombre = f"{self.tipo_servicio} de {self.instrumento}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.nombre}"


# ─────────────────────────
# VARIANTES (CORE DEL SISTEMA)
# ─────────────────────────

class VarianteServicio(models.Model):
    servicio = models.ForeignKey(
        Servicios,
        on_delete=models.CASCADE,
        related_name='variantes'
    )

    cod_variante = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField()

    procedimiento = models.ForeignKey(
        Procedimiento,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    acreditado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['servicio']),
            # models.Index(fields=['servicio']),
        ]

    def __str__(self):
        return f"{self.servicio} | {self.descripcion}"


# ─────────────────────────
# DIMENSIONES (ESCALABILIDAD REAL)
# ─────────────────────────

class DimensionVariante(models.Model):

    class TipoDimension(models.TextChoices):
        PUNTOS_TEMP = 'PUNTOS_TEMP'
        PUNTOS_HUM = 'PUNTOS_HUM'
        RANGO_MASA = 'RANGO_MASA'
        CAP_MAX = 'CAP_MAX'
        VALOR_NOMINAL = 'VALOR_NOMINAL'
        CLASE_PESO = 'CLASE_PESO'
        ENTORNO = 'ENTORNO'

    variante = models.ForeignKey(
        VarianteServicio,
        on_delete=models.CASCADE,
        related_name='dimensiones'
    )

    tipo_dimension = models.CharField(max_length=30)
    valor_entero = models.IntegerField(null=True, blank=True)
    valor_texto = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('variante', 'tipo_dimension')
        indexes = [
            models.Index(fields=['tipo_dimension']),
        ]

    def __str__(self):
        val = self.valor_entero if self.valor_entero is not None else self.valor_texto
        return f"{self.variante.cod_variante} | {self.tipo_dimension}={val}"


# ─────────────────────────
# PRECIOS (DESACOPLADO)
# ─────────────────────────

class PrecioVariante(models.Model):
    variante = models.ForeignKey(
        VarianteServicio,
        on_delete=models.CASCADE,
        related_name='precios'
    )

    precio = models.DecimalField(max_digits=10, decimal_places=2)

    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-vigente_desde']
        indexes = [
            models.Index(fields=['vigente_desde']),
        ]

    def __str__(self):
        return f"{self.variante.cod_variante} | {self.precio}"
