"""Vista del perfil de usuario."""

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from ..forms import EditarPerfilForm
from .helpers import login_requerido


# 12. Perfil de usuario
@login_requerido
def perfil_view(request):
    """Permite al usuario ver y editar sus datos personales."""
    usuario = request.usuario

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            # Actualizar nombre en sesion
            request.session['usuario_nombre'] = usuario.nombre
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        form = EditarPerfilForm(instance=usuario)

    reservas = usuario.reservas.all()
    hoy = timezone.localdate()
    resumen = {
        'reservas_total': reservas.count(),
        'reservas_asistidas': reservas.filter(estado='asistida').count(),
        'proximas_reservas': reservas.filter(estado='confirmada', fecha__gte=hoy).count(),
    }

    return render(request, 'reservas/perfil.html', {
        'usuario': usuario,
        'form': form,
        'resumen': resumen,
    })
