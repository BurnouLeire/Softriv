from django.contrib import admin
from .models import Customer, Branch, Contact, Phone

# --- CONFIGURACIÓN DE INLINES ---
# Esto permite agregar sucursales dentro de la vista del Cliente


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1  # Cuántos espacios vacíos mostrar para agregar nuevas

# Esto permite agregar teléfonos dentro de la vista del Contacto


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1

# --- CONFIGURACIÓN DEL MODELO CLIENTE ---


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # Columnas que se ven en la lista principal
    list_display = ('identificacion', 'nombre_completo')

    # Filtros laterales
    # list_filter = ('tipo_persona')

    # # Buscador por identificación o nombre
    # search_fields = ('identificacion', 'nombre_completo')

    # Agregamos las sucursales para editarlas aquí mismo
    inlines = [BranchInline]


# --- CONFIGURACIÓN DEL MODELO CONTACTO ---


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'customer', 'email', 'cargo')
    # search_fields = ('nombre', 'email', 'customer__nombre_comercial')

    # Agregamos los teléfonos para editarlos aquí mismo
    inlines = [PhoneInline]


# Registramos los otros modelos de forma sencilla por si quieres verlos solos
# admin.site.register(Branch)
# admin.site.register(Phone)
