# Guía de Implementación — Vistas y Formularios

Guía completa paso a paso para implementar todo lo descrito en [Vistas y Formularios.md]
---

## Paso 0: Instalar dependencia

Ejecuta en tu terminal (con el venv activado):

```bash
pip install qrcode[pil]
```

Esto permite generar los códigos QR de las reservas.

---

## Paso 1: Crear `reservas/forms.py`

Crea el archivo [forms.py] con los 7 formularios:

```python
from django import forms
from django.contrib.auth.hashers import check_password
from .models import Usuario, Cancha, HorarioDisponible, Reserva


class LoginForm(forms.Form):
    """Formulario de inicio de sesión."""
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get('correo')
        password = cleaned_data.get('password')

        if correo and password:
            try:
                usuario = Usuario.objects.get(correo=correo, estado='activo')
            except Usuario.DoesNotExist:
                raise forms.ValidationError('Correo o contraseña incorrectos.')

            if not check_password(password, usuario.password):
                raise forms.ValidationError('Correo o contraseña incorrectos.')

            cleaned_data['usuario'] = usuario

        return cleaned_data


class RegistroForm(forms.ModelForm):
    """Formulario de registro de usuario."""
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña (mínimo 8 caracteres)',
        })
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
        })
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')

        if password and confirmar and password != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.password = self.cleaned_data['password']  # se cifra en el modelo
        usuario.rol = 'usuario'
        if commit:
            usuario.save()
        return usuario


class CanchaForm(forms.ModelForm):
    """Formulario para crear/editar canchas."""

    class Meta:
        model = Cancha
        fields = ['nombre', 'tipo_deporte', 'ubicacion', 'estado', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_deporte': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }


class HorarioDisponibleForm(forms.ModelForm):
    """Formulario para crear/editar horarios disponibles."""

    class Meta:
        model = HorarioDisponible
        fields = ['cancha', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'cancha': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('hora_inicio')
        fin = cleaned_data.get('hora_fin')

        if inicio and fin and fin <= inicio:
            raise forms.ValidationError(
                'La hora de fin debe ser mayor que la hora de inicio.'
            )

        return cleaned_data


class ReservaForm(forms.Form):
    """Formulario para crear una reserva."""
    cancha = forms.ModelChoiceField(
        queryset=Cancha.objects.filter(estado='disponible'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
        })
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
        })
    )
    observacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Observación (opcional)',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        cancha = cleaned_data.get('cancha')
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise forms.ValidationError(
                'La hora de fin debe ser mayor que la de inicio.'
            )

        # Verificar que no exista reserva duplicada
        if cancha and fecha and hora_inicio and hora_fin:
            existe = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado='confirmada',
            ).exists()
            if existe:
                raise forms.ValidationError(
                    'Ya existe una reserva para esa cancha en ese horario.'
                )

        return cleaned_data


class ValidacionQRForm(forms.Form):
    """Formulario para validar código QR."""
    codigo_qr = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escanear o ingresar código QR',
        })
    )


class CanjePuntosForm(forms.Form):
    """Formulario para canjear puntos."""
    puntos_a_canjear = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cantidad de puntos',
        })
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_puntos_a_canjear(self):
        puntos = self.cleaned_data['puntos_a_canjear']
        if self.usuario and puntos > self.usuario.puntos_acumulados:
            raise forms.ValidationError(
                f'No tienes suficientes puntos. Tienes {self.usuario.puntos_acumulados}.'
            )
        return puntos
```

---

## Paso 2: Actualizar `reservas/views.py`

Reemplaza **todo** el contenido de [views.py] con:

