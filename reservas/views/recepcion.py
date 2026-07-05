"""Vistas de recepcion: validar QR, crear reservas, calendario, historial."""

import calendar
from datetime import date, timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..codigos import generar_codigo_acceso, identificar_tipo_codigo, normalizar_codigo
from ..forms import ReservaRecepcionForm, ValidacionQRForm, obtener_opciones_horario_recepcion
from ..models import (
    CanjeProducto,
    ConfiguracionPuntos,
    PuntosHistorial,
    Reserva,
    ReservaBloqueo,
    Usuario,
)
from .helpers import registrar_error, rol_requerido


# ------------------------------------------------------------------------------
# 8. Validar QR (P5: otorgar puntos, P8: verificar hora)
# ------------------------------------------------------------------------------

def _obtener_reserva_por_codigo(codigo):
    return (
        Reserva.objects.select_for_update()
        .select_related('usuario', 'cancha')
        .get(codigo_qr=codigo)
    )


def _obtener_voucher_por_codigo(codigo):
    return (
        CanjeProducto.objects.select_for_update()
        .select_related('usuario', 'producto')
        .get(codigo=codigo)
    )


def _buscar_objeto_escaneado(codigo):
    """Prioriza prefijos nuevos y mantiene compatibilidad con codigos antiguos."""
    tipo_codigo = identificar_tipo_codigo(codigo)

    if tipo_codigo == 'acceso':
        return 'acceso', _obtener_reserva_por_codigo(codigo)

    if tipo_codigo == 'voucher':
        return 'voucher', _obtener_voucher_por_codigo(codigo)

    try:
        return 'acceso', _obtener_reserva_por_codigo(codigo)
    except Reserva.DoesNotExist:
        return 'voucher', _obtener_voucher_por_codigo(codigo)


def _resultado_reserva_valida(reserva):
    from datetime import datetime as dt

    from django.utils import timezone

    aviso_hora = ''
    ahora = timezone.localtime(timezone.now()).time()

    if reserva.fecha == date.today():
        hora_inicio_dt = dt.combine(date.today(), reserva.hora_inicio)
        hora_fin_dt = dt.combine(date.today(), reserva.hora_fin)
        ahora_dt = dt.combine(date.today(), ahora)

        margen = timedelta(minutes=30)
        if ahora_dt < (hora_inicio_dt - margen):
            aviso_hora = (
                f' Nota: la reserva es a las {reserva.hora_inicio.strftime("%H:%M")} '
                'y todavia es temprano.'
            )
        elif ahora_dt > (hora_fin_dt + margen):
            aviso_hora = (
                f' Nota: la franja ya termino a las {reserva.hora_fin.strftime("%H:%M")}.'
            )

    reserva.estado = Reserva.Estado.ASISTIDA
    reserva.save(update_fields=['estado'])

    config = ConfiguracionPuntos.obtener()
    puntos = config.puntos_por_asistencia
    usuario_reserva = Usuario.objects.select_for_update().get(id=reserva.usuario_id)

    PuntosHistorial.objects.create(
        usuario=usuario_reserva,
        reserva=reserva,
        puntos=puntos,
        tipo_movimiento='otorgado',
        descripcion=f'Puntos por asistencia confirmada (+{puntos}).',
    )
    usuario_reserva.puntos_acumulados += puntos
    usuario_reserva.save(update_fields=['puntos_acumulados'])
    reserva.usuario = usuario_reserva

    return {
        'valido': True,
        'tipo': 'acceso',
        'mensaje': (
            f'Acceso permitido - {usuario_reserva.nombre}. '
            f'Reserva marcada como asistida y +{puntos} puntos otorgados.{aviso_hora}'
        ),
        'reserva': reserva,
    }


def _procesar_reserva(reserva):
    if reserva.estado != Reserva.Estado.CONFIRMADA:
        return {
            'valido': False,
            'tipo': 'acceso',
            'mensaje': f'La reserva esta {reserva.get_estado_display()}.',
        }

    if reserva.fecha < date.today():
        return {
            'valido': False,
            'tipo': 'acceso',
            'mensaje': 'La reserva ya vencio (fecha pasada).',
        }

    return _resultado_reserva_valida(reserva)


