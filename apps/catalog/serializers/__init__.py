# apps/catalog/serializers/__init__.py
from .base import (
    ServiciosSerializer,
    # VarianteSerializer,
    # PrecioSerializer,
    # DimensionSerializer,
    MagnitudeSerializer,
    TypeServiceSerializer,
)

from .writable import (
    ServicioWritableSerializer,
    # VarianteWritableSerializer,
    # PrecioWritableSerializer,
    # DimensionWritableSerializer,
)

__all__ = [
    # Base (lectura)
    'ServiciosSerializer',
    'MagnitudeSerializer',
    'TypeServiceSerializer',
    'ServicioWritableSerializer',
]