```python
import uuid
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import (
    Usuario, Cancha, HorarioDisponible,
    Reserva, PuntosHistorial, LogErrores,
)
from .forms import (
    LoginForm, RegistroForm, CanchaForm,
    HorarioDisponibleForm, ReservaForm,
    ValidacionQRForm, CanjePuntosForm,
)


# ──────────────────────────────────────────────
# Decoradores de control de acceso
# ──────────────────────────────────────────────

def login_requerido(view_func):
    """Verifica que haya un usuario en sesión."""
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_requerido(*roles):
    """Verifica que el usuario tenga uno de los roles indicados."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if 'usuario_id' not in request.session:
                return redirect('login')
            try:
                usuario = Usuario.objects.get(id=request.session['usuario_id'])
            except Usuario.DoesNotExist:
                return redirect('login')
            if usuario.rol not in roles:
                return HttpResponseForbidden('No tienes permiso para esta acción.')
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

            # Redirigir según rol
            if usuario.rol == 'administrador':
                return redirect('admin_canchas')
            elif usuario.rol == 'recepcionista':
                return redirect('validar_qr')
            else:
                return redirect('lista_canchas')
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


# ──────────────────────────────────────────────
# 4. Lista de canchas
# ──────────────────────────────────────────────

@login_requerido
def lista_canchas_view(request):
    canchas = Cancha.objects.all()

    # Filtros opcionales
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')

    if tipo:
        canchas = canchas.filter(tipo_deporte=tipo)
    if estado:
        canchas = canchas.filter(estado=estado)

    usuario = obtener_usuario(request)
    return render(request, 'reservas/lista_canchas.html', {
        'canchas': canchas,
        'usuario': usuario,
        'tipos': Cancha.TipoDeporte.choices,
        'estados': Cancha.Estado.choices,
        'filtro_tipo': tipo or '',
        'filtro_estado': estado or '',
    })


# ──────────────────────────────────────────────
# 5. Disponibilidad
# ──────────────────────────────────────────────

@login_requerido
def disponibilidad_view(request):
    cancha_id = request.GET.get('cancha')
    fecha_str = request.GET.get('fecha')
    cancha = None
    horarios = []
    reservas_existentes = []

    canchas_disponibles = Cancha.objects.filter(estado='disponible')

    if cancha_id and fecha_str:
        try:
            cancha = Cancha.objects.get(id=cancha_id)
            fecha_obj = date.fromisoformat(fecha_str)
            dia_semana = fecha_obj.isoweekday()  # 1=Lunes, 7=Domingo

            horarios = HorarioDisponible.objects.filter(
                cancha=cancha,
                dia_semana=dia_semana,
                activo=True,
            )

            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha_obj,
                estado='confirmada',
            ).values_list('hora_inicio', 'hora_fin')

        except (Cancha.DoesNotExist, ValueError):
            messages.error(request, 'Cancha o fecha inválida.')

    usuario = obtener_usuario(request)
    return render(request, 'reservas/disponibilidad.html', {
        'canchas': canchas_disponibles,
        'cancha_sel': cancha,
        'fecha': fecha_str or '',
        'horarios': horarios,
        'reservas_existentes': list(reservas_existentes),
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 6. Crear reserva
# ──────────────────────────────────────────────

@login_requerido
def crear_reserva_view(request):
    usuario = obtener_usuario(request)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = Reserva(
                usuario=usuario,
                cancha=form.cleaned_data['cancha'],
                fecha=form.cleaned_data['fecha'],
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                observacion=form.cleaned_data.get('observacion', ''),
                codigo_qr=str(uuid.uuid4()),
                estado='confirmada',
            )
            reserva.save()

            # Otorgar puntos
            PuntosHistorial.objects.create(
                usuario=usuario,
                reserva=reserva,
                puntos=10,
                tipo_movimiento='otorgado',
                descripcion='Puntos por nueva reserva.',
            )
            usuario.puntos_acumulados += 10
            usuario.save()

            messages.success(
                request,
                f'Reserva creada. Tu código QR es: {reserva.codigo_qr}'
            )
            return redirect('mis_reservas')
    else:
        # Pre-cargar datos desde query params si vienen de disponibilidad
        initial = {}
        if request.GET.get('cancha'):
            initial['cancha'] = request.GET.get('cancha')
        if request.GET.get('fecha'):
            initial['fecha'] = request.GET.get('fecha')
        if request.GET.get('hora_inicio'):
            initial['hora_inicio'] = request.GET.get('hora_inicio')
        if request.GET.get('hora_fin'):
            initial['hora_fin'] = request.GET.get('hora_fin')
        form = ReservaForm(initial=initial)

    return render(request, 'reservas/crear_reserva.html', {
        'form': form,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 7. Mis reservas + Cancelar
# ──────────────────────────────────────────────

@login_requerido
def mis_reservas_view(request):
    usuario = obtener_usuario(request)
    reservas = Reserva.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'usuario': usuario,
    })


@login_requerido
def cancelar_reserva_view(request, reserva_id):
    usuario = obtener_usuario(request)
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario)

    if reserva.estado != 'confirmada':
        messages.error(request, 'Solo puedes cancelar reservas confirmadas.')
    else:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')

    return redirect('mis_reservas')


# ──────────────────────────────────────────────
# 8. Validar QR (recepcionista)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def validar_qr_view(request):
    resultado = None

    if request.method == 'POST':
        form = ValidacionQRForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo_qr']
            try:
                reserva = Reserva.objects.get(codigo_qr=codigo)

                if reserva.estado != 'confirmada':
                    resultado = {
                        'valido': False,
                        'mensaje': f'La reserva está {reserva.get_estado_display()}.',
                    }
                elif reserva.fecha < date.today():
                    resultado = {
                        'valido': False,
                        'mensaje': 'La reserva ya venció (fecha pasada).',
                    }
                else:
                    resultado = {
                        'valido': True,
                        'mensaje': 'Acceso autorizado.',
                        'reserva': reserva,
                    }

            except Reserva.DoesNotExist:
                resultado = {
                    'valido': False,
                    'mensaje': 'Código QR no encontrado.',
                }
    else:
        form = ValidacionQRForm()

    usuario = obtener_usuario(request)
    return render(request, 'reservas/validar_qr.html', {
        'form': form,
        'resultado': resultado,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 9. Admin: Gestión de canchas
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def admin_canchas_view(request):
    canchas = Cancha.objects.all()
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

    usuario = obtener_usuario(request)
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
    horarios = HorarioDisponible.objects.select_related('cancha').all()
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

    usuario = obtener_usuario(request)
    return render(request, 'reservas/admin_horarios.html', {
        'horarios': horarios,
        'form': form,
        'horario_editar': horario_editar,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 11. Reportes
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def reportes_view(request):
    total_reservas = Reserva.objects.count()
    reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
    reservas_canceladas = Reserva.objects.filter(estado='cancelada').count()
    reservas_no_asistidas = Reserva.objects.filter(estado='no_asistida').count()
    total_usuarios = Usuario.objects.count()
    total_canchas = Cancha.objects.count()

    historial_puntos = PuntosHistorial.objects.select_related(
        'usuario', 'reserva'
    ).order_by('-fecha')[:50]

    ultimas_reservas = Reserva.objects.select_related(
        'usuario', 'cancha'
    ).order_by('-fecha_creacion')[:20]

    usuario = obtener_usuario(request)
    return render(request, 'reservas/reportes.html', {
        'total_reservas': total_reservas,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_canceladas': reservas_canceladas,
        'reservas_no_asistidas': reservas_no_asistidas,
        'total_usuarios': total_usuarios,
        'total_canchas': total_canchas,
        'historial_puntos': historial_puntos,
        'ultimas_reservas': ultimas_reservas,
        'usuario': usuario,
    })
```

