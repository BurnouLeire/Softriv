from django.contrib import admin
from .models import (
    TipoServicio, Magnitud, Procedimiento, Instrumento,
    CatalogoServicio, VarianteServicio, ParametroVariante, VarianteProc
)

# --- INLINES ---


class ParametroVarianteInline(admin.TabularInline):
    model = ParametroVariante
    extra = 1


# Stacked ocupa más espacio, ideal para muchos campos
class VarianteServicioInline(admin.StackedInline):
    model = VarianteServicio
    extra = 0
    show_change_link = True  # Permite ir a editar la variante sola


class VarianteProcInline(admin.TabularInline):
    model = VarianteProc
    extra = 1

# --- CONFIGURACIONES PRINCIPALES ---


@admin.register(CatalogoServicio)
class CatalogoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_servicio',
                    'magnitud', 'acreditado', 'activo')
    list_filter = ('tipo_servicio', 'magnitud', 'acreditado', 'activo')
    search_fields = ('codigo', 'nombre', 'cod_facturacion')

    # Esto permite crear el servicio y sus variantes de una vez
    inlines = [VarianteServicioInline]


@admin.register(VarianteServicio)
class VarianteServicioAdmin(admin.ModelAdmin):
    list_display = ('cod_variante', 'servicio', 'acreditado', 'activo')
    list_filter = ('acreditado', 'activo')
    search_fields = ('cod_variante', 'servicio__nombre')

    # Aquí puedes gestionar los parámetros y procedimientos de la variante
    inlines = [ParametroVarianteInline, VarianteProcInline]


@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'magnitud', 'codigo_base', 'activo')
    list_filter = ('magnitud', 'activo')
    search_fields = ('nombre', 'codigo_base')

# --- CONFIGURACIONES SIMPLES (TABLAS MAESTRAS) ---


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')


@admin.register(Magnitud)
class MagnitudAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')


@admin.register(Procedimiento)
class ProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
