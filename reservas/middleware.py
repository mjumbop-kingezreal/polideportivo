"""
Middleware global de excepciones para el sistema de polideportivo.
Captura excepciones no manejadas y las registra en la tabla LogErrores.
"""

import traceback
from django.http import HttpResponseServerError
from .models import LogErrores


class ExceptionLoggingMiddleware:
    """
    Middleware que captura excepciones no manejadas en las vistas
    y las registra en la tabla log_errores para auditoría.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Se ejecuta cuando una vista lanza una excepción no capturada.
        Registra el error en LogErrores y devuelve una respuesta 500 amigable.
        """
        from django.http import Http404
        if isinstance(exception, Http404):
            return None  # Let Django handle 404s properly
        # Obtener información del error
        modulo = request.path
        descripcion = (
            f'Excepción no manejada: {type(exception).__name__}: {str(exception)}\n'
            f'Método: {request.method}\n'
            f'Usuario ID: {request.session.get("usuario_id", "anónimo")}\n'
            f'Traceback:\n{traceback.format_exc()}'
        )

        # Registrar en la base de datos
        try:
            LogErrores.objects.create(
                modulo_origen=modulo[:100],  # Limitar a 100 chars
                descripcion_error=descripcion,
                nivel_severidad='critical',
            )
        except Exception:
            pass  # Evitar errores recursivos

        # En modo DEBUG, dejar que Django muestre su página de error detallada
        from django.conf import settings
        if settings.DEBUG:
            return None  # Django mostrará la página de debug estándar

        # En producción, mostrar un mensaje amigable
        return HttpResponseServerError(
            '<div style="font-family:sans-serif;padding:3rem;text-align:center;'
            'background:#1a1a2e;color:#e0e0e0;min-height:100vh;display:flex;'
            'flex-direction:column;justify-content:center;align-items:center;">'
            '<h1 style="color:#ff5252;font-size:2rem;">⚠️ Error del Sistema</h1>'
            '<p style="margin-top:1rem;color:#aaa;max-width:500px;">'
            'Ocurrió un problema al procesar su solicitud. '
            'El error ha sido registrado y nuestro equipo lo revisará.'
            '</p>'
            '<a href="/" style="margin-top:2rem;color:#7c4dff;text-decoration:none;">'
            'Volver al inicio</a>'
            '</div>'
        )
