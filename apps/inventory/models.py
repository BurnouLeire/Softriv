from django.db import models

# Create your models here.
class InventoryItem(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    quantity = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name    

