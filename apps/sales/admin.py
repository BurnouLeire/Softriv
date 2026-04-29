# apps/sales/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Quote, Items, QuoteGroup, SubItem

User = get_user_model()


class SubItemInline(admin.TabularInline):
    model = SubItem
    extra = 0
    fields = ('asset', 'magnitude_price', 'quantity', 'unit_price', 'technical_description')
    readonly_fields = ('subtotal',)
    
    def subtotal(self, obj):
        return obj.subtotal if obj.pk else "-"
    subtotal.short_description = "Subtotal"


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 0
    fields = ('service', 'quantity', 'unit_price', 'is_accredited', 'is_outsourced', 'notes')
    readonly_fields = ('subtotal', 'total_subitems')
    show_change_link = True
    
    def subtotal(self, obj):
        return obj.subtotal if obj.pk else "-"
    subtotal.short_description = "Subtotal"
    
    def total_subitems(self, obj):
        return obj.subitems.count() if obj.pk else "-"
    total_subitems.short_description = "N° SubItems"


@admin.register(QuoteGroup)
class QuoteGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'quote', 'total', 'total_items')
    list_filter = ('quote__customer',)
    search_fields = ('name', 'quote__numero')
    inlines = [ItemsInline]
    readonly_fields = ('total', 'total_items')


class QuoteGroupInline(admin.TabularInline):
    model = QuoteGroup
    extra = 0
    fields = ('name', 'order', 'total', 'total_items')
    readonly_fields = ('total', 'total_items')
    show_change_link = True


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'customer', 'branch', 'seller', 'date', 'state')
    list_filter = ('state', 'date', 'customer')
    search_fields = ('numero', 'customer__nombre_completo', 'codigo_empresa')
    readonly_fields = ('numero', 'date')
    fieldsets = (
        ('Información General', {
            'fields': ('numero', 'codigo_empresa', 'customer', 'branch', 'seller', 'date', 'state')
        }),
        ('Documentos', {
            'fields': ('observations', 'archivo_pdf')
        }),
        ('Certificados', {
            'fields': ('certificate_customer',)
        }),
    )
    inlines = [QuoteGroupInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'seller':
            kwargs['queryset'] = User.objects.filter(groups__name='Vendedor')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'service', 'quantity', 'unit_price', 'subtotal', 'is_accredited', 'n_subitems')
    list_filter = ('is_accredited', 'is_outsourced', 'group__quote__customer')
    search_fields = ('service__name', 'group__name', 'group__quote__numero')
    inlines = [SubItemInline]
    readonly_fields = ('subtotal',)
    
    def n_subitems(self, obj):
        return obj.subitems.count()
    n_subitems.short_description = "N° SubItems"


@admin.register(SubItem)
class SubItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'asset', 'magnitude_price', 'quantity', 'unit_price', 'subtotal', 'item_link')
    list_filter = ('magnitude_price__magnitude', 'item__group__quote__customer')
    search_fields = ('asset__tag', 'asset__nombre', 'magnitude_price__tag', 'technical_description')
    readonly_fields = ('subtotal',)
    
    def item_link(self, obj):
        return obj.item.__str__()
    item_link.short_description = "Grupo - Item"