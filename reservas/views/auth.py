"""Vistas de autenticación: login, registro, logout."""

from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import LoginForm, RegistroForm
from .helpers import registrar_error


# ──────────────────────────────────────────────
# 1. Login
# ──────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.rol

            messages.success(request, f'¡Bienvenido, {usuario.nombre}!')

            # Redirigir según rol (P6: incluye municipio)
            if usuario.rol == 'administrador':
                return redirect('admin_usuarios')
            elif usuario.rol == 'municipio':
                return redirect('reportes')
            elif usuario.rol == 'recepcionista':
                return redirect('validar_qr')
            else:
                return redirect('lista_canchas')
        else:
            # P3: Registrar intentos fallidos de login
            correo = request.POST.get('correo', 'desconocido')
            registrar_error(
                'login',
                f'Intento fallido de login para correo: {correo}',
                nivel='warning'
            )
    else:
        form = LoginForm()

    return render(request, 'reservas/login.html', {'form': form})


# ──────────────────────────────────────────────
# 2. Registro
# ──────────────────────────────────────────────

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Inicia sesión.')
            return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'reservas/registro.html', {'form': form})


# ──────────────────────────────────────────────
# 3. Logout
# ──────────────────────────────────────────────

def logout_view(request):
    request.session.flush()
    messages.info(request, 'Sesión cerrada.')
    return redirect('login')
