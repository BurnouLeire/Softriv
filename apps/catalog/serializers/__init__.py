# apps/catalog/serializers/__init__.py
from .base import (
    ServicesSerializer,
    # VarianteSerializer,
    # PrecioSerializer,
    # DimensionSerializer,
    MagnitudeSerializer,
    TypeServiceSerializer,
)

from .writable import (
    ServiceWritableSerializer,
    # VarianteWritableSerializer,
    # PrecioWritableSerializer,
    # DimensionWritableSerializer,
)

__all__ = [
    # Base (lectura)
    'ServicesSerializer',
    'MagnitudeSerializer',
    'TypeServiceSerializer',
    'ServiceWritableSerializer',
]