from reportlab.lib.colors import black
from django.db import models

from apps.catalog.models import TypeInstruments


class Asset(models.Model):
    
    OWNER_CHOICES = [
        ('customer', 'Cliente'),
        ('laboratory', 'Laboratorio'),
    ]

    type_instrument = models.ForeignKey(
        TypeInstruments, 
        verbose_name='Tipo de Instrumento',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='type_instrument_assets')
    name = models.CharField("Nombre",max_length=100, blank=True)
    brand = models.CharField("Marca",max_length=100, blank=True)
    model = models.CharField("Modelo",max_length=100, blank=True)
    serial_number = models.CharField("Número de serie",max_length=50, blank=True)
    

    owner_type = models.CharField(
        verbose_name='Tipo de Propietario',
        max_length=20, 
        choices=OWNER_CHOICES, 
        default='customer'
        )
    
    
    customer = models.ForeignKey(
        'customers.Customer', 
        verbose_name='Cliente',
        on_delete=models.CASCADE, 
        related_name='assets',
        null=True,
        blank=True,
        )

    metadata = models.JSONField(default=dict, blank=True)

    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
    
    def __str__(self):
        return f"{self.type_instrument.name} - {self.brand} - {self.model}"