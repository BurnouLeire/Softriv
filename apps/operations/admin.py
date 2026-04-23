from django.contrib import admin
from .models import WorkOrder, WorkOrderItem, OutsourcingRequest

class WorkOrderItemInline(admin.StackedInline):
    model = WorkOrderItem
    extra = 0 # No mostrar filas vacías por defecto
    readonly_fields = ('service_name',)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'quote', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('code', 'quote__numero', 'quote__cliente__name')
    
    # Aquí está la magia: al editar una Orden, ves los ítems abajo
    inlines = [WorkOrderItemInline]
    
    # Campos de solo lectura en el header (para que no puedas borrar el código por error)
    readonly_fields = ('created_at',)

@admin.register(WorkOrderItem)
class WorkOrderItemAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'service_name', 'quantity', 'notes')
    list_filter = ('work_order__status',)
    search_fields = ('service_name', 'work_order__code')

@admin.register(OutsourcingRequest)
class OutsourcingRequestAdmin(admin.ModelAdmin):
    list_display = ('work_order_item', 'provider', 'request_date', 'expected_return_date', 'status')
    list_filter = ('status', 'request_date')
    search_fields = ('work_order_item__service_name', 'provider__name')
    readonly_fields = ('request_date',)
