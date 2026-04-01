from django.db import models

# --- Tablas Maestras (Las amarillas en tu diagrama) ---


class TipoServicio(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Servicio"
        verbose_name_plural = "Tipos de Servicio"

    def __str__(self):
        return self.nombre


class Magnitud(models.Model):
    nombre = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Magnitud"
        verbose_name_plural = "Magnitudes"

    def __str__(self):
        return self.nombre

# --- Procedimientos e Instrumentos ---


class Procedimiento(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Instrumento(models.Model):
    nombre = models.CharField(max_length=255)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    codigo_base = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# --- El núcleo del catálogo ---


class CatalogoServicio(models.Model):
    cod_facturacion = models.CharField(max_length=100, unique=True)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.PROTECT)
    magnitud = models.ForeignKey(Magnitud, on_delete=models.PROTECT)
    instrumento = models.ForeignKey(Instrumento, on_delete=models.PROTECT)

    # 👇 NUEVO AQUÍ
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.PROTECT)

    nombre = models.CharField(max_length=255, blank=True)
    acreditado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.nombre = f"{self.tipo_servicio} de {self.instrumento}"
        super().save(*args, **kwargs)

# --- Variantes y Parámetros ---


class VarianteServicio(models.Model):
    servicio = models.ForeignKey(
        CatalogoServicio, on_delete=models.CASCADE, related_name='variantes'
    )
    cod_variante = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    # procedimiento = models.ForeignKey(Procedimiento, on_delete=models.PROTECT)
    acreditado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.cod_variante:
            # contar cuántas variantes ya existen para este servicio
            count = VarianteServicio.objects.filter(
                servicio=self.servicio).count() + 1

            # generar código con formato 01, 02, 03...
            self.cod_variante = f"{self.servicio.cod_facturacion}-{count:02d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.cod_variante


class VarianteProc(models.Model):
    # Tabla intermedia segun diagrama
    variante = models.ForeignKey(VarianteServicio, on_delete=models.CASCADE)
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.CASCADE)


class ParametroVariante(models.Model):
    variante = models.ForeignKey(
        VarianteServicio, on_delete=models.CASCADE, related_name='parametros')
    nombre_param = models.CharField(max_length=255)
    valor = models.CharField(max_length=255)
    unidad = models.CharField(max_length=50)
    tipo_dato = models.CharField(max_length=50)  # Ej: float, int, string

    def __str__(self):
        return f"{self.nombre_param}: {self.valor} {self.unidad}"
