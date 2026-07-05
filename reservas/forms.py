from datetime import date, datetime

from django import forms
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from .models import Usuario, Cancha, HorarioDisponible, Reserva, ConfiguracionPuntos, ProductoBar


def _normalizar_invitados(valor):
    return Reserva.parsear_lista_invitados(valor)


def _extraer_invitados_desde_campos(data):
    invitados = []

    def ordenar_item(item):
        key = item[0]
        try:
            return int(key.split('_')[1])
        except (IndexError, ValueError):
            return 0

    for _, valor in sorted(data.items(), key=ordenar_item):
        nombre = ' '.join(str(valor).strip().split())
        if nombre:
            invitados.append(nombre)
    return invitados


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
        fields = [
            'nombre',
            'tipo_deporte',
            'tipo_personalizado',
            'ubicacion',
            'capacidad_jugadores_min',
            'capacidad_jugadores_max',
            'estado',
            'descripcion',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_deporte': forms.Select(attrs={'class': 'form-control'}),
            'tipo_personalizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Piscina, gimnasio, pista de trote',
            }),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad_jugadores_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Minimo',
            }),
            'capacidad_jugadores_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Maximo',
            }),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_personalizado'].label = 'Especifica el espacio'
        self.fields['tipo_personalizado'].required = False
        self.fields['capacidad_jugadores_min'].label = 'Jugadores minimos'
        self.fields['capacidad_jugadores_max'].label = 'Jugadores maximos'

    def clean(self):
        cleaned_data = super().clean()
        tipo_deporte = cleaned_data.get('tipo_deporte')
        tipo_personalizado = (cleaned_data.get('tipo_personalizado') or '').strip()
        capacidad_min = cleaned_data.get('capacidad_jugadores_min')
        capacidad_max = cleaned_data.get('capacidad_jugadores_max')

        if tipo_deporte == Cancha.TipoDeporte.OTRO:
            if not tipo_personalizado:
                self.add_error('tipo_personalizado', 'Escribe el nombre del espacio personalizado.')
        else:
            cleaned_data['tipo_personalizado'] = ''

        if capacidad_min is None:
            self.add_error('capacidad_jugadores_min', 'Ingresa el minimo de jugadores.')
        if capacidad_max is None:
            self.add_error('capacidad_jugadores_max', 'Ingresa el maximo de jugadores.')
        if capacidad_min is not None and capacidad_max is not None and capacidad_max < capacidad_min:
            self.add_error('capacidad_jugadores_max', 'El maximo no puede ser menor que el minimo.')

        return cleaned_data


class _HorarioRecepcionHelper:
    @staticmethod
    def parse_fecha(raw_value):
        if not raw_value:
            return None
        if hasattr(raw_value, 'isoformat'):
            return raw_value
        try:
            return date.fromisoformat(str(raw_value))
        except ValueError:
            return None

    @staticmethod
    def slot_value(hora_inicio, hora_fin):
        return f"{hora_inicio.strftime('%H:%M')}|{hora_fin.strftime('%H:%M')}"

    @staticmethod
    def slot_label(hora_inicio, hora_fin):
        return f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"