---

## Paso 3: Crear `reservas/urls.py`

Crea el archivo [reservas/urls.py](file:///c:/Users/DELL/Documents/proyecto%20final/reservas/urls.py):

```python
from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Canchas y disponibilidad
    path('canchas/', views.lista_canchas_view, name='lista_canchas'),
    path('disponibilidad/', views.disponibilidad_view, name='disponibilidad'),

    # Reservas
    path('reservar/', views.crear_reserva_view, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('cancelar-reserva/<int:reserva_id>/',
         views.cancelar_reserva_view, name='cancelar_reserva'),

    # Recepcionista
    path('validar-qr/', views.validar_qr_view, name='validar_qr'),

    # Administración
    path('admin-canchas/', views.admin_canchas_view, name='admin_canchas'),
    path('admin-horarios/', views.admin_horarios_view, name='admin_horarios'),
    path('reportes/', views.reportes_view, name='reportes'),
]
```

---

## Paso 4: Actualizar `polideportivo/urls.py`

Modifica [polideportivo/urls.py](file:///c:/Users/DELL/Documents/proyecto%20final/polideportivo/urls.py) para incluir las URLs de reservas:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservas.urls')),
]
```

---

## Paso 5: Crear la carpeta de templates

Crea la siguiente estructura de carpetas:

```
reservas/
└── templates/
    └── reservas/
```

En Windows, puedes ejecutar:

```bash
mkdir reservas\templates\reservas
```

---

## Paso 6: Crear `base.html`

Crea el archivo `reservas/templates/reservas/base.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titulo %}Polideportivo{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
        }

        /* ─── Navegación ─── */
        .navbar {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-brand {
            font-size: 1.4rem;
            font-weight: 700;
            color: #7c4dff;
            text-decoration: none;
        }

        .navbar-links { display: flex; gap: 1rem; align-items: center; }

        .navbar-links a {
            color: #b0b0b0;
            text-decoration: none;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            transition: all 0.3s;
            font-size: 0.9rem;
        }

        .navbar-links a:hover {
            color: #fff;
            background: rgba(124,77,255,0.2);
        }

        .navbar-links a.active {
            color: #7c4dff;
            background: rgba(124,77,255,0.15);
        }

        .navbar-user {
            color: #aaa;
            font-size: 0.85rem;
        }

        /* ─── Contenido ─── */
        .container {
            max-width: 1100px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }

        .page-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: #fff;
        }

        /* ─── Cards ─── */
        .card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(8px);
        }

        .card h3 {
            color: #b388ff;
            margin-bottom: 0.8rem;
        }

        /* ─── Formularios ─── */
        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.3rem;
            color: #ccc;
            font-size: 0.9rem;
        }

        .form-control {
            width: 100%;
            padding: 0.6rem 0.8rem;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 8px;
            color: #fff;
            font-size: 0.95rem;
            transition: border 0.3s;
        }

        .form-control:focus {
            outline: none;
            border-color: #7c4dff;
            box-shadow: 0 0 0 3px rgba(124,77,255,0.2);
        }

        select.form-control { cursor: pointer; }
        select.form-control option { background: #24243e; color: #fff; }

        .form-check-input { width: 18px; height: 18px; cursor: pointer; }

        /* ─── Botones ─── */
        .btn {
            display: inline-block;
            padding: 0.55rem 1.2rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-primary {
            background: linear-gradient(135deg, #7c4dff, #536dfe);
            color: #fff;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(124,77,255,0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ff5252, #ff1744);
            color: #fff;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,23,68,0.4);
        }

        .btn-success {
            background: linear-gradient(135deg, #69f0ae, #00e676);
            color: #1a1a2e;
        }

        .btn-outline {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.2);
            color: #ccc;
        }

        .btn-outline:hover {
            background: rgba(255,255,255,0.08);
            color: #fff;
        }

        /* ─── Tablas ─── */
        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 0.7rem 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        th {
            color: #b388ff;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }

        tr:hover { background: rgba(255,255,255,0.04); }

        /* ─── Alertas / Mensajes ─── */
        .alert {
            padding: 0.8rem 1.2rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }

        .alert-success {
            background: rgba(105,240,174,0.15);
            border: 1px solid rgba(105,240,174,0.3);
            color: #69f0ae;
        }

        .alert-error {
            background: rgba(255,82,82,0.15);
            border: 1px solid rgba(255,82,82,0.3);
            color: #ff5252;
        }

        .alert-warning {
            background: rgba(255,234,0,0.1);
            border: 1px solid rgba(255,234,0,0.3);
            color: #ffea00;
        }

        .alert-info {
            background: rgba(64,196,255,0.1);
            border: 1px solid rgba(64,196,255,0.3);
            color: #40c4ff;
        }

        /* ─── Badges ─── */
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-confirmada { background: rgba(105,240,174,0.2); color: #69f0ae; }
        .badge-cancelada { background: rgba(255,82,82,0.2); color: #ff5252; }
        .badge-no_asistida { background: rgba(255,234,0,0.2); color: #ffea00; }
        .badge-disponible { background: rgba(105,240,174,0.2); color: #69f0ae; }
        .badge-mantenimiento { background: rgba(255,234,0,0.2); color: #ffea00; }
        .badge-fuera_servicio { background: rgba(255,82,82,0.2); color: #ff5252; }

        /* ─── Stats ─── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
        }

        .stat-card .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #7c4dff;
        }

        .stat-card .stat-label {
            color: #aaa;
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }

        /* ─── Filtros ─── */
        .filters {
            display: flex;
            gap: 1rem;
            align-items: end;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }

        .filters .form-group { margin-bottom: 0; min-width: 180px; }

        /* ─── Grid de canchas ─── */
        .canchas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.2rem;
        }

        /* ─── QR resultado ─── */
        .qr-resultado {
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-top: 1rem;
        }

        .qr-valido {
            background: rgba(105,240,174,0.1);
            border: 2px solid rgba(105,240,174,0.3);
        }

        .qr-invalido {
            background: rgba(255,82,82,0.1);
            border: 2px solid rgba(255,82,82,0.3);
        }

        /* ─── Login box ─── */
        .auth-container {
            max-width: 420px;
            margin: 5rem auto;
        }

        .auth-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 2.5rem;
            backdrop-filter: blur(12px);
        }

        .auth-card h2 {
            text-align: center;
            color: #fff;
            margin-bottom: 1.5rem;
            font-size: 1.6rem;
        }

        .auth-footer {
            text-align: center;
            margin-top: 1.2rem;
            color: #888;
            font-size: 0.9rem;
        }

        .auth-footer a { color: #7c4dff; text-decoration: none; }
        .auth-footer a:hover { text-decoration: underline; }

        /* ─── Responsive ─── */
        @media (max-width: 768px) {
            .navbar { flex-direction: column; gap: 0.5rem; }
            .filters { flex-direction: column; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    {% if usuario %}
    <nav class="navbar">
        <a href="{% url 'lista_canchas' %}" class="navbar-brand">🏟️ Polideportivo</a>
        <div class="navbar-links">
            <a href="{% url 'lista_canchas' %}">Canchas</a>
            <a href="{% url 'disponibilidad' %}">Disponibilidad</a>
            <a href="{% url 'crear_reserva' %}">Reservar</a>
            <a href="{% url 'mis_reservas' %}">Mis Reservas</a>

            {% if usuario.rol == 'recepcionista' or usuario.rol == 'administrador' %}
                <a href="{% url 'validar_qr' %}">Validar QR</a>
            {% endif %}

            {% if usuario.rol == 'administrador' %}
                <a href="{% url 'admin_canchas' %}">Admin Canchas</a>
                <a href="{% url 'admin_horarios' %}">Admin Horarios</a>
                <a href="{% url 'reportes' %}">Reportes</a>
            {% endif %}

            <span class="navbar-user">{{ usuario.nombre }} ({{ usuario.rol }})</span>
            <a href="{% url 'logout' %}">Salir</a>
        </div>
    </nav>
    {% endif %}

    <div class="container">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}

        {% block contenido %}{% endblock %}
    </div>
</body>
</html>
```

---

## Paso 7: Crear `login.html`

Archivo: `reservas/templates/reservas/login.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Iniciar Sesión - Polideportivo{% endblock %}

{% block contenido %}
<div class="auth-container">
    <div class="auth-card">
        <h2>🏟️ Polideportivo</h2>

        {% if form.errors %}
            <div class="alert alert-error">
                {% for error in form.non_field_errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label>Correo electrónico</label>
                {{ form.correo }}
            </div>
            <div class="form-group">
                <label>Contraseña</label>
                {{ form.password }}
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%; margin-top:0.5rem;">
                Iniciar Sesión
            </button>
        </form>

        <div class="auth-footer">
            ¿No tienes cuenta? <a href="{% url 'registro' %}">Regístrate aquí</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Paso 8: Crear `registro.html`

Archivo: `reservas/templates/reservas/registro.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Registro - Polideportivo{% endblock %}

{% block contenido %}
<div class="auth-container">
    <div class="auth-card">
        <h2>Crear Cuenta</h2>

        {% if form.errors %}
            <div class="alert alert-error">
                {% for field, errors in form.errors.items %}
                    {% for error in errors %}
                        <div>{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            {% for field in form.visible_fields %}
                <div class="form-group">
                    <label>{{ field.label }}</label>
                    {{ field }}
                </div>
            {% endfor %}
            <button type="submit" class="btn btn-primary" style="width:100%; margin-top:0.5rem;">
                Registrarse
            </button>
        </form>

        <div class="auth-footer">
            ¿Ya tienes cuenta? <a href="{% url 'login' %}">Inicia sesión</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Paso 9: Crear `lista_canchas.html`

Archivo: `reservas/templates/reservas/lista_canchas.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Canchas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Canchas Disponibles</h1>

<form method="get" class="filters">
    <div class="form-group">
        <label>Deporte</label>
        <select name="tipo" class="form-control">
            <option value="">Todos</option>
            {% for value, label in tipos %}
                <option value="{{ value }}" {% if filtro_tipo == value %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="form-group">
        <label>Estado</label>
        <select name="estado" class="form-control">
            <option value="">Todos</option>
            {% for value, label in estados %}
                <option value="{{ value }}" {% if filtro_estado == value %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
        </select>
    </div>
    <button type="submit" class="btn btn-outline">Filtrar</button>
</form>

<div class="canchas-grid">
    {% for cancha in canchas %}
    <div class="card">
        <h3>{{ cancha.nombre }}</h3>
        <p>🏅 {{ cancha.get_tipo_deporte_display }}</p>
        <p>📍 {{ cancha.ubicacion }}</p>
        <p><span class="badge badge-{{ cancha.estado }}">{{ cancha.get_estado_display }}</span></p>
        {% if cancha.descripcion %}
            <p style="color:#999; font-size:0.85rem; margin-top:0.5rem;">{{ cancha.descripcion }}</p>
        {% endif %}
        {% if cancha.estado == 'disponible' %}
            <a href="{% url 'disponibilidad' %}?cancha={{ cancha.id }}" class="btn btn-primary" style="margin-top:0.8rem;">
                Ver Disponibilidad
            </a>
        {% endif %}
    </div>
    {% empty %}
    <p style="color:#888;">No se encontraron canchas.</p>
    {% endfor %}
</div>
{% endblock %}
```

---

## Paso 10: Crear `disponibilidad.html`

Archivo: `reservas/templates/reservas/disponibilidad.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Disponibilidad - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Consultar Disponibilidad</h1>

<div class="card">
    <form method="get" class="filters">
        <div class="form-group">
            <label>Cancha</label>
            <select name="cancha" class="form-control">
                <option value="">Seleccionar...</option>
                {% for c in canchas %}
                    <option value="{{ c.id }}" {% if cancha_sel and cancha_sel.id == c.id %}selected{% endif %}>
                        {{ c.nombre }} ({{ c.get_tipo_deporte_display }})
                    </option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label>Fecha</label>
            <input type="date" name="fecha" class="form-control" value="{{ fecha }}">
        </div>
        <button type="submit" class="btn btn-primary">Buscar</button>
    </form>
</div>

{% if cancha_sel and horarios %}
<div class="card">
    <h3>Horarios de {{ cancha_sel.nombre }} — {{ fecha }}</h3>
    <table>
        <thead>
            <tr>
                <th>Hora Inicio</th>
                <th>Hora Fin</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for h in horarios %}
            <tr>
                <td>{{ h.hora_inicio }}</td>
                <td>{{ h.hora_fin }}</td>
                <td>
                    {% if h.hora_inicio|stringformat:"s" in reservas_existentes_str %}
                        <span class="badge badge-cancelada">Ocupado</span>
                    {% else %}
                        <span class="badge badge-confirmada">Libre</span>
                    {% endif %}
                </td>
                <td>
                    <a href="{% url 'crear_reserva' %}?cancha={{ cancha_sel.id }}&fecha={{ fecha }}&hora_inicio={{ h.hora_inicio|time:'H:i' }}&hora_fin={{ h.hora_fin|time:'H:i' }}"
                       class="btn btn-primary">
                        Reservar
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% elif cancha_sel %}
<div class="card">
    <p style="color:#888;">No hay horarios disponibles para esta cancha en la fecha seleccionada.</p>
</div>
{% endif %}
{% endblock %}
```

---

## Paso 11: Crear `crear_reserva.html`

Archivo: `reservas/templates/reservas/crear_reserva.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Crear Reserva - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Nueva Reserva</h1>

<div class="card" style="max-width: 600px;">
    {% if form.errors %}
        <div class="alert alert-error">
            {% for error in form.non_field_errors %}
                <div>{{ error }}</div>
            {% endfor %}
        </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <div class="form-group">
            <label>Cancha</label>
            {{ form.cancha }}
        </div>
        <div class="form-group">
            <label>Fecha</label>
            {{ form.fecha }}
        </div>
        <div class="form-group">
            <label>Hora Inicio</label>
            {{ form.hora_inicio }}
        </div>
        <div class="form-group">
            <label>Hora Fin</label>
            {{ form.hora_fin }}
        </div>
        <div class="form-group">
            <label>Observación</label>
            {{ form.observacion }}
        </div>
        <button type="submit" class="btn btn-primary">Confirmar Reserva</button>
        <a href="{% url 'disponibilidad' %}" class="btn btn-outline">Cancelar</a>
    </form>
</div>
{% endblock %}
```

---

## Paso 12: Crear `mis_reservas.html`

Archivo: `reservas/templates/reservas/mis_reservas.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Mis Reservas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Mis Reservas</h1>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Cancha</th>
                <th>Fecha</th>
                <th>Horario</th>
                <th>Estado</th>
                <th>QR</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for r in reservas %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.cancha.nombre }}</td>
                <td>{{ r.fecha }}</td>
                <td>{{ r.hora_inicio }} - {{ r.hora_fin }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
                <td style="font-size:0.75rem; color:#7c4dff;">{{ r.codigo_qr|truncatechars:12 }}</td>
                <td>
                    {% if r.estado == 'confirmada' %}
                        <a href="{% url 'cancelar_reserva' r.id %}"
                           class="btn btn-danger"
                           onclick="return confirm('¿Cancelar esta reserva?');">
                            Cancelar
                        </a>
                    {% else %}
                        —
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" style="color:#888; text-align:center;">No tienes reservas.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

## Paso 13: Crear `validar_qr.html`

Archivo: `reservas/templates/reservas/validar_qr.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Validar QR - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Validar Código QR</h1>

<div class="card" style="max-width: 500px;">
    <form method="post">
        {% csrf_token %}
        <div class="form-group">
            <label>Código QR</label>
            {{ form.codigo_qr }}
        </div>
        <button type="submit" class="btn btn-primary">Verificar</button>
    </form>
</div>

{% if resultado %}
<div class="qr-resultado {% if resultado.valido %}qr-valido{% else %}qr-invalido{% endif %}">
    <h3 style="margin-bottom:0.5rem;">
        {% if resultado.valido %}✅{% else %}❌{% endif %}
        {{ resultado.mensaje }}
    </h3>

    {% if resultado.reserva %}
    <table style="margin-top:1rem; text-align:left;">
        <tr><th>Usuario</th><td>{{ resultado.reserva.usuario.nombre }}</td></tr>
        <tr><th>Cancha</th><td>{{ resultado.reserva.cancha.nombre }}</td></tr>
        <tr><th>Fecha</th><td>{{ resultado.reserva.fecha }}</td></tr>
        <tr><th>Horario</th><td>{{ resultado.reserva.hora_inicio }} - {{ resultado.reserva.hora_fin }}</td></tr>
    </table>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

---

## Paso 14: Crear `admin_canchas.html`

Archivo: `reservas/templates/reservas/admin_canchas.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Gestión de Canchas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Gestión de Canchas</h1>

<div class="card">
    <h3>{% if cancha_editar %}Editar Cancha{% else %}Nueva Cancha{% endif %}</h3>

    <form method="post">
        {% csrf_token %}
        {% if cancha_editar %}
            <input type="hidden" name="cancha_id" value="{{ cancha_editar.id }}">
        {% endif %}

        {% for field in form.visible_fields %}
            <div class="form-group">
                <label>{{ field.label }}</label>
                {{ field }}
            </div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">Guardar</button>
        {% if cancha_editar %}
            <a href="{% url 'admin_canchas' %}" class="btn btn-outline">Cancelar Edición</a>
        {% endif %}
    </form>
</div>

<div class="card">
    <h3>Canchas Registradas</h3>
    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Deporte</th>
                <th>Ubicación</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for c in canchas %}
            <tr>
                <td>{{ c.nombre }}</td>
                <td>{{ c.get_tipo_deporte_display }}</td>
                <td>{{ c.ubicacion }}</td>
                <td><span class="badge badge-{{ c.estado }}">{{ c.get_estado_display }}</span></td>
                <td>
                    <a href="?editar={{ c.id }}" class="btn btn-outline">Editar</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

## Paso 15: Crear `admin_horarios.html`

Archivo: `reservas/templates/reservas/admin_horarios.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Gestión de Horarios - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Gestión de Horarios</h1>

<div class="card">
    <h3>{% if horario_editar %}Editar Horario{% else %}Nuevo Horario{% endif %}</h3>

    <form method="post">
        {% csrf_token %}
        {% if horario_editar %}
            <input type="hidden" name="horario_id" value="{{ horario_editar.id }}">
        {% endif %}

        {% for field in form.visible_fields %}
            <div class="form-group">
                <label>{{ field.label }}</label>
                {{ field }}
            </div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">Guardar</button>
        {% if horario_editar %}
            <a href="{% url 'admin_horarios' %}" class="btn btn-outline">Cancelar</a>
        {% endif %}
    </form>
</div>

<div class="card">
    <h3>Horarios Registrados</h3>
    <table>
        <thead>
            <tr>
                <th>Cancha</th>
                <th>Día</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Activo</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for h in horarios %}
            <tr>
                <td>{{ h.cancha.nombre }}</td>
                <td>{{ h.get_dia_semana_display }}</td>
                <td>{{ h.hora_inicio }}</td>
                <td>{{ h.hora_fin }}</td>
                <td>{% if h.activo %}✅{% else %}❌{% endif %}</td>
                <td>
                    <a href="?editar={{ h.id }}" class="btn btn-outline">Editar</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

## Paso 16: Crear `reportes.html`

Archivo: `reservas/templates/reservas/reportes.html`

```html
{% extends 'reservas/base.html' %}

{% block titulo %}Reportes - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Reportes y Estadísticas</h1>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">{{ total_reservas }}</div>
        <div class="stat-label">Total Reservas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_confirmadas }}</div>
        <div class="stat-label">Confirmadas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_canceladas }}</div>
        <div class="stat-label">Canceladas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_no_asistidas }}</div>
        <div class="stat-label">No Asistidas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_usuarios }}</div>
        <div class="stat-label">Usuarios</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_canchas }}</div>
        <div class="stat-label">Canchas</div>
    </div>
