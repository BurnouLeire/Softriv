from django.contrib import admin
from django import forms
from .models import Customer, Branch, Contact, Phone
from apps.users.models import User


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
            kwargs['queryset'] = User.objects.filter(rol='VENDEDOR')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'customer', 'email')
    inlines = [PhoneInline]
