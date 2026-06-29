from django.contrib import admin
from .models import (
    Usuario,
    Cancha,
    HorarioDisponible,
    Reserva,
    PuntosHistorial,
    LogErrores,
    ConfiguracionPuntos,
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
    list_display = ('puntos_por_asistencia', 'minimo_canje')