def obtener_opciones_horario_recepcion(cancha_id, fecha_obj):
    if not cancha_id or not fecha_obj:
        return []

    try:
        cancha_id = int(cancha_id)
    except (TypeError, ValueError):
        return []

    horarios = HorarioDisponible.objects.filter(
        cancha_id=cancha_id,
        dia_semana=fecha_obj.isoweekday(),
        activo=True,
    ).order_by('hora_inicio')

    reservas_ocupadas = set(
        Reserva.objects.filter(
            cancha_id=cancha_id,
            fecha=fecha_obj,
            estado__in=['confirmada', 'asistida'],
        ).values_list('hora_inicio', 'hora_fin')
    )

    hoy = timezone.localdate()
    hora_actual = timezone.localtime(timezone.now()).time()
    opciones = []

    for horario in horarios:
        franja = (horario.hora_inicio, horario.hora_fin)
        if franja in reservas_ocupadas:
            continue
        if fecha_obj < hoy:
            continue
        if fecha_obj == hoy and horario.hora_inicio < hora_actual:
            continue

        opciones.append((
            _HorarioRecepcionHelper.slot_value(horario.hora_inicio, horario.hora_fin),
            _HorarioRecepcionHelper.slot_label(horario.hora_inicio, horario.hora_fin),
        ))

    return opciones


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
    cantidad_invitados = forms.IntegerField(
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': '0',
        }),
        label='Cu?ntos acompa?antes van'
    )
    lista_invitados = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        label='Lista de Invitados (Acompañantes)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cantidad_actual = None

        cantidad_raw = self.data.get('cantidad_invitados') if hasattr(self, 'data') else None
        if cantidad_raw not in (None, ''):
            try:
                cantidad_actual = max(int(cantidad_raw), 0)
            except (TypeError, ValueError):
                cantidad_actual = 0

        if cantidad_actual is None:
            lista_base = self.initial.get('lista_invitados', '')
            cantidad_actual = len(_normalizar_invitados(lista_base))

        self.fields['cantidad_invitados'].initial = cantidad_actual

    def _resolver_invitados(self, cleaned_data):
        invitados = _extraer_invitados_desde_campos({
            key: value
            for key, value in self.data.items()
            if key.startswith('invitado_')
        })
        if invitados:
            return invitados
        return _normalizar_invitados(cleaned_data.get('lista_invitados', ''))

    def clean(self):
        cleaned_data = super().clean()
        cancha = cleaned_data.get('cancha')
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        horario_disponible = cleaned_data.get('horario_disponible')
        cantidad_invitados = cleaned_data.get('cantidad_invitados')
        cantidad_raw = self.data.get('cantidad_invitados') if hasattr(self, 'data') else None

        if horario_disponible and (not hora_inicio or not hora_fin):
            try:
                hora_inicio_str, hora_fin_str = horario_disponible.split('|', 1)
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
                cleaned_data['hora_inicio'] = hora_inicio
                cleaned_data['hora_fin'] = hora_fin
            except ValueError:
                if 'horario_disponible' in self.fields:
                    self.add_error('horario_disponible', 'Selecciona un horario valido.')
                return cleaned_data

        if cancha and fecha and not (hora_inicio and hora_fin):
            if 'horario_disponible' in self.fields:
                self.add_error('horario_disponible', 'Selecciona un horario disponible.')
            return cleaned_data

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise forms.ValidationError(
                'La hora de fin debe ser mayor que la de inicio.'
            )

        if cancha and fecha and hora_inicio and hora_fin:
            now_time = timezone.localtime(timezone.now()).time()
            today_date = timezone.localtime(timezone.now()).date()

            if fecha < today_date:
                raise forms.ValidationError('No puedes hacer reservas en fechas pasadas.')

            if fecha == today_date and hora_inicio < now_time:
                raise forms.ValidationError('No puedes hacer reservas en horarios que ya pasaron.')

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

        invitados = self._resolver_invitados(cleaned_data)
        if cantidad_raw in (None, ''):
            cantidad_invitados = len(invitados)

        cantidad_invitados = cantidad_invitados or 0

        if cantidad_invitados == 0 and invitados:
            self.add_error(
                'cantidad_invitados',
                'Si escribes acompa?antes, indica cu?ntos van.'
            )
        elif cantidad_invitados > 0 and not invitados:
            self.add_error(
                'lista_invitados',
                'Escribe el nombre de cada acompa?ante.'
            )
        elif cantidad_invitados != len(invitados):
            self.add_error(
                'lista_invitados',
                f'Debes registrar {cantidad_invitados} acompa?ante(s) y ahora hay {len(invitados)}.'
            )

        cleaned_data['cantidad_invitados'] = cantidad_invitados
        cleaned_data['lista_invitados'] = '\n'.join(invitados)

        return cleaned_data


class ReservaRecepcionForm(ReservaForm):
    """Formulario para que el recepcionista cree una reserva para otro usuario."""
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(estado='activo').order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Cliente / Usuario'
    )
    horario_disponible = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Horario disponible'
    )
    hora_inicio = forms.TimeField(required=False, widget=forms.HiddenInput())
    hora_fin = forms.TimeField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].empty_label = 'Selecciona un cliente'
        self.fields['cancha'].queryset = Cancha.objects.filter(estado='disponible').order_by('nombre')
        self.fields['cancha'].widget.attrs['class'] = 'form-select'
        self.fields['cancha'].widget.attrs.pop('readonly', None)
        self.fields['cancha'].widget.attrs.pop('style', None)
        self.fields['fecha'].widget.attrs.pop('readonly', None)
        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['min'] = timezone.localdate().isoformat()

        self.fields['cantidad_invitados'].widget.attrs['placeholder'] = 'Ej. 2'
        self.fields['observacion'].widget.attrs['placeholder'] = 'Opcional: notas para la reserva o para el recepcionista'

        cancha_valor = self.data.get('cancha') or self.initial.get('cancha')
        fecha_valor = self.data.get('fecha') or self.initial.get('fecha')
        fecha_obj = _HorarioRecepcionHelper.parse_fecha(fecha_valor)
        opciones = obtener_opciones_horario_recepcion(cancha_valor, fecha_obj)

        if cancha_valor and fecha_obj:
            placeholder = 'Selecciona un horario disponible' if opciones else 'No hay horarios libres para esa fecha'
        else:
            placeholder = 'Selecciona cancha y fecha primero'

        self.fields['horario_disponible'].choices = [('', placeholder)] + list(opciones)

        horario_actual = self.data.get('horario_disponible')
        if not horario_actual:
            hora_inicio_valor = self.data.get('hora_inicio') or self.initial.get('hora_inicio')
            hora_fin_valor = self.data.get('hora_fin') or self.initial.get('hora_fin')
            if hora_inicio_valor and hora_fin_valor:
                try:
                    if hasattr(hora_inicio_valor, 'strftime'):
                        horario_actual = _HorarioRecepcionHelper.slot_value(hora_inicio_valor, hora_fin_valor)
                    else:
                        horario_actual = f"{str(hora_inicio_valor)[:5]}|{str(hora_fin_valor)[:5]}"
                except Exception:
                    horario_actual = ''

        self.fields['horario_disponible'].initial = horario_actual or ''

    def clean(self):
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


class ProductoBarForm(forms.ModelForm):
    """Formulario para crear/editar productos del bar."""

    class Meta:
        model = ProductoBar
        fields = ['nombre', 'categoria', 'puntos_requeridos', 'descripcion', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Coca-Cola, Agua, Papas',
            }),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'puntos_requeridos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Ej. 10',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripcion breve (opcional)',
            }),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
        fields = ['puntos_por_asistencia']
        widgets = {
            'puntos_por_asistencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
        }




