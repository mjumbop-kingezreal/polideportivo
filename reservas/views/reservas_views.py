"""Vistas de reservas: crear, listar y cancelar reservas del usuario."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from ..codigos import generar_codigo_acceso
from ..models import Reserva, ReservaBloqueo
from ..forms import ReservaForm
from .helpers import login_requerido, registrar_error


@login_requerido
def crear_reserva_view(request):
    usuario = request.usuario

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
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
                            'La cancha ya esta reservada en ese horario. '
                            'Por favor seleccione otro horario disponible.'
                        )
                        return redirect('disponibilidad')

                    reserva = Reserva(
                        usuario=usuario,
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        observacion=form.cleaned_data.get('observacion', ''),
                        lista_invitados=form.cleaned_data.get('lista_invitados', ''),
                        codigo_qr=generar_codigo_acceso(),
                        estado='confirmada',
                    )
                    reserva.save() 
                    ReservaBloqueo.objects.create(
                        cancha=reserva.cancha,
                        fecha=reserva.fecha,
                        hora_inicio=reserva.hora_inicio,
                        hora_fin=reserva.hora_fin,
                        reserva=reserva,
                    )

                messages.success(
                    request,
                    f'Reserva creada. Tu codigo QR es: {reserva.codigo_qr}'
                )
                return redirect('mis_reservas')

            except IntegrityError:
                registrar_error(
                    'crear_reserva',
                    f'IntegrityError: duplicado concurrente para cancha={form.cleaned_data.get("cancha")}, '
                    f'fecha={form.cleaned_data.get("fecha")}',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya esta reservada en ese horario. '
                    'Por favor seleccione otro horario disponible.'
                )
                return redirect('disponibilidad')

            except Exception as exc:
                registrar_error(
                    'crear_reserva',
                    f'Error inesperado al crear reserva: {str(exc)}',
                    nivel='error'
                )
                messages.error(
                    request,
                    'Ocurrio un problema al procesar su solicitud. Por favor, intentelo mas tarde.'
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
        form = ReservaForm(initial=initial)

    return render(request, 'reservas/crear_reserva.html', {
        'form': form,
        'usuario': usuario,
    })


@login_requerido
def mis_reservas_view(request):
    usuario = request.usuario
    reservas_qs = Reserva.objects.filter(usuario=usuario).select_related('cancha').order_by('-fecha', '-hora_inicio', '-fecha_creacion')

    today_date = timezone.localdate()
    now_time = timezone.localtime(timezone.now()).time()
    reservas_pasadas_confirmadas = reservas_qs.filter(
        estado=Reserva.Estado.CONFIRMADA,
    ).filter(
        Q(fecha__lt=today_date) |
        Q(fecha=today_date, hora_fin__lte=now_time)
    )

    resumen = {
        'total': reservas_qs.count(),
        'futuras': reservas_qs.filter(
            estado=Reserva.Estado.CONFIRMADA,
        ).filter(
            Q(fecha__gt=today_date) |
            Q(fecha=today_date, hora_inicio__gt=now_time)
        ).count(),
        'asistidas': reservas_qs.filter(estado=Reserva.Estado.ASISTIDA).count(),
        'no_asistidas': reservas_qs.filter(estado=Reserva.Estado.NO_ASISTIDA).count() + reservas_pasadas_confirmadas.count(),
    }

    paginator = Paginator(reservas_qs, 10)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'usuario': usuario,
        'resumen': resumen,
    })


@login_requerido
def cancelar_reserva_view(request, reserva_id):
    usuario = request.usuario

    with transaction.atomic():
        reserva = get_object_or_404(
            Reserva.objects.select_for_update(),
            id=reserva_id,
            usuario=usuario,
        )

        if reserva.estado != 'confirmada':
            messages.error(request, 'Solo puedes cancelar reservas confirmadas.')
        elif not reserva.can_cancel:
            messages.error(request, 'Solo puedes cancelar reservas futuras.')
        else:
            reserva.estado = 'cancelada'
            reserva.save(update_fields=['estado'])
            ReservaBloqueo.objects.filter(reserva=reserva).delete()
            messages.success(request, 'Reserva cancelada exitosamente.')

    return redirect('mis_reservas')
