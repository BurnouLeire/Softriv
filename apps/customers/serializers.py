from rest_framework import serializers
from .models import Customer, Branch, Contact, Phone


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['id', 'numero', 'tipo']


class ContactSerializer(serializers.ModelSerializer):
    phones = PhoneSerializer(many=True, required=False)

    class Meta:
        model = Contact
        fields = ['id', 'nombre', 'email', 'cargo', 'branch', 'phones']


class BranchSerializer(serializers.ModelSerializer):
    branch_contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Branch
        fields = ['id', 'codigo', 'nombre_sucursal',
                  'ciudad', 'direccion', 'branch_contacts']


class CustomerSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, required=False)
    contacts = ContactSerializer(many=True, required=False)

    tipo_persona_display = serializers.CharField(
        source='get_tipo_persona_display', read_only=True)
    tipo_identificacion_display = serializers.CharField(
        source='get_tipo_identificacion_display', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'tipo_persona', 'tipo_persona_display',
            'tipo_identificacion', 'tipo_identificacion_display',
            'identificacion', 'nombre_completo', 'branches', 'contacts'
        ]

    def create(self, validated_data):
        branches_data = validated_data.pop('branches', [])
        contacts_data = validated_data.pop('contacts', [])
        
        customer = Customer.objects.create(**validated_data)
        
        created_branches = []
        for branch_data in branches_data:
            created_branches.append(Branch.objects.create(customer=customer, **branch_data))
            
        primary_branch = created_branches[0] if created_branches else None
            
        for contact_data in contacts_data:
            phones_data = contact_data.pop('phones', [])
            
            # Map branch index from frontend if available
            branch_index = contact_data.pop('branch_index', None)
            if branch_index is not None and 0 <= branch_index < len(created_branches):
                branch_obj = created_branches[branch_index]
            else:
                branch_obj = primary_branch
                
            # Pop 'branch' if it was sent by accident in nested payload
            contact_data.pop('branch', None)
            
            contact = Contact.objects.create(customer=customer, branch=branch_obj, **contact_data)
            for phone_data in phones_data:
                Phone.objects.create(contact=contact, **phone_data)
                
        return customer

    def update(self, instance, validated_data):
        branches_data = validated_data.pop('branches', None)
        contacts_data = validated_data.pop('contacts', None)
        
        # Actualizamos los campos genéricos del Customer
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        primary_branch = instance.branches.first()
        created_branches = list(instance.branches.all())

        # Re-crear branches
        if branches_data is not None:
            instance.branches.all().delete()
            created_branches = []
            for branch_data in branches_data:
                created_branches.append(Branch.objects.create(customer=instance, **branch_data))
            primary_branch = created_branches[0] if created_branches else None
                
        # Re-crear contacts y linkearlos
        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                phones_data = contact_data.pop('phones', [])
                
                # Link by index first
                branch_index = contact_data.pop('branch_index', None)
                if branch_index is not None and 0 <= branch_index < len(created_branches):
                    branch_obj = created_branches[branch_index]
                else:
                    branch_obj = primary_branch
                    
                contact_data.pop('branch', None)
                
                contact = Contact.objects.create(customer=instance, branch=branch_obj, **contact_data)
                for phone_data in phones_data:
                    Phone.objects.create(contact=contact, **phone_data)
                    
        return instance
