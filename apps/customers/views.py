from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer
from apps.users.constants import Roles


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['identificacion', 'nombre_completo']

    def get_queryset(self):
        user = self.request.user
        base_qs = Customer.objects.all().prefetch_related(
            'branches',
            'contacts__phones'
        )

        if user.tiene_alguno_de([Roles.ADMIN, Roles.GERENCIA]):
            return base_qs

        elif user.tiene_rol(Roles.VENDEDOR):
            return base_qs.filter(vendedor=user)

        elif user.tiene_rol(Roles.TECNICO):
            return base_qs.none()

        else:
            return base_qs.none()