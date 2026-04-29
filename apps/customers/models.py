from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.catalog.models import TypeInstruments

class Customer(models.Model):

    class PersonType(models.TextChoices):
        NATURAL = 'NAT', 'Persona Natural'
        JURIDICA = 'JUR', 'Persona Jurídica'

    class IDType(models.TextChoices):
        RUC = 'RUC', 'RUC'
        CEDULA = 'CED', 'Cédula'
        PASAPORTE = 'PAS', 'Pasaporte'

    tipo_persona = models.CharField(
        max_length=3,
        choices=PersonType.choices,
        default=PersonType.JURIDICA
    )

    tipo_identificacion = models.CharField(
        max_length=3,
        choices=IDType.choices,
        default=IDType.RUC
    )

    identificacion = models.CharField(
        max_length=13,
        unique=True,
        help_text="Ingrese RUC, Cédula o Pasaporte"
    )

    nombre_completo = models.CharField(
        max_length=255,
        verbose_name="Nombre Completo / Razón Social"
    )
    es_aliado = models.BooleanField(default=False)
    # 🔥 NUEVO: guardamos si pasa validación matemática
    identificacion_valida = models.BooleanField(default=True)

    # 🔥 OPCIONAL PRO: validación real contra SRI (futuro)
    validado_sri = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Cliente"

    def __str__(self):
        return self.nombre_completo

    # =========================
    # VALIDACIÓN ECUADOR
    # =========================
    def validar_identificacion_ec(self, valor):
        v = valor.strip()

        if not v.isdigit():
            return False

        # -------------------------
        # CÉDULA
        # -------------------------
        if len(v) == 10:
            provincia = int(v[0:2])
            if not (1 <= provincia <= 24):
                return False

            tercer_digito = int(v[2])
            if not (0 <= tercer_digito <= 5):
                return False

            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            suma = 0

            for i in range(9):
                val = int(v[i]) * coeficientes[i]
                if val >= 10:
                    val -= 9
                suma += val

            digito = (10 - (suma % 10)) % 10
            return digito == int(v[9])

        # -------------------------
        # RUC
        # -------------------------
        elif len(v) == 13:
            provincia = int(v[0:2])
            if not (1 <= provincia <= 24):
                return False

            tercer_digito = int(v[2])

            # PERSONA NATURAL
            if 0 <= tercer_digito <= 5:
                coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
                suma = 0

                for i in range(9):
                    val = int(v[i]) * coeficientes[i]
                    if val >= 10:
                        val -= 9
                    suma += val

                digito = (10 - (suma % 10)) % 10

                if digito != int(v[9]):
                    return False

                return v[10:13] != "000"

            # ENTIDAD PÚBLICA
            elif tercer_digito == 6:
                coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
                suma = 0

                for i in range(8):
                    suma += int(v[i]) * coeficientes[i]

                digito = 11 - (suma % 11)

                if digito in (10, 11):
                    digito = 0

                if digito != int(v[8]):
                    return False

                return v[9:13] != "0000"

            # SOCIEDAD PRIVADA
            elif tercer_digito == 9:
                coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
                suma = 0

                for i in range(9):
                    suma += int(v[i]) * coeficientes[i]

                digito = 11 - (suma % 11)

                if digito in (10, 11):
                    digito = 0

                # ⚠️ CAMBIO IMPORTANTE:
                # NO devolvemos False directo si falla
                # porque existen RUC válidos en SRI que no cumplen esto (ej: S.A.S.)
                if digito != int(v[9]):
                    return False  # <- solo marca inválido matemáticamente

                return v[10:13] != "000"

            else:
                return False

        return False

    # =========================
    # ⚠️ CAMBIO IMPORTANTE
    # =========================
    def clean(self):
        # ❌ ANTES:
        # bloqueabas el guardado con ValidationError

        # ✅ AHORA:
        # NO bloqueamos, solo validamos en save()
        pass

    # =========================
    # 🔥 SAVE INTELIGENTE
    # =========================
    def save(self, *args, **kwargs):
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.upper()

        # 🔥 VALIDAMOS PERO NO BLOQUEAMOS
        if self.tipo_identificacion in ['CED', 'RUC']:
            self.identificacion_valida = self.validar_identificacion_ec(
                self.identificacion)

        super().save(*args, **kwargs)

    # -------------------------
    # RELACIONES
    # -------------------------
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers_created',
        verbose_name="Creado por"
    )

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Vendedor'},
        related_name='customers_assigned',
        verbose_name="Vendedor asignado"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Branch(models.Model):
    """Corresponde a 'clien_sucursales'"""
    codigo = models.CharField(max_length=4)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='branches')
    nombre_sucursal = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return f"{self.nombre_sucursal} - {self.customer.nombre_completo}"


class Contact(models.Model):
    """Corresponde a 'clien_contactos'"""
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='contacts')
    # Si los contactos dependen de la sucursal, usa esta FK opcional:
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='branch_contacts')

    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    cargo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre


class Phone(models.Model):
    """Corresponde a 'conta_telefonos'"""
    # Relacionamos el teléfono al contacto
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='phones')
    numero = models.CharField(max_length=20)
    tipo = models.CharField(
        max_length=20, help_text="Ej: Celular, Fijo, WhatsApp")

    def __str__(self):
        return f"{self.numero} ({self.contact.nombre})"

class Equipment(models.Model):
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='equipments',
        null=True,
        blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='equipments')
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branch_equipments')
    internal_code= models.CharField("Código interno", max_length=50, blank=True)


    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return f"{self.name} - {self.customer.nombre_completo}"
    