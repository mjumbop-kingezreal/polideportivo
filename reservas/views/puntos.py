"""Vistas del programa de puntos: canje y configuración."""

from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import PuntosHistorial, ConfiguracionPuntos
from ..forms import CanjePuntosForm, ConfiguracionPuntosForm
from .helpers import login_requerido, rol_requerido


# ──────────────────────────────────────────────
# 14. Canjear Puntos (P4: nueva vista)
# ──────────────────────────────────────────────

@login_requerido
def canjear_puntos_view(request):
    """Permite al usuario canjear sus puntos acumulados por beneficios."""
    usuario = request.usuario
    config = ConfiguracionPuntos.obtener()

    if request.method == 'POST':
        form = CanjePuntosForm(request.POST, usuario=usuario)
        if form.is_valid():
            puntos = form.cleaned_data['puntos_a_canjear']

            if puntos < config.minimo_canje:
                messages.error(
                    request,
                    f'El mínimo de puntos para canjear es {config.minimo_canje}.'
                )
            else:
                # Descontar puntos
                usuario.puntos_acumulados -= puntos
                usuario.save()

                # Registrar en historial
                PuntosHistorial.objects.create(
                    usuario=usuario,
                    puntos=puntos,
                    tipo_movimiento='canjeado',
                    descripcion=f'Canje de {puntos} puntos por beneficios.',
                )

                messages.success(
                    request,
                    f'¡Has canjeado {puntos} puntos exitosamente!'
                )
                return redirect('canjear_puntos')
    else:
        form = CanjePuntosForm(usuario=usuario)

    historial = usuario.puntos_historial.order_by('-fecha')[:20]
    return render(request, 'reservas/canjear_puntos.html', {
        'form': form,
        'usuario': usuario,
        'historial': historial,
        'config': config,
    })


# ──────────────────────────────────────────────
# 15. Admin: Configuración de Puntos (P10)
# ──────────────────────────────────────────────

@rol_requerido('administrador', 'municipio')
def admin_config_puntos_view(request):
    """Panel para configurar las reglas del programa de puntos."""
    config = ConfiguracionPuntos.obtener()

    if request.method == 'POST':
        form = ConfiguracionPuntosForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de puntos actualizada correctamente.')
            return redirect('admin_config_puntos')
    else:
        form = ConfiguracionPuntosForm(instance=config)

    usuario = request.usuario
    return render(request, 'reservas/admin_config_puntos.html', {
        'form': form,
        'config': config,
        'usuario': usuario,
    })
