# apps/catalog/serializers/__init__.py
from .base import (
    ServiciosSerializer,
    # VarianteSerializer,
    # PrecioSerializer,
    # DimensionSerializer,
    MagnitudeSerializer,
    TipoServicioSerializer,
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
    # 'VarianteSerializer',
    # 'PrecioSerializer',
    # 'DimensionSerializer',
    'MagnitudeSerializer',
    'TipoServicioSerializer',
    # Writable (escritura)
    'ServicioWritableSerializer',
    # 'VarianteWritableSerializer',
    # 'PrecioWritableSerializer',
    # 'DimensionWritableSerializer',
]