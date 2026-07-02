"""Funciones auxiliares y decoradores de control de acceso.

Contiene:
- registrar_error: Registra errores en LogErrores para auditoría.
- login_requerido: Decorador que verifica sesión activa.
- rol_requerido: Decorador que verifica rol del usuario.
- obtener_usuario: Obtiene el usuario desde la sesión.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from ..models import Usuario, LogErrores


# ──────────────────────────────────────────────
# Función auxiliar para registrar errores (P3)
# ──────────────────────────────────────────────

def registrar_error(modulo, descripcion, nivel='error'):
    """Registra un error en la tabla LogErrores para auditoría."""
    try:
        LogErrores.objects.create(
            modulo_origen=modulo,
            descripcion_error=descripcion,
            nivel_severidad=nivel,
        )
    except Exception:
        pass  # Evitar errores recursivos al intentar loggear


# ──────────────────────────────────────────────
# Decoradores de control de acceso
# ──────────────────────────────────────────────

def login_requerido(view_func):
    """Verifica que haya un usuario en sesión activa."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('login')
        # Verificar que el usuario sigue activo en BD
        try:
            usuario = Usuario.objects.get(
                id=request.session['usuario_id'], estado='activo'
            )
        except Usuario.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Tu cuenta ha sido desactivada.')
            return redirect('login')
        request.usuario = usuario
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_requerido(*roles):
    """Verifica que el usuario tenga uno de los roles indicados."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'usuario_id' not in request.session:
                messages.warning(request, 'Debes iniciar sesión.')
                return redirect('login')
            try:
                usuario = Usuario.objects.get(
                    id=request.session['usuario_id'], estado='activo'
                )
            except Usuario.DoesNotExist:
                request.session.flush()
                messages.error(request, 'Tu cuenta ha sido desactivada.')
                return redirect('login')
            if usuario.rol not in roles:
                return HttpResponseForbidden(
                    '<h2 style="font-family:sans-serif;padding:2rem;color:#b91c1c">'
                    '⛔ No tienes permiso para acceder a esta página.</h2>'
                )
            request.usuario = usuario
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def obtener_usuario(request):
    """Obtiene el usuario desde la sesión."""
    uid = request.session.get('usuario_id')
    if uid:
        try:
            return Usuario.objects.get(id=uid)
        except Usuario.DoesNotExist:
            pass
    return None
