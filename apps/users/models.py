# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        VENDEDOR = "VENDEDOR", "Vendedor"
        TECNICO = "TECNICO", "Técnico"
        DIGITADORA = "DIGITADORA", "Digitadora"
        CALIDAD = "CALIDAD", "Calidad"
        GERENCIA = "GERENCIA", "Gerencia"

    rol = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VENDEDOR
    )

    def __str__(self):
        return f"{self.username} - {self.rol}"
