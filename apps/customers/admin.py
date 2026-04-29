from django.contrib import admin
from .models import Customer, Branch, Contact, Phone, Equipment
from apps.users.models import User
from apps.users.constants import Roles


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('identificacion', 'nombre_completo', 'vendedor')
    inlines = [BranchInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'vendedor':
            kwargs['queryset'] = User.objects.filter(
                groups__name=Roles.VENDEDOR)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'customer', 'email')
    inlines = [PhoneInline]

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('internal_code', 'customer', 'asset')
