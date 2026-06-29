from django import forms
from django.contrib.auth.hashers import check_password
from .models import Usuario, Cancha, HorarioDisponible, Reserva, ConfiguracionPuntos


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
                raise forms.ValidationError(
                    'Este correo no está registrado. ¿Deseas crear una cuenta?'
                )

            if not check_password(password, usuario.password):
                raise forms.ValidationError('Contraseña incorrecta. Inténtalo de nuevo.')

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
        widget=forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly', 'style': 'pointer-events: none;'}),
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'readonly': 'readonly',
        })
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'readonly': 'readonly',
        })
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'readonly': 'readonly',
        })
    )
    observacion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': '¿Algún requerimiento especial? (Opcional)'
        }),
        required=False,
    )
    lista_invitados = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Escribe los nombres de las personas que te acompañarán (Obligatorio)'
        }),
        required=True,
        label='Lista de Invitados (Acompañantes)'
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

        if cancha and fecha and hora_inicio and hora_fin:
            from django.utils import timezone
            now_time = timezone.localtime(timezone.now()).time()
            today_date = timezone.localtime(timezone.now()).date()
            
            # 1. Validar fechas pasadas
            if fecha < today_date:
                raise forms.ValidationError('No puedes hacer reservas en fechas pasadas.')
            
            # 2. Validar horarios pasados hoy
            if fecha == today_date and hora_inicio < now_time:
                raise forms.ValidationError('No puedes hacer reservas en horarios que ya pasaron.')

            # 3. Validar que la franja horaria existe para esa cancha y está activa
            dia_semana = fecha.isoweekday()
            horario_valido = HorarioDisponible.objects.filter(
                cancha=cancha,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                activo=True
            ).exists()
            if not horario_valido:
                raise forms.ValidationError('El horario seleccionado no es válido o no está configurado para esta cancha.')

            # 4. Verificar que no exista reserva duplicada (confirmada o asistida)
            existe = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado__in=['confirmada', 'asistida'],
            ).exists()
            if existe:
                raise forms.ValidationError(
                    'Ya existe una reserva confirmada para esa cancha en ese horario.'
                )

        return cleaned_data


class ReservaRecepcionForm(ReservaForm):
    """Formulario para que el recepcionista cree una reserva para otro usuario."""
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(estado='activo'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Cliente / Usuario'
    )

    def clean(self):
        # Primero ejecuta las validaciones de ReservaForm
        cleaned_data = super().clean()
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

class EditarRolForm(forms.ModelForm):
    """Formulario para que el administrador cambie el rol de un usuario."""

    class Meta:
        model = Usuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }


class EditarPerfilForm(forms.ModelForm):
    """Formulario para que el usuario edite sus datos personales."""

    class Meta:
        model = Usuario
        fields = ['nombre', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)',
            }),
        }


class ConfiguracionPuntosForm(forms.ModelForm):
    """Formulario para configurar las reglas del programa de puntos."""

    class Meta:
        model = ConfiguracionPuntos
        fields = ['puntos_por_asistencia', 'minimo_canje', 'descripcion_beneficio']
        widgets = {
            'puntos_por_asistencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'minimo_canje': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'descripcion_beneficio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe los beneficios que los usuarios pueden obtener',
            }),
        }
