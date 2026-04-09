from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def tiene_rol(self, rol: str) -> bool:
        return self.groups.filter(name=rol).exists()

    def tiene_alguno_de(self, roles: list[str]) -> bool:
        return self.groups.filter(name__in=roles).exists()

    @property
    def roles(self) -> list[str]:
        return list(self.groups.values_list('name', flat=True))

    def __str__(self):
        return f"{self.username} - {', '.join(self.roles)}"
