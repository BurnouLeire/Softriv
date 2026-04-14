# apps/catalog/serializers/__init__.py
from .base import (
    ServiciosSerializer,
    VarianteSerializer,
    PrecioSerializer,
    DimensionSerializer,
    MagnitudSerializer,
    TipoServicioSerializer,
)

from .writable import (
    ServicioWritableSerializer,
    VarianteWritableSerializer,
    PrecioWritableSerializer,
    DimensionWritableSerializer,
)

__all__ = [
    # Base (lectura)
    'ServiciosSerializer',
    'VarianteSerializer',
    'PrecioSerializer',
    'DimensionSerializer',
    'MagnitudSerializer',
    'TipoServicioSerializer',
    # Writable (escritura)
    'ServicioWritableSerializer',
    'VarianteWritableSerializer',
    'PrecioWritableSerializer',
    'DimensionWritableSerializer',
]