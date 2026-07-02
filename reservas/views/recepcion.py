"""Vistas de recepción: validar QR, crear reservas, calendario, historial."""

import uuid
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import Usuario, Cancha, Reserva, PuntosHistorial, ConfiguracionPuntos
from ..forms import ValidacionQRForm, ReservaRecepcionForm
from .helpers import rol_requerido, registrar_error


# ──────────────────────────────────────────────
# 8. Validar QR (P5: otorgar puntos, P8: verificar hora)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def validar_qr_view(request):
    resultado = None

    if request.method == 'POST':
        form = ValidacionQRForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo_qr']
            try:
                reserva = Reserva.objects.get(codigo_qr=codigo)

                if reserva.estado != 'confirmada':
                    resultado = {
                        'valido': False,
                        'mensaje': f'La reserva está {reserva.get_estado_display()}.',
                    }
                elif reserva.fecha < date.today():
                    resultado = {
                        'valido': False,
                        'mensaje': 'La reserva ya venció (fecha pasada).',
                    }
                else:
                    # P8: Verificar hora actual vs franja horaria
                    from django.utils import timezone
                    ahora = timezone.localtime(timezone.now()).time()
                    aviso_hora = ''

                    if reserva.fecha == date.today():
                        # Margen de 30 minutos antes y después
                        from datetime import datetime as dt
                        hora_inicio_dt = dt.combine(date.today(), reserva.hora_inicio)
                        hora_fin_dt = dt.combine(date.today(), reserva.hora_fin)
                        ahora_dt = dt.combine(date.today(), ahora)

                        margen = timedelta(minutes=30)
                        if ahora_dt < (hora_inicio_dt - margen):
                            aviso_hora = f' (Nota: La reserva es a las {reserva.hora_inicio.strftime("%H:%M")}, aún es temprano)'
                        elif ahora_dt > (hora_fin_dt + margen):
                            aviso_hora = f' (Nota: La franja horaria ya terminó a las {reserva.hora_fin.strftime("%H:%M")})'

                    # Marcar como asistida
                    reserva.estado = 'asistida'
                    reserva.save()

                    # P5: Otorgar puntos al ASISTIR (no al crear)
                    config = ConfiguracionPuntos.obtener()
                    puntos = config.puntos_por_asistencia

                    PuntosHistorial.objects.create(
                        usuario=reserva.usuario,
                        reserva=reserva,
                        puntos=puntos,
                        tipo_movimiento='otorgado',
                        descripcion=f'Puntos por asistencia confirmada (+{puntos}).',
                    )
                    reserva.usuario.puntos_acumulados += puntos
                    reserva.usuario.save()

                    resultado = {
                        'valido': True,
                        'mensaje': f'Acceso autorizado. Reserva marcada como Asistida. '
                                   f'+{puntos} puntos otorgados a {reserva.usuario.nombre}.{aviso_hora}',
                        'reserva': reserva,
                    }

            except Reserva.DoesNotExist:
                # P3: Registrar QR no encontrado
                registrar_error(
                    'validar_qr',
                    f'Código QR no encontrado: {codigo}',
                    nivel='warning'
                )
                resultado = {
                    'valido': False,
                    'mensaje': 'Código QR no encontrado.',
                }
    else:
        form = ValidacionQRForm()

    usuario = request.usuario
    return render(request, 'reservas/validar_qr.html', {
        'form': form,
        'resultado': resultado,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 8.1. Recepcionista: Crear Reserva para Usuario (P1: atomic)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def crear_reserva_recepcion_view(request):
    usuario_recepcion = request.usuario

    if request.method == 'POST':
        form = ReservaRecepcionForm(request.POST)
        if form.is_valid():
            try:
                # P1: Transacción atómica
                with transaction.atomic():
                    existe = Reserva.objects.select_for_update().filter(
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        estado__in=['confirmada', 'asistida'],
                    ).exists()

                    if existe:
                        messages.error(
                            request,
                            'La cancha ya está reservada en ese horario.'
                        )
                        return redirect('calendario_reservas')

                    usuario_cliente = form.cleaned_data['usuario']
                    reserva = Reserva(
                        usuario=usuario_cliente,
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        observacion=form.cleaned_data.get('observacion', ''),
                        lista_invitados=form.cleaned_data.get('lista_invitados', ''),
                        codigo_qr=str(uuid.uuid4()),
                        estado='confirmada',
                    )
                    reserva.save()

                # P5: Ya NO se otorgan puntos aquí, se otorgan al validar QR

                messages.success(
                    request,
                    f'Reserva creada para {usuario_cliente.nombre}. '
                    f'Código QR: {reserva.codigo_qr}'
                )
                return redirect('calendario_reservas')

            except IntegrityError:
                registrar_error(
                    'crear_reserva_recepcion',
                    f'IntegrityError: duplicado concurrente en reserva de recepción',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya está reservada en ese horario.'
                )
                return redirect('calendario_reservas')

            except Exception as e:
                registrar_error(
                    'crear_reserva_recepcion',
                    f'Error inesperado: {str(e)}',
                    nivel='error'
                )
                messages.error(
                    request,
                    'Ocurrió un problema al procesar su solicitud. Por favor, inténtelo más tarde.'
                )
    else:
        initial = {}
        if request.GET.get('cancha'):
            initial['cancha'] = request.GET.get('cancha')
        if request.GET.get('fecha'):
            initial['fecha'] = request.GET.get('fecha')
        if request.GET.get('hora_inicio'):
            initial['hora_inicio'] = request.GET.get('hora_inicio')
        if request.GET.get('hora_fin'):
            initial['hora_fin'] = request.GET.get('hora_fin')
        form = ReservaRecepcionForm(initial=initial)

    return render(request, 'reservas/crear_reserva_recepcion.html', {
        'form': form,
        'usuario': usuario_recepcion,
    })


# ──────────────────────────────────────────────
# 8.2. Recepcionista: Calendario de Reservas (P7: semanal)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def calendario_reservas_view(request):
    fecha_str = request.GET.get('fecha')
    vista = request.GET.get('vista', 'diaria')  # P7: diaria o semanal

    if fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_obj = date.today()
    else:
        fecha_obj = date.today()

    if vista == 'semanal':
        # P7: Calcular lunes-domingo de la semana
        lunes = fecha_obj - timedelta(days=fecha_obj.weekday())
        domingo = lunes + timedelta(days=6)
        reservas = Reserva.objects.select_related('cancha', 'usuario').filter(
            fecha__range=[lunes, domingo]
        ).order_by('fecha', 'hora_inicio')
        dias_semana = [lunes + timedelta(days=i) for i in range(7)]
    else:
        reservas = Reserva.objects.select_related('cancha', 'usuario').filter(
            fecha=fecha_obj
        ).order_by('hora_inicio')
        dias_semana = []
        lunes = None
        domingo = None

    return render(request, 'reservas/calendario.html', {
        'fecha': fecha_obj,
        'fecha_str': fecha_obj.isoformat(),
        'reservas': reservas,
        'usuario': request.usuario,
        'vista': vista,
        'dias_semana': dias_semana,
        'lunes': lunes,
        'domingo': domingo,
    })


# ──────────────────────────────────────────────
# 8.3. Recepcionista: Marcar No Asistida
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def marcar_no_asistida_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.estado != 'confirmada':
        messages.error(request, 'Solo se pueden marcar reservas confirmadas.')
    else:
        reserva.estado = 'no_asistida'
        reserva.save()
        messages.success(request, f'Reserva #{reserva.id} marcada como No Asistida.')

    # Redirigir de vuelta a donde vino (calendario o validación)
    next_url = request.META.get('HTTP_REFERER', 'calendario_reservas')
    return redirect(next_url)


# ──────────────────────────────────────────────
# 8.4. Recepcionista: Historial General
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def historial_reservas_view(request):
    busqueda = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')

    reservas = Reserva.objects.select_related('cancha', 'usuario').all()

    if busqueda:
        # FIX: Usar Q() para combinar filtros correctamente en un solo queryset
        reservas = reservas.filter(
            Q(usuario__nombre__icontains=busqueda) | Q(usuario__correo__icontains=busqueda)
        )
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
            reservas = reservas.filter(fecha=fecha_obj)
        except ValueError:
            pass

    reservas = reservas.order_by('-fecha', '-hora_inicio')

    # Paginación: 20 resultados por página
    paginator = Paginator(reservas, 20)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    return render(request, 'reservas/historial_reservas.html', {
        'reservas': reservas,
        'busqueda': busqueda,
        'fecha': fecha,
        'usuario': request.usuario,
    })