</div>

<div class="card">
    <h3>Últimas Reservas</h3>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Usuario</th>
                <th>Cancha</th>
                <th>Fecha</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            {% for r in ultimas_reservas %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.usuario.nombre }}</td>
                <td>{{ r.cancha.nombre }}</td>
                <td>{{ r.fecha }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>Historial de Puntos</h3>
    <table>
        <thead>
            <tr>
                <th>Usuario</th>
                <th>Puntos</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Descripción</th>
            </tr>
        </thead>
        <tbody>
            {% for p in historial_puntos %}
            <tr>
                <td>{{ p.usuario.nombre }}</td>
                <td>{{ p.puntos }}</td>
                <td>{{ p.get_tipo_movimiento_display }}</td>
                <td>{{ p.fecha|date:"d/m/Y H:i" }}</td>
                <td>{{ p.descripcion }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

## Paso 17: Configurar tags de mensajes

Abre [settings.py](file:///c:/Users/DELL/Documents/proyecto%20final/polideportivo/settings.py) y agrega al final del archivo:

```python
from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: 'info',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'error',
}
```

---

## Paso 18: Verificar

Una vez que hayas creado todos los archivos, ejecuta:

```bash
python manage.py check
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/` en tu navegador para ver la pantalla de login.

---

## Resumen de archivos a crear/modificar

| Acción | Archivo |
|---|---|
| **CREAR** | `reservas/forms.py` |
| **REEMPLAZAR** | `reservas/views.py` |
| **CREAR** | `reservas/urls.py` |
| **MODIFICAR** | `polideportivo/urls.py` |
| **CREAR** | `reservas/templates/reservas/base.html` |
| **CREAR** | `reservas/templates/reservas/login.html` |
| **CREAR** | `reservas/templates/reservas/registro.html` |
| **CREAR** | `reservas/templates/reservas/lista_canchas.html` |
| **CREAR** | `reservas/templates/reservas/disponibilidad.html` |
| **CREAR** | `reservas/templates/reservas/crear_reserva.html` |
| **CREAR** | `reservas/templates/reservas/mis_reservas.html` |
| **CREAR** | `reservas/templates/reservas/validar_qr.html` |
| **CREAR** | `reservas/templates/reservas/admin_canchas.html` |
| **CREAR** | `reservas/templates/reservas/admin_horarios.html` |
| **CREAR** | `reservas/templates/reservas/reportes.html` |
| **MODIFICAR** | `polideportivo/settings.py` (MESSAGE_TAGS) |

---

## Flujo de prueba

1. Ve a `http://127.0.0.1:8000/registro/` → crea un usuario
2. Ve a `http://127.0.0.1:8000/` → inicia sesión
3. Ve a **Canchas** → mira el listado
4. Ve a **Disponibilidad** → busca horarios
5. Ve a **Reservar** → crea una reserva
6. Ve a **Mis Reservas** → ve tu reserva con el QR
7. Para admin: crea un usuario con rol `administrador` desde el admin de Django (`/admin/`)