def _procesar_voucher(canje):
    if canje.estado != CanjeProducto.Estado.PENDIENTE:
        return {
            'valido': False,
            'tipo': 'voucher',
            'mensaje': f'El voucher ya esta {canje.get_estado_display()}.',
        }

    if canje.esta_caducado:
        return {
            'valido': False,
            'tipo': 'voucher',
            'mensaje': 'El voucher ya caduco.',
        }

    canje.estado = CanjeProducto.Estado.ENTREGADO
    canje.save(update_fields=['estado'])

    return {
        'valido': True,
        'tipo': 'voucher',
        'mensaje': (
            f'Voucher validado - Comprobante PDF listo para imprimir. '
            f'Producto: {canje.producto.nombre}.'
        ),
        'es_voucher': True,
        'canje_id': canje.id,
        'producto_nombre': canje.producto.nombre,
    }


def _procesar_codigo_escaneado(codigo):
    try:
        tipo, objeto = _buscar_objeto_escaneado(codigo)
    except Reserva.DoesNotExist:
        registrar_error(
            'validar_qr',
            f'Codigo de acceso no encontrado: {codigo}',
            nivel='warning'
        )
        return {
            'valido': False,
            'tipo': 'acceso',
            'mensaje': 'Codigo de acceso no encontrado.',
        }
    except CanjeProducto.DoesNotExist:
        registrar_error(
            'validar_qr',
            f'Codigo QR/Voucher no encontrado: {codigo}',
            nivel='warning'
        )
        return {
            'valido': False,
            'tipo': 'desconocido',
            'mensaje': 'Codigo no encontrado (ni acceso ni voucher).',
        }

    if tipo == 'acceso':
        return _procesar_reserva(objeto)
    return _procesar_voucher(objeto)


@rol_requerido('recepcionista', 'administrador')
def validar_qr_view(request):
    resultado = None

    if request.method == 'POST':
        form = ValidacionQRForm(request.POST)
        if form.is_valid():
            codigo = normalizar_codigo(form.cleaned_data['codigo_qr'])
            with transaction.atomic():
                resultado = _procesar_codigo_escaneado(codigo)
    else:
        form = ValidacionQRForm()

    usuario = request.usuario
    return render(request, 'reservas/validar_qr.html', {
        'form': form,
        'resultado': resultado,
        'usuario': usuario,
    })


# ------------------------------------------------------------------------------
# 8.1. Recepcionista: Horarios Disponibles para Reserva Manual
# ------------------------------------------------------------------------------

@rol_requerido('recepcionista', 'administrador')
def horarios_disponibles_recepcion_view(request):
    cancha_id = request.GET.get('cancha')
    fecha_str = request.GET.get('fecha')

    try:
        fecha_obj = date.fromisoformat(fecha_str) if fecha_str else None
    except ValueError:
        fecha_obj = None

    opciones = obtener_opciones_horario_recepcion(cancha_id, fecha_obj)
    mensaje = 'Selecciona cancha y fecha primero.'
    if cancha_id and fecha_str:
        mensaje = 'No hay horarios libres para esa fecha.' if not opciones else 'Horarios encontrados.'

    return JsonResponse({
        'options': [
            {
                'value': value,
                'label': label,
                'hora_inicio': value.split('|')[0],
                'hora_fin': value.split('|')[1],
            }
            for value, label in opciones
        ],
        'message': mensaje,
    })


