"""Vistas de administración: gestión de canchas, horarios y usuarios."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Cancha, HorarioDisponible, Usuario
from ..forms import CanchaForm, HorarioDisponibleForm, EditarRolForm
from .helpers import rol_requerido


# ──────────────────────────────────────────────
# 9. Admin: Gestión de canchas
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def admin_canchas_view(request):
    canchas_list = Cancha.objects.all()
    cancha_editar = None

    # Editar cancha existente
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

    # Paginación: 15 canchas por página
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


# ──────────────────────────────────────────────
# 10. Admin: Gestión de horarios
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def admin_horarios_view(request):
    horarios_list = HorarioDisponible.objects.select_related('cancha').all()
    horario_editar = None

    edit_id = request.GET.get('editar')
    if edit_id:
        horario_editar = get_object_or_404(HorarioDisponible, id=edit_id)

    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        if horario_id:
            instancia = get_object_or_404(HorarioDisponible, id=horario_id)
            form = HorarioDisponibleForm(request.POST, instance=instancia)
        else:
            form = HorarioDisponibleForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Horario guardado correctamente.')
            return redirect('admin_horarios')
    else:
        form = HorarioDisponibleForm(instance=horario_editar) if horario_editar else HorarioDisponibleForm()

    # Paginación: 15 horarios por página
    paginator = Paginator(horarios_list, 15)
    page_number = request.GET.get('page')
    horarios = paginator.get_page(page_number)

    usuario = request.usuario
    return render(request, 'reservas/admin_horarios.html', {
        'horarios': horarios,
        'form': form,
        'horario_editar': horario_editar,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 13. Admin: Gestión de usuarios y roles
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def admin_usuarios_view(request):
    """Panel de administración de usuarios y asignación de roles."""
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
                messages.error(request, 'Rol inválido.')

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

    # Paginación: 15 usuarios por página
    paginator = Paginator(usuarios_list, 15)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)

    usuario = request.usuario
    return render(request, 'reservas/admin_usuarios.html', {
        'usuarios': usuarios,
        'usuario': usuario,
        'rol_form_class': EditarRolForm,
    })
