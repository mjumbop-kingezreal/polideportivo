"""Funciones auxiliares y decoradores de control de acceso."""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from ..models import Usuario, LogErrores, ReservaBloqueo


def registrar_error(modulo, descripcion, nivel='error'):
    """Registra un error en la tabla LogErrores para auditoria."""
    try:
        LogErrores.objects.create(
            modulo_origen=modulo,
            descripcion_error=descripcion,
            nivel_severidad=nivel,
        )
    except Exception:
        pass


def limpiar_bloqueos_vencidos():
    """Elimina bloqueos de reserva que ya terminaron para evitar crecimiento innecesario."""
    try:
        today_date = timezone.localdate()
        now_time = timezone.localtime(timezone.now()).time()
        ReservaBloqueo.objects.filter(
            Q(fecha__lt=today_date) |
            Q(fecha=today_date, hora_fin__lte=now_time)
        ).delete()
    except Exception:
        pass


def login_requerido(view_func):
    """Verifica que haya un usuario en sesion activa."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.warning(request, 'Debes iniciar sesion.')
            return redirect('login')
        try:
            usuario = Usuario.objects.get(
                id=request.session['usuario_id'], estado='activo'
            )
        except Usuario.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Tu cuenta ha sido desactivada.')
            return redirect('login')
        request.usuario = usuario
        limpiar_bloqueos_vencidos()
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_requerido(*roles):
    """Verifica que el usuario tenga uno de los roles indicados."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'usuario_id' not in request.session:
                messages.warning(request, 'Debes iniciar sesion.')
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
                    'No tienes permiso para acceder a esta pagina.</h2>'
                )
            request.usuario = usuario
            limpiar_bloqueos_vencidos()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

