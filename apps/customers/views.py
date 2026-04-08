# customers/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['identificacion', 'nombre_completo']

    def get_queryset(self):
        """
        Filtra clientes según el rol del usuario actual.

        Reglas:
        - Vendedor: Solo ve clientes donde él es el vendedor
        - Gerencia: Ve todos los clientes
        - Facturación: Ve clientes con OT ejecutadas
        - Técnico: No ve clientes (devuelve queryset vacío)
        """
        user = self.request.user
        base_qs = Customer.objects.all().prefetch_related(
            'branches',
            'contacts__phones'
        )

        # 🔐 GERENCIA ve todo
        if user.rol == 'gerencia':
            return base_qs

        # 🔐 VENDEDOR ve solo sus clientes
        elif user.rol == 'vendedor':
            # Asumiendo que agregarás campo 'vendedor' a Customer
            # o lo relaciones vía Prospecto/Cotización
            return base_qs.filter(vendedor=user)

        # 🔐 FACTURACIÓN ve clientes con OT ejecutadas
        elif user.rol == 'facturacion':
            from equipment.models import OrdenDeTrabajo
            clientes_con_ot = OrdenDeTrabajo.objects.filter(
                estado='ejecutada'
            ).values_list('cliente_id', flat=True).distinct()
            return base_qs.filter(id__in=clientes_con_ot)

        # 🔐 TÉCNICO no ve clientes
        elif user.rol == 'tecnico':
            return base_qs.none()  # Queryset vacío

        # 🔐 Default: solo sus propios registros (si tiene campo 'created_by')
        else:
            return base_qs.filter(created_by=user)
