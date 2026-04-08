from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Customer(models.Model):

    class PersonType(models.TextChoices):
        NATURAL = 'NAT', 'Persona Natural'
        JURIDICA = 'JUR', 'Persona Jurídica'

    class IDType(models.TextChoices):
        RUC = 'RUC', 'RUC'
        CEDULA = 'CED', 'Cédula'
        PASAPORTE = 'PAS', 'Pasaporte'

    # Tipo de entidad (Natural o Empresa)
    tipo_persona = models.CharField(
        max_length=3,
        choices=PersonType.choices,
        default=PersonType.JURIDICA
    )

    # Tipo de documento que presenta
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

    # Razón Social (Nombre de empresa) o Nombres Completos (Persona)
    nombre_completo = models.CharField(
        max_length=255,
        verbose_name="Nombre Completo / Razón Social"
    )

    class Meta:
        verbose_name = "Cliente"

    def __str__(self):
        return self.nombre_completo

        # 🔥 VALIDACIÓN COMPLETA AQUÍ
    def validar_identificacion_ec(self, valor):
        v = valor.strip()

        if not v.isdigit():
            return False

        # =========================
        # CÉDULA (10 dígitos)
        # =========================
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

        # =========================
        # RUC (13 dígitos)
        # =========================
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

                if digito != int(v[9]):
                    return False

                return v[10:13] != "000"

            else:
                return False

        return False

    # 🔥 SE EJECUTA AUTOMÁTICAMENTE

    def clean(self):
        if self.tipo_identificacion in ['CED', 'RUC']:
            if not self.validar_identificacion_ec(self.identificacion):
                raise ValidationError({
                    "identificacion": "Cédula o RUC inválido"
                })

    # 🔥 OBLIGA VALIDACIÓN AL GUARDAR
    def save(self, *args, **kwargs):
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.upper()
        self.full_clean()
        super().save(*args, **kwargs)
     # 🆕 Campo para saber quién creó este cliente
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers_created',
        verbose_name="Creado por"
    )

    # 🆕 Campo para asignar vendedor responsable
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'VENDEDOR'},  # Solo vendedores
        related_name='customers_assigned',
        verbose_name="Vendedor asignado"
    )

    # 🆕 Timestamps automáticos
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
