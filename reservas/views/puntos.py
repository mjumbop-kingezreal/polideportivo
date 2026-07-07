"""Vistas del programa de puntos: canje y configuracion."""

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..codigos import generar_codigo_voucher
from ..forms import ConfiguracionPuntosForm
from ..models import CanjeProducto, ConfiguracionPuntos, ProductoBar, PuntosHistorial, Usuario
from .helpers import login_requerido, rol_requerido


CATALOGO_CATEGORIAS = (
    ('bebida', 'Bebidas', 'bi-cup-straw'),
    ('snack', 'Snacks', 'bi-cookie'),
    ('otro', 'Otros', 'bi-gift'),
)


@login_requerido
def canjear_puntos_view(request):
    """Muestra el catalogo, el voucher activo y el historial de canjes."""
    usuario = request.usuario
    productos = list(
        ProductoBar.objects.filter(
            disponible=True,
        ).filter(
            Q(stock__isnull=True) | Q(stock__gt=0)
        ).order_by('categoria', 'puntos_requeridos', 'nombre')
    )
    for producto in productos:
        producto.puede_canjear = producto.puntos_requeridos <= usuario.puntos_acumulados
        producto.puntos_faltantes = max(producto.puntos_requeridos - usuario.puntos_acumulados, 0)

    catalogo = []
    for clave, etiqueta, icono in CATALOGO_CATEGORIAS:
        items = [producto for producto in productos if producto.categoria == clave]
        catalogo.append({
            'clave': clave,
            'etiqueta': etiqueta,
            'icono': icono,
            'productos': items,
            'cantidad': len(items),
        })

    historial = list(
        CanjeProducto.objects.filter(usuario=usuario)
        .select_related('producto')
        .order_by('-fecha')[:20]
    )
    canjes_vigentes = [canje for canje in historial if canje.esta_vigente]
    canje_activo = canjes_vigentes[0] if canjes_vigentes else None

    return render(request, 'reservas/canjear_puntos.html', {
        'usuario': usuario,
        'catalogo': catalogo,
        'historial': historial,
        'canje_activo': canje_activo,
        'productos_disponibles': len(productos),
        'canjes_vigentes_count': len(canjes_vigentes),
        'canjes_caducados_count': len(historial) - len(canjes_vigentes),
    })


@login_requerido
def canjear_producto_view(request, producto_id):
    """Procesa el canje de un producto especifico y genera el voucher."""
    if request.method != 'POST':
        return redirect('canjear_puntos')

    usuario = request.usuario
    producto = get_object_or_404(ProductoBar, id=producto_id)

    with transaction.atomic():
        usuario_actual = Usuario.objects.select_for_update().get(id=usuario.id)
        producto_actual = ProductoBar.objects.select_for_update().get(id=producto.id)

        if not producto_actual.disponible:
            messages.error(request, f'{producto_actual.nombre} no esta disponible para canje en este momento.')
            return redirect('canjear_puntos')

        if not producto_actual.tiene_stock:
            messages.error(request, f'{producto_actual.nombre} no tiene stock disponible en este momento.')
            return redirect('canjear_puntos')

        if producto_actual.puntos_requeridos > usuario_actual.puntos_acumulados:
            messages.error(
                request,
                f'No tienes suficientes puntos para canjear {producto_actual.nombre}. '
                f'Requieres {producto_actual.puntos_requeridos} pts pero tienes {usuario_actual.puntos_acumulados}.'
            )
            return redirect('canjear_puntos')

        usuario_actual.puntos_acumulados -= producto_actual.puntos_requeridos
        usuario_actual.save(update_fields=['puntos_acumulados'])

        if producto_actual.stock is not None:
            producto_actual.stock -= 1
            producto_actual.save(update_fields=['stock'])

        canje = CanjeProducto.objects.create(
            usuario=usuario_actual,
            producto=producto_actual,
            puntos_usados=producto_actual.puntos_requeridos,
            codigo=generar_codigo_voucher(),
            estado=CanjeProducto.Estado.PENDIENTE,
        )

        PuntosHistorial.objects.create(
            usuario=usuario_actual,
            puntos=producto_actual.puntos_requeridos,
            tipo_movimiento=PuntosHistorial.TipoMovimiento.CANJEADO,
            descripcion=f'Canje de producto: {producto_actual.nombre}',
        )

        messages.success(
            request,
            f'Canje realizado: {producto_actual.nombre}. Tu codigo es {canje.codigo} y vence el {canje.fecha_caducidad:%d/%m/%Y}.'
        )

    return redirect('canjear_puntos')


@rol_requerido('administrador', 'municipio')
def admin_config_puntos_view(request):
    """Panel para configurar las reglas del programa de puntos."""
    config = ConfiguracionPuntos.obtener()

    if request.method == 'POST':
        form = ConfiguracionPuntosForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuracion de puntos actualizada correctamente.')
            return redirect('admin_config_puntos')
    else:
        form = ConfiguracionPuntosForm(instance=config)

    usuario = request.usuario
    return render(request, 'reservas/admin_config_puntos.html', {
        'form': form,
        'config': config,
        'usuario': usuario,
    })
