"""Vistas de canchas: listado y disponibilidad."""

import calendar
from pathlib import Path
from datetime import date, timedelta
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from ..models import Cancha, HorarioDisponible, Reserva
from .helpers import login_requerido


DIAS_CORTOS = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
DIAS_LARGOS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
MESES_LARGOS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _court_image_version():
    image_dir = Path(__file__).resolve().parents[2] / 'static' / 'img'
    image_names = [
        'cancha-futbol.jpg',
        'cancha-basquet.jpg',
        'cancha-voley.jpg',
        'cancha-tenis.jpg',
        'cancha-general.jpg',
    ]
    versions = []
    for name in image_names:
        image_path = image_dir / name
        if image_path.exists():
            versions.append(int(image_path.stat().st_mtime))
    return max(versions) if versions else 0



@login_requerido
def lista_canchas_view(request):
    tipo = (request.GET.get('tipo') or '').strip()

    todas_las_canchas = Cancha.objects.all().order_by('nombre')
    canchas_filtradas = todas_las_canchas
    if tipo:
        canchas_filtradas = canchas_filtradas.filter(tipo_deporte=tipo)

    usuario = request.usuario
    image_version = _court_image_version()
    return render(request, 'reservas/lista_canchas.html', {
        'canchas': canchas_filtradas,
        'canchas_mapa': todas_las_canchas,
        'usuario': usuario,
        'tipos': Cancha.TipoDeporte.choices,
        'filtro_tipo': tipo,
        'image_version': image_version,
    })


@login_requerido
def disponibilidad_view(request):
    cancha_id = request.GET.get('cancha')
    fecha_str = request.GET.get('fecha') or timezone.localdate().isoformat()
    cancha = None
    horarios = []

    today_date = timezone.localdate()
    canchas_disponibles = Cancha.objects.filter(estado=Cancha.Estado.DISPONIBLE).order_by('nombre')

    try:
        fecha_obj = date.fromisoformat(fecha_str)
    except ValueError:
        fecha_obj = today_date
        fecha_str = fecha_obj.isoformat()
        messages.error(request, 'Fecha invalida.')

    semana_inicio = fecha_obj - timedelta(days=fecha_obj.weekday())
    semana_fin = semana_inicio + timedelta(days=6)
    fecha_anterior = fecha_obj - timedelta(days=7)
    fecha_siguiente = fecha_obj + timedelta(days=7)

    horarios_por_dia = {}
    reservas_por_fecha = {}
    selected_stats = {'total': 0, 'occupied': 0, 'free': 0, 'past': 0}

    if cancha_id:
        try:
            cancha = Cancha.objects.get(id=cancha_id)
            if cancha.estado != Cancha.Estado.DISPONIBLE:
                messages.warning(
                    request,
                    f'{cancha.nombre} no esta disponible para reservas: {cancha.get_estado_display()}.'
                )
                cancha = None
        except Cancha.DoesNotExist:
            messages.error(request, 'Cancha invalida.')

    if cancha:
        horarios_semana = list(HorarioDisponible.objects.filter(
            cancha=cancha,
            activo=True,
            dia_semana__in=range(1, 8),
        ).order_by('dia_semana', 'hora_inicio'))

        for horario in horarios_semana:
            horarios_por_dia.setdefault(horario.dia_semana, []).append(horario)

        reservas_semana = list(Reserva.objects.filter(
            cancha=cancha,
            fecha__range=[semana_inicio, semana_fin],
            estado__in=['confirmada', 'asistida'],
        ).values_list('fecha', 'hora_inicio', 'hora_fin'))

        for fecha_reserva, hora_inicio, hora_fin in reservas_semana:
            reservas_por_fecha.setdefault(fecha_reserva, set()).add((hora_inicio, hora_fin))

        horarios = list(horarios_por_dia.get(fecha_obj.isoweekday(), []))
        now_time = timezone.localtime(timezone.now()).time()

        for horario in horarios:
            horario.is_ocupado = (horario.hora_inicio, horario.hora_fin) in reservas_por_fecha.get(fecha_obj, set())
            horario.is_past = False

            if fecha_obj < today_date:
                horario.is_past = True
            elif fecha_obj == today_date and horario.hora_inicio < now_time:
                horario.is_past = True

        selected_stats['total'] = len(horarios)
        selected_stats['occupied'] = sum(1 for horario in horarios if horario.is_ocupado)
        selected_stats['past'] = sum(1 for horario in horarios if horario.is_past)
        selected_stats['free'] = sum(1 for horario in horarios if not horario.is_ocupado and not horario.is_past)

    semana_fechas = []
    for offset in range(7):
        dia = semana_inicio + timedelta(days=offset)
        franjas_dia = horarios_por_dia.get(dia.isoweekday(), []) if cancha else []
        reservas_dia = reservas_por_fecha.get(dia, set()) if cancha else set()
        semana_fechas.append({
            'fecha': dia,
            'iso': dia.isoformat(),
            'selected': dia == fecha_obj,
            'today': dia == today_date,
            'past': dia < today_date,
            'name_short': DIAS_CORTOS[dia.weekday()],
            'month_short': MESES_CORTOS[dia.month - 1],
            'slot_count': len(franjas_dia),
            'occupied_count': len(reservas_dia),
            'free_count': max(len(franjas_dia) - len(reservas_dia), 0),
        })

    month_weeks = []
    for week in calendar.Calendar(firstweekday=0).monthdatescalendar(fecha_obj.year, fecha_obj.month):
        week_cells = []
        for day in week:
            week_cells.append({
                'date': day,
                'day': day.day,
                'outside': day.month != fecha_obj.month,
                'selected': day == fecha_obj,
                'today': day == today_date,
            })
        month_weeks.append(week_cells)

    usuario = request.usuario
    return render(request, 'reservas/disponibilidad.html', {
        'canchas': canchas_disponibles,
        'cancha_sel': cancha,
        'fecha': fecha_str,
        'fecha_obj': fecha_obj,
        'horarios': horarios,
        'usuario': usuario,
        'hoy': today_date.isoformat(),
        'semana_fechas': semana_fechas,
        'semana_inicio': semana_inicio,
        'semana_fin': semana_fin,
        'fecha_anterior': fecha_anterior.isoformat(),
        'fecha_siguiente': fecha_siguiente.isoformat(),
        'selected_stats': selected_stats,
        'selected_day_name': DIAS_LARGOS[fecha_obj.weekday()],
        'selected_month_name': MESES_LARGOS[fecha_obj.month - 1],
        'month_weeks': month_weeks,
        'month_weekdays': DIAS_CORTOS,
    })
