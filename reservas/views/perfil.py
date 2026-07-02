"""Vista del perfil de usuario."""

from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import EditarPerfilForm
from .helpers import login_requerido


# ──────────────────────────────────────────────
# 12. Perfil de usuario
# ──────────────────────────────────────────────

@login_requerido
def perfil_view(request):
    """Permite al usuario ver y editar sus datos personales."""
    usuario = request.usuario

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            # Actualizar nombre en sesión
            request.session['usuario_nombre'] = usuario.nombre
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        form = EditarPerfilForm(instance=usuario)

    historial = usuario.puntos_historial.order_by('-fecha')[:10]
    return render(request, 'reservas/perfil.html', {
        'usuario': usuario,
        'form': form,
        'historial': historial,
    })
