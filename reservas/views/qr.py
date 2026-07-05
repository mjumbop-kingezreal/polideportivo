"""Vista de generacion de codigos QR."""

import io

import qrcode
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404

from ..models import CanjeProducto, Reserva
from .helpers import login_requerido


@login_requerido
def generar_qr_view(request, codigo_qr):
    """Genera y devuelve la imagen del codigo QR de una reserva autorizada."""
    reserva = get_object_or_404(Reserva, codigo_qr=codigo_qr)
    usuario = request.usuario

    puede_ver = (
        reserva.usuario_id == usuario.id or
        usuario.rol in ['recepcionista', 'administrador']
    )
    if not puede_ver:
        return HttpResponseForbidden('No tienes permiso para ver este codigo QR.')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')


@login_requerido
def generar_voucher_qr_view(request, codigo_voucher):
    """Genera y devuelve la imagen QR del voucher para mostrarlo al usuario."""
    canje = get_object_or_404(CanjeProducto.objects.select_related('usuario'), codigo=codigo_voucher)
    usuario = request.usuario

    puede_ver = (
        canje.usuario_id == usuario.id or
        usuario.rol in ['recepcionista', 'administrador']
    )
    if not puede_ver:
        return HttpResponseForbidden('No tienes permiso para ver este voucher.')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(codigo_voucher)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')
