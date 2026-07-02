"""Vistas de reservas: crear, listar y cancelar reservas del usuario."""

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
from ..models import Reserva
from ..forms import ReservaForm
from .helpers import login_requerido, registrar_error


# ──────────────────────────────────────────────
# 6. Crear reserva (P1: transaction.atomic, P5: sin puntos)
# ──────────────────────────────────────────────

@login_requerido
def crear_reserva_view(request):
    usuario = request.usuario

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
                # P1: Transacción atómica con bloqueo
                with transaction.atomic():
                    # Verificar duplicados dentro de la transacción con lock
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
                            'La cancha ya está reservada en ese horario. '
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
                        codigo_qr=str(uuid.uuid4()),
                        estado='confirmada',
                    )
                    reserva.save()

                # P5: Ya NO se otorgan puntos aquí, se otorgan al validar QR (asistencia)

                messages.success(
                    request,
                    f'Reserva creada. Tu código QR es: {reserva.codigo_qr}'
                )
                return redirect('mis_reservas')

            except IntegrityError:
                # P2: La restricción UNIQUE atrapó un duplicado concurrente
                # P3: Registrar el error
                registrar_error(
                    'crear_reserva',
                    f'IntegrityError: duplicado concurrente para cancha={form.cleaned_data.get("cancha")}, '
                    f'fecha={form.cleaned_data.get("fecha")}',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya está reservada en ese horario. '
                    'Por favor seleccione otro horario disponible.'
                )
                return redirect('disponibilidad')

            except Exception as e:
                # P3: Registrar errores inesperados
                registrar_error(
                    'crear_reserva',
                    f'Error inesperado al crear reserva: {str(e)}',
                    nivel='error'
                )
                messages.error(
                    request,
                    'Ocurrió un problema al procesar su solicitud. Por favor, inténtelo más tarde.'
                )
    else:
        # Pre-cargar datos desde query params si vienen de disponibilidad
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


# ──────────────────────────────────────────────
# 7. Mis reservas + Cancelar
# ──────────────────────────────────────────────

@login_requerido
def mis_reservas_view(request):
    usuario = request.usuario
    reservas_list = Reserva.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    paginator = Paginator(reservas_list, 10)  # 10 per page
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'usuario': usuario,
    })


@login_requerido
def cancelar_reserva_view(request, reserva_id):
    usuario = request.usuario
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario)

    if reserva.estado != 'confirmada':
        messages.error(request, 'Solo puedes cancelar reservas confirmadas.')
    elif reserva.is_past:
        messages.error(request, 'No puedes cancelar una reserva que ya pasó.')
    else:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')

    return redirect('mis_reservas')
