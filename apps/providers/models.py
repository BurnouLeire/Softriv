from django.db import models

# Create your models here.
# apps/providers/models.py

class Provider(models.Model):
    class ProviderType(models.TextChoices):
        LABORATORY = 'LABORATORY', 'Laboratorio de Metrología'
        MAINTENANCE = 'MAINTENANCE', 'Mantenimiento/Reparación'
        LOGISTICS = 'LOGISTICS', 'Transporte/Logística'

    name = models.CharField("Razón Social", max_length=255, unique=True)
    identification = models.CharField("RUC/NIT", max_length=20, unique=True)
    provider_type = models.CharField(
        verbose_name="Tipo de Proveedor",
        max_length=20, 
        choices=ProviderType.choices, 
        default=ProviderType.LABORATORY
    )
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Correo Electrónico", blank=True)
    # --- CONTROL DE CALIDAD ---
    is_approved = models.BooleanField("Proveedor Homologado/Aprobado", default=False)
    accreditation_file = models.FileField(
        "Certificado de Acreditación", 
        upload_to='providers/accreditations/', 
        null=True, blank=True
    )
    expiration_date = models.DateField("Vencimiento de Acreditación", null=True, blank=True)

    def __str__(self):
        return self.name
