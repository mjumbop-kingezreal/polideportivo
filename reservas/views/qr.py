"""Vista de generación de código QR."""

import io
import qrcode
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from ..models import Reserva
from .helpers import login_requerido


# ──────────────────────────────────────────────
# Generador de Código QR (Imagen)
# ──────────────────────────────────────────────

@login_requerido
def generar_qr_view(request, codigo_qr):
    """Genera y devuelve la imagen del código QR a partir de la cadena."""
    # Opcional: Validar que la reserva exista, aunque aquí solo generamos el QR visual
    get_object_or_404(Reserva, codigo_qr=codigo_qr)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type="image/png")
