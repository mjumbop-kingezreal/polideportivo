from django.contrib import admin
from .models import (
    Usuario,
    Cancha,
    HorarioDisponible,
    Reserva,
    ReservaBloqueo,
    PuntosHistorial,
    LogErrores,
    ConfiguracionPuntos,
    ProductoBar,
    CanjeProducto,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'rol', 'puntos_acumulados', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('nombre', 'correo')


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_deporte', 'ubicacion', 'estado')
    list_filter = ('tipo_deporte', 'estado')
    search_fields = ('nombre',)


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo', 'cancha')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'cancha', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha', 'cancha')
    search_fields = ('usuario__nombre', 'cancha__nombre')


@admin.register(ReservaBloqueo)
class ReservaBloqueoAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'fecha', 'hora_inicio', 'hora_fin', 'reserva')
    list_filter = ('fecha', 'cancha')
    search_fields = ('cancha__nombre', 'reserva__usuario__nombre')


@admin.register(PuntosHistorial)
class PuntosHistorialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntos', 'tipo_movimiento', 'fecha')
    list_filter = ('tipo_movimiento',)


@admin.register(LogErrores)
class LogErroresAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'modulo_origen', 'nivel_severidad')
    list_filter = ('nivel_severidad',)
    search_fields = ('modulo_origen', 'descripcion_error')


@admin.register(ConfiguracionPuntos)
class ConfiguracionPuntosAdmin(admin.ModelAdmin):
    list_display = ('puntos_por_asistencia',)


@admin.register(ProductoBar)
class ProductoBarAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'puntos_requeridos', 'stock', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre',)


@admin.register(CanjeProducto)
class CanjeProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario', 'producto', 'puntos_usados', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('codigo', 'usuario__nombre', 'producto__nombre')