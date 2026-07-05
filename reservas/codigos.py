"""Utilidades para generar y clasificar codigos de acceso y vouchers."""

import uuid

from django.utils.crypto import get_random_string

from .models import CanjeProducto, Reserva


PREFIJO_ACCESO = 'ACC-'
PREFIJO_VOUCHER = 'VCH-'


def normalizar_codigo(codigo):
    """Limpia espacios para evitar fallos por escaneos con saltos de linea."""
    return (codigo or '').strip()


def identificar_tipo_codigo(codigo):
    """Intenta inferir el tipo de codigo por su prefijo."""
    codigo_normalizado = normalizar_codigo(codigo).upper()

    if codigo_normalizado.startswith(PREFIJO_ACCESO):
        return 'acceso'
    if codigo_normalizado.startswith(PREFIJO_VOUCHER):
        return 'voucher'
    return 'desconocido'


def generar_codigo_acceso():
    """Genera un codigo legible para reservas con prefijo de acceso."""
    while True:
        codigo = f'{PREFIJO_ACCESO}{uuid.uuid4().hex[:10].upper()}'
        if not Reserva.objects.filter(codigo_qr=codigo).exists():
            return codigo


def generar_codigo_voucher():
    """Genera un codigo legible para vouchers con prefijo de voucher."""
    caracteres = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    while True:
        codigo = f'{PREFIJO_VOUCHER}{get_random_string(6, caracteres)}'
        if not CanjeProducto.objects.filter(codigo=codigo).exists():
            return codigo