# ------------------------------------------------------------------------------
# 8.1. Recepcionista: Crear Reserva para Usuario (P1: atomic)
# ------------------------------------------------------------------------------
@rol_requerido('recepcionista', 'administrador')
def crear_reserva_recepcion_view(request):
    usuario_recepcion = request.usuario

    if request.method == 'POST':
        form = ReservaRecepcionForm(request.POST)
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
                            'La cancha ya esta reservada en ese horario.'
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
                    f'Reserva creada para {usuario_cliente.nombre}. '
                    f'Codigo QR: {reserva.codigo_qr}'
                )
                return redirect('calendario_reservas')

            except IntegrityError:
                registrar_error(
                    'crear_reserva_recepcion',
                    'IntegrityError: duplicado concurrente en reserva de recepcion',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya esta reservada en ese horario.'
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
        form = ReservaRecepcionForm(initial=initial)

    return render(request, 'reservas/crear_reserva_recepcion.html', {
        'form': form,
        'usuario': usuario_recepcion,
    })


# ------------------------------------------------------------------------------
# 8.2. Recepcionista: Calendario de Reservas (P7: semanal)
# ------------------------------------------------------------------------------

@rol_requerido('recepcionista', 'administrador')
def calendario_reservas_view(request):
    fecha_str = request.GET.get('fecha')
    vista = request.GET.get('vista', 'diaria')

    if fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_obj = date.today()
    else:
        fecha_obj = date.today()

    if vista == 'semanal':
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


# ------------------------------------------------------------------------------
# 8.3. Recepcionista: Marcar No Asistida
# ------------------------------------------------------------------------------

@rol_requerido('recepcionista', 'administrador')
def marcar_no_asistida_view(request, reserva_id):
    with transaction.atomic():
        reserva = get_object_or_404(Reserva.objects.select_for_update(), id=reserva_id)

        if reserva.estado != 'confirmada':
            messages.error(request, 'Solo se pueden marcar reservas confirmadas.')
        else:
            reserva.estado = 'no_asistida'
            reserva.save(update_fields=['estado'])
            ReservaBloqueo.objects.filter(reserva=reserva).delete()
            messages.success(request, f'Reserva #{reserva.id} marcada como No Asistida.')

    next_url = request.META.get('HTTP_REFERER', 'calendario_reservas')
    return redirect(next_url)


# ------------------------------------------------------------------------------
# 8.4. Recepcionista: Historial General
# ------------------------------------------------------------------------------

@rol_requerido('recepcionista', 'administrador')
def historial_reservas_view(request):
    busqueda = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')
    mes = request.GET.get('mes', '')

    if fecha:
        try:
            fecha_base = date.fromisoformat(fecha)
        except ValueError:
            fecha_base = date.today()
    elif mes:
        try:
            anio, numero_mes = mes.split('-')
            fecha_base = date(int(anio), int(numero_mes), 1)
        except (ValueError, TypeError):
            fecha_base = date.today().replace(day=1)
    else:
        fecha_base = date.today().replace(day=1)

    primer_dia_mes = fecha_base.replace(day=1)
    ultimo_dia_mes = fecha_base.replace(
        day=calendar.monthrange(fecha_base.year, fecha_base.month)[1]
    )

    reservas_qs = Reserva.objects.select_related('cancha', 'usuario').filter(
        fecha__range=[primer_dia_mes, ultimo_dia_mes]
    )

    if busqueda:
        reservas_qs = reservas_qs.filter(
            Q(usuario__nombre__icontains=busqueda) | Q(usuario__correo__icontains=busqueda)
        )

    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
            reservas_qs = reservas_qs.filter(fecha=fecha_obj)
        except ValueError:
            pass

    reservas_qs = reservas_qs.order_by('fecha', 'hora_inicio')
    reservas_lista = list(reservas_qs)

    reservas_por_fecha = {}
    for reserva in reservas_lista:
        reservas_por_fecha.setdefault(reserva.fecha, []).append(reserva)

    calendario_mes = []
    month_matrix = calendar.Calendar(firstweekday=0).monthdatescalendar(
        fecha_base.year, fecha_base.month
    )
    for semana in month_matrix:
        fila = []
        for dia in semana:
            fila.append({
                'fecha': dia,
                'en_mes': dia.month == fecha_base.month,
                'es_hoy': dia == date.today(),
                'reservas': reservas_por_fecha.get(dia, []),
            })
        calendario_mes.append(fila)

    nombres_dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    mes_anterior = (primer_dia_mes - timedelta(days=1)).replace(day=1)
    siguiente_mes = (ultimo_dia_mes + timedelta(days=1)).replace(day=1)

    return render(request, 'reservas/historial_reservas.html', {
        'usuario': request.usuario,
        'busqueda': busqueda,
        'fecha': fecha,
        'mes': fecha_base.strftime('%Y-%m'),
        'fecha_base': fecha_base,
        'mes_label': f"{nombres_meses[fecha_base.month - 1]} {fecha_base.year}",
        'nombres_dias': nombres_dias,
        'calendario_mes': calendario_mes,
        'mes_anterior': mes_anterior.strftime('%Y-%m'),
        'mes_siguiente': siguiente_mes.strftime('%Y-%m'),
        'total_reservas_mes': len(reservas_lista),
    })


# ------------------------------------------------------------------------------
# 8.5. Recepcionista: Imprimir Ticket de Voucher
# ------------------------------------------------------------------------------

def _generar_ticket_voucher_pdf(canje):
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    page_width = 80 * mm
    page_height = 118 * mm
    margin_x = 5 * mm
    y = page_height - (6 * mm)
    line_gap = 4.3 * mm
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    pdf.setTitle(f'Comprobante {canje.codigo}')

    def draw_text(texto, x, y_pos, fuente='Helvetica', tamano=9, color=colors.black):
        pdf.setFont(fuente, tamano)
        pdf.setFillColor(color)
        pdf.drawString(x, y_pos, texto)

    def draw_right(texto, x_right, y_pos, fuente='Helvetica', tamano=9, color=colors.black):
        pdf.setFont(fuente, tamano)
        pdf.setFillColor(color)
        ancho = stringWidth(texto, fuente, tamano)
        pdf.drawString(x_right - ancho, y_pos, texto)

    def separator(y_pos):
        pdf.setStrokeColor(colors.black)
        pdf.setDash(2, 2)
        pdf.line(margin_x, y_pos, page_width - margin_x, y_pos)
        pdf.setDash()

    pdf.setFillColor(colors.HexColor('#f1f5f9'))
    pdf.rect(margin_x, y - 14 * mm, page_width - (2 * margin_x), 12 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.black)
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawCentredString(page_width / 2, y - 5 * mm, 'POLIDEPORTIVO')
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawCentredString(page_width / 2, y - 9.2 * mm, 'COMPROBANTE DE CANJE')
    y -= 17 * mm

    draw_text('Documento:', margin_x, y, 'Helvetica-Bold', 8)
    draw_right(f'CV-{canje.id:05d}', page_width - margin_x, y, 'Helvetica-Bold', 8)
    y -= line_gap
    draw_text('Fecha:', margin_x, y, 'Helvetica-Bold', 8)
    draw_right(canje.fecha.strftime('%d/%m/%Y %H:%M'), page_width - margin_x, y, 'Helvetica', 8)
    y -= line_gap
    draw_text('Cliente:', margin_x, y, 'Helvetica-Bold', 8)
    draw_right(canje.usuario.nombre[:26], page_width - margin_x, y, 'Helvetica', 8)
    y -= line_gap
    draw_text('Canje:', margin_x, y, 'Helvetica-Bold', 8)
    draw_right('Producto de bar', page_width - margin_x, y, 'Helvetica', 8)
    y -= 2.5 * mm

    separator(y)
    y -= 6 * mm

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(margin_x, y, 'DETALLE')
    pdf.drawString(page_width - (28 * mm), y, 'CANT.')
    draw_right('VALOR', page_width - margin_x, y, 'Helvetica-Bold', 8)
    y -= 4 * mm

    pdf.setFont('Helvetica', 8.5)
    pdf.drawString(margin_x, y, canje.producto.nombre[:30])
    pdf.drawString(page_width - (26 * mm), y, '1')
    draw_right(f'{canje.puntos_usados} pts', page_width - margin_x, y, 'Helvetica', 8.5)
    y -= 6 * mm

    separator(y)
    y -= 6 * mm

    draw_text('Subtotal:', margin_x, y, 'Helvetica', 8.5)
    draw_right(f'{canje.puntos_usados} pts', page_width - margin_x, y, 'Helvetica', 8.5)
    y -= line_gap
    draw_text('Metodo:', margin_x, y, 'Helvetica', 8.5)
    draw_right('Canje por puntos', page_width - margin_x, y, 'Helvetica', 8.5)
    y -= line_gap
    draw_text('Total:', margin_x, y, 'Helvetica-Bold', 9.5)
    draw_right(f'{canje.puntos_usados} pts', page_width - margin_x, y, 'Helvetica-Bold', 9.5)
    y -= 2.5 * mm

    separator(y)
    y -= 8 * mm

    pdf.setFillColor(colors.HexColor('#f8fafc'))
    pdf.rect(margin_x, y - 12 * mm, page_width - (2 * margin_x), 11 * mm, fill=1, stroke=1)
    pdf.setFillColor(colors.black)
    pdf.setFont('Helvetica-Bold', 7.5)
    pdf.drawCentredString(page_width / 2, y - 4 * mm, 'CODIGO DE RETIRO')
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawCentredString(page_width / 2, y - 8.5 * mm, canje.codigo)
    y -= 17 * mm

    pdf.setFont('Helvetica', 7.2)
    pdf.drawCentredString(page_width / 2, y, 'Presentar este comprobante en barra para retirar el producto.')
    y -= 3.5 * mm
    pdf.drawCentredString(page_width / 2, y, 'Documento generado automaticamente por el sistema.')

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


@rol_requerido('recepcionista', 'administrador')
def ticket_voucher_view(request, canje_id):
    canje = get_object_or_404(CanjeProducto.objects.select_related('usuario', 'producto'), id=canje_id)
    pdf_bytes = _generar_ticket_voucher_pdf(canje)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ticket_voucher_{canje.codigo}.pdf"'
    return response



