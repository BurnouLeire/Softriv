from django.db import models


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
