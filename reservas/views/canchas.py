"""Vistas de canchas: listado y disponibilidad."""

from datetime import date
from django.shortcuts import render
from django.contrib import messages
from ..models import Cancha, HorarioDisponible, Reserva
from .helpers import login_requerido


# ──────────────────────────────────────────────
# 4. Lista de canchas
# ──────────────────────────────────────────────

@login_requerido
def lista_canchas_view(request):
    canchas = Cancha.objects.all()

    # Filtros opcionales
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')

    if tipo:
        canchas = canchas.filter(tipo_deporte=tipo)
    if estado:
        canchas = canchas.filter(estado=estado)

    usuario = request.usuario
    return render(request, 'reservas/lista_canchas.html', {
        'canchas': canchas,
        'usuario': usuario,
        'tipos': Cancha.TipoDeporte.choices,
        'estados': Cancha.Estado.choices,
        'filtro_tipo': tipo or '',
        'filtro_estado': estado or '',
    })


# ──────────────────────────────────────────────
# 5. Disponibilidad
# ──────────────────────────────────────────────

@login_requerido
def disponibilidad_view(request):
    cancha_id = request.GET.get('cancha')
    fecha_str = request.GET.get('fecha')
    cancha = None
    horarios = []
    reservas_existentes = []
    reservas_existentes_str = []

    canchas_disponibles = Cancha.objects.filter(estado='disponible')

    if cancha_id:
        try:
            cancha = Cancha.objects.get(id=cancha_id)
        except Cancha.DoesNotExist:
            messages.error(request, 'Cancha inválida.')

    if cancha and fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
            dia_semana = fecha_obj.isoweekday()  # 1=Lunes, 7=Domingo

            horarios = list(HorarioDisponible.objects.filter(
                cancha=cancha,
                dia_semana=dia_semana,
                activo=True,
            ))

            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha_obj,
                estado__in=['confirmada', 'asistida'],
            ).values_list('hora_inicio', 'hora_fin')

            from django.utils import timezone
            now_time = timezone.localtime(timezone.now()).time()
            today_date = timezone.localtime(timezone.now()).date()

            for h in horarios:
                h.is_ocupado = False
                h_inicio_str = h.hora_inicio.strftime('%H:%M')
                h_fin_str = h.hora_fin.strftime('%H:%M')

                for r_inicio, r_fin in reservas_existentes:
                    r_inicio_str = r_inicio.strftime('%H:%M')
                    r_fin_str = r_fin.strftime('%H:%M')
                    if h_inicio_str == r_inicio_str and h_fin_str == r_fin_str:
                        h.is_ocupado = True
                        break

                if fecha_obj < today_date:
                    h.is_past = True
                elif fecha_obj == today_date and h.hora_inicio < now_time:
                    h.is_past = True
                else:
                    h.is_past = False

        except ValueError:
            messages.error(request, 'Fecha inválida.')

    usuario = request.usuario
    return render(request, 'reservas/disponibilidad.html', {
        'canchas': canchas_disponibles,
        'cancha_sel': cancha,
        'fecha': fecha_str or '',
        'horarios': horarios,
        'reservas_existentes': list(reservas_existentes),
        'reservas_existentes_str': reservas_existentes_str,
        'usuario': usuario,
    })
