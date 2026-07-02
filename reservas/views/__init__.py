"""Views package del sistema de reservas del polideportivo.

Este paquete reorganiza las vistas en módulos por responsabilidad.
Todas las vistas se re-exportan aquí para mantener compatibilidad
con urls.py (from . import views → views.login_view, etc.).
"""

from .auth import login_view, registro_view, logout_view
from .canchas import lista_canchas_view, disponibilidad_view
from .reservas_views import crear_reserva_view, mis_reservas_view, cancelar_reserva_view
from .recepcion import (
    validar_qr_view, crear_reserva_recepcion_view,
    calendario_reservas_view, marcar_no_asistida_view,
    historial_reservas_view,
)
from .admin_views import admin_canchas_view, admin_horarios_view, admin_usuarios_view
from .puntos import canjear_puntos_view, admin_config_puntos_view
from .reportes import reportes_view, exportar_pdf_view, exportar_excel_view
from .qr import generar_qr_view
from .perfil import perfil_view

__all__ = [
    'login_view', 'registro_view', 'logout_view',
    'lista_canchas_view', 'disponibilidad_view',
    'crear_reserva_view', 'mis_reservas_view', 'cancelar_reserva_view',
    'validar_qr_view', 'crear_reserva_recepcion_view',
    'calendario_reservas_view', 'marcar_no_asistida_view',
    'historial_reservas_view',
    'admin_canchas_view', 'admin_horarios_view', 'admin_usuarios_view',
    'canjear_puntos_view', 'admin_config_puntos_view',
    'reportes_view', 'exportar_pdf_view', 'exportar_excel_view',
    'generar_qr_view', 'perfil_view',
]
