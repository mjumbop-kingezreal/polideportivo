"""Vistas de administracion: gestion de canchas, horarios y usuarios."""

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from ..models import Cancha, HorarioDisponible, Usuario, ProductoBar
from ..forms import CanchaForm, EditarRolForm, ProductoBarForm
from .helpers import rol_requerido


def _parse_time(value):
    return datetime.strptime(value, '%H:%M').time()


@rol_requerido('administrador')
def admin_canchas_view(request):
    canchas_list = Cancha.objects.all().order_by('nombre')
    cancha_editar = None

    edit_id = request.GET.get('editar')
    if edit_id:
        cancha_editar = get_object_or_404(Cancha, id=edit_id)

    if request.method == 'POST':
        cancha_id = request.POST.get('cancha_id')
        if cancha_id:
            instancia = get_object_or_404(Cancha, id=cancha_id)
            form = CanchaForm(request.POST, instance=instancia)
        else:
            form = CanchaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cancha guardada correctamente.')
            return redirect('admin_canchas')
    else:
        form = CanchaForm(instance=cancha_editar) if cancha_editar else CanchaForm()

    paginator = Paginator(canchas_list, 15)
    page_number = request.GET.get('page')
    canchas = paginator.get_page(page_number)

    usuario = request.usuario
    return render(request, 'reservas/admin_canchas.html', {
        'canchas': canchas,
        'form': form,
        'cancha_editar': cancha_editar,
        'usuario': usuario,
    })


@rol_requerido('administrador')
def admin_horarios_view(request):
    canchas_catalogo = Cancha.objects.all().order_by('nombre')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'generar_horarios':
            cancha_id = request.POST.get('cancha_generador')
            dias = [int(dia) for dia in request.POST.getlist('dias') if dia]
            hora_inicio = request.POST.get('hora_inicio_generador')
            hora_fin = request.POST.get('hora_fin_generador')

            try:
                if not cancha_id:
                    raise ValueError('Selecciona una cancha.')
                if not dias:
                    raise ValueError('Selecciona al menos un dia.')
                inicio = _parse_time(hora_inicio)
                fin = _parse_time(hora_fin)
                if fin <= inicio:
                    raise ValueError('La hora fin debe ser mayor a la hora inicio.')

                creados = 0
                reactivados = 0
                existentes = 0
                with transaction.atomic():
                    for dia in dias:
                        horario, creado = HorarioDisponible.objects.get_or_create(
                            cancha_id=cancha_id,
                            dia_semana=dia,
                            hora_inicio=inicio,
                            hora_fin=fin,
                            defaults={'activo': True},
                        )
                        if creado:
                            creados += 1
                        elif not horario.activo:
                            horario.activo = True
                            horario.save(update_fields=['activo'])
                            reactivados += 1
                        else:
                            existentes += 1

                messages.success(
                    request,
                    f'Se guardaron los horarios tal como los definiste. Nuevos: {creados}, reactivados: {reactivados}, ya existentes: {existentes}.'
                )
                return redirect('admin_horarios')
            except ValueError as exc:
                messages.error(request, str(exc))

        elif accion == 'eliminar_horario':
            horario = get_object_or_404(HorarioDisponible, id=request.POST.get('horario_id'))
            horario.delete()
            messages.success(request, 'Horario eliminado correctamente.')
            return redirect('admin_horarios')

    horarios_activos = list(HorarioDisponible.objects.select_related('cancha').filter(activo=True).order_by(
        'cancha__nombre', 'dia_semana', 'hora_inicio'
    ))

    horarios_agrupados = []
    for cancha in canchas_catalogo:
        cancha_horarios = [h for h in horarios_activos if h.cancha_id == cancha.id]
        if not cancha_horarios:
            continue

        dias_configurados = []
        for valor, nombre in HorarioDisponible.DiaSemana.choices:
            bloques = [h for h in cancha_horarios if h.dia_semana == valor]
            if bloques:
                dias_configurados.append({
                    'nombre': nombre,
                    'bloques': bloques,
                })

        horarios_agrupados.append({
            'cancha': cancha,
            'dias': dias_configurados,
        })

    usuario = request.usuario
    return render(request, 'reservas/admin_horarios.html', {
        'usuario': usuario,
        'canchas_catalogo': canchas_catalogo,
        'dia_choices': HorarioDisponible.DiaSemana.choices,
        'horarios_agrupados': horarios_agrupados,
    })


@rol_requerido('administrador')
def admin_usuarios_view(request):
    """Panel de administracion de usuarios y asignacion de roles."""
    usuarios_list = Usuario.objects.all().order_by('-fecha_creacion')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        usuario_id = request.POST.get('usuario_id')

        if not usuario_id:
            messages.error(request, 'Usuario no especificado.')
            return redirect('admin_usuarios')

        try:
            usuario_obj = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('admin_usuarios')

        if accion == 'cambiar_rol':
            form = EditarRolForm(request.POST, instance=usuario_obj)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    f'Rol de {usuario_obj.nombre} actualizado a '
                    f'{usuario_obj.get_rol_display()}.'
                )
            else:
                messages.error(request, 'Rol invalido.')

        elif accion == 'toggle_estado':
            if usuario_obj.id == request.session.get('usuario_id'):
                messages.error(request, 'No puedes desactivar tu propia cuenta.')
            else:
                if usuario_obj.estado == 'activo':
                    usuario_obj.estado = 'inactivo'
                    msg = f'Usuario {usuario_obj.nombre} desactivado.'
                else:
                    usuario_obj.estado = 'activo'
                    msg = f'Usuario {usuario_obj.nombre} activado.'
                usuario_obj.save()
                messages.success(request, msg)

        return redirect('admin_usuarios')

    paginator = Paginator(usuarios_list, 15)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)

    usuario = request.usuario
    return render(request, 'reservas/admin_usuarios.html', {
        'usuarios': usuarios,
        'usuario': usuario,
        'rol_form_class': EditarRolForm,
    })


@rol_requerido('administrador')
def admin_productos_bar_view(request):
    """Panel de administración para productos del bar (Puntos)."""
    productos_list = ProductoBar.objects.all().order_by('categoria', 'puntos_requeridos')
    producto_editar = None

    edit_id = request.GET.get('editar')
    if edit_id:
        producto_editar = get_object_or_404(ProductoBar, id=edit_id)

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        if producto_id:
            instancia = get_object_or_404(ProductoBar, id=producto_id)
            form = ProductoBarForm(request.POST, instance=instancia)
        else:
            form = ProductoBarForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Producto del bar guardado correctamente.')
            return redirect('admin_productos_bar')
    else:
        form = ProductoBarForm(instance=producto_editar) if producto_editar else ProductoBarForm()

    paginator = Paginator(productos_list, 15)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    usuario = request.usuario
    return render(request, 'reservas/admin_productos_bar.html', {
        'productos': productos,
        'form': form,
        'producto_editar': producto_editar,
        'usuario': usuario,
    })