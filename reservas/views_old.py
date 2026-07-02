import uuid
from datetime import date, timedelta
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.db import transaction, IntegrityError
import qrcode
import io

from .models import (
    Usuario, Cancha, HorarioDisponible,
    Reserva, PuntosHistorial, LogErrores,
    ConfiguracionPuntos,
)
from .forms import (
    LoginForm, RegistroForm, CanchaForm,
    HorarioDisponibleForm, ReservaForm,
    ValidacionQRForm, CanjePuntosForm,
    EditarPerfilForm, EditarRolForm,
    ReservaRecepcionForm, ConfiguracionPuntosForm,
)


# ──────────────────────────────────────────────
# Función auxiliar para registrar errores (P3)
# ──────────────────────────────────────────────

def registrar_error(modulo, descripcion, nivel='error'):
    """Registra un error en la tabla LogErrores para auditoría."""
    try:
        LogErrores.objects.create(
            modulo_origen=modulo,
            descripcion_error=descripcion,
            nivel_severidad=nivel,
        )
    except Exception:
        pass  # Evitar errores recursivos al intentar loggear


# ──────────────────────────────────────────────
# Decoradores de control de acceso
# ──────────────────────────────────────────────

def login_requerido(view_func):
    """Verifica que haya un usuario en sesión activa."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.warning(request, 'Debes iniciar sesión.')
            return redirect('login')
        # Verificar que el usuario sigue activo en BD
        try:
            usuario = Usuario.objects.get(
                id=request.session['usuario_id'], estado='activo'
            )
        except Usuario.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Tu cuenta ha sido desactivada.')
            return redirect('login')
        request.usuario = usuario
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_requerido(*roles):
    """Verifica que el usuario tenga uno de los roles indicados."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'usuario_id' not in request.session:
                messages.warning(request, 'Debes iniciar sesión.')
                return redirect('login')
            try:
                usuario = Usuario.objects.get(
                    id=request.session['usuario_id'], estado='activo'
                )
            except Usuario.DoesNotExist:
                request.session.flush()
                messages.error(request, 'Tu cuenta ha sido desactivada.')
                return redirect('login')
            if usuario.rol not in roles:
                return HttpResponseForbidden(
                    '<h2 style="font-family:sans-serif;padding:2rem;color:#b91c1c">'
                    '⛔ No tienes permiso para acceder a esta página.</h2>'
                )
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

    usuario = request.usuario
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
    reservas_existentes_str = []

    canchas_disponibles = Cancha.objects.filter(estado='disponible')

    if cancha_id:
        try:
            cancha = Cancha.objects.get(id=cancha_id)
        except Cancha.DoesNotExist:
            messages.error(request, 'Cancha inválida.')

    if cancha and fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
            dia_semana = fecha_obj.isoweekday()  # 1=Lunes, 7=Domingo

            horarios = list(HorarioDisponible.objects.filter(
                cancha=cancha,
                dia_semana=dia_semana,
                activo=True,
            ))

            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha_obj,
                estado__in=['confirmada', 'asistida'],
            ).values_list('hora_inicio', 'hora_fin')

            from django.utils import timezone
            now_time = timezone.localtime(timezone.now()).time()
            today_date = timezone.localtime(timezone.now()).date()

            for h in horarios:
                h.is_ocupado = False
                h_inicio_str = h.hora_inicio.strftime('%H:%M')
                h_fin_str = h.hora_fin.strftime('%H:%M')

                for r_inicio, r_fin in reservas_existentes:
                    r_inicio_str = r_inicio.strftime('%H:%M')
                    r_fin_str = r_fin.strftime('%H:%M')
                    if h_inicio_str == r_inicio_str and h_fin_str == r_fin_str:
                        h.is_ocupado = True
                        break

                if fecha_obj < today_date:
                    h.is_past = True
                elif fecha_obj == today_date and h.hora_inicio < now_time:
                    h.is_past = True
                else:
                    h.is_past = False

        except ValueError:
            messages.error(request, 'Fecha inválida.')

    usuario = request.usuario
    return render(request, 'reservas/disponibilidad.html', {
        'canchas': canchas_disponibles,
        'cancha_sel': cancha,
        'fecha': fecha_str or '',
        'horarios': horarios,
        'reservas_existentes': list(reservas_existentes),
        'reservas_existentes_str': reservas_existentes_str,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 6. Crear reserva (P1: transaction.atomic, P5: sin puntos)
# ──────────────────────────────────────────────

@login_requerido
def crear_reserva_view(request):
    usuario = request.usuario

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
                # P1: Transacción atómica con bloqueo
                with transaction.atomic():
                    # Verificar duplicados dentro de la transacción con lock
                    existe = Reserva.objects.select_for_update().filter(
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        estado__in=['confirmada', 'asistida'],
                    ).exists()

                    if existe:
                        messages.error(
                            request,
                            'La cancha ya está reservada en ese horario. '
                            'Por favor seleccione otro horario disponible.'
                        )
                        return redirect('disponibilidad')

                    reserva = Reserva(
                        usuario=usuario,
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        observacion=form.cleaned_data.get('observacion', ''),
                        lista_invitados=form.cleaned_data.get('lista_invitados', ''),
                        codigo_qr=str(uuid.uuid4()),
                        estado='confirmada',
                    )
                    reserva.save()

                # P5: Ya NO se otorgan puntos aquí, se otorgan al validar QR (asistencia)

                messages.success(
                    request,
                    f'Reserva creada. Tu código QR es: {reserva.codigo_qr}'
                )
                return redirect('mis_reservas')

            except IntegrityError:
                # P2: La restricción UNIQUE atrapó un duplicado concurrente
                # P3: Registrar el error
                registrar_error(
                    'crear_reserva',
                    f'IntegrityError: duplicado concurrente para cancha={form.cleaned_data.get("cancha")}, '
                    f'fecha={form.cleaned_data.get("fecha")}',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya está reservada en ese horario. '
                    'Por favor seleccione otro horario disponible.'
                )
                return redirect('disponibilidad')

            except Exception as e:
                # P3: Registrar errores inesperados
                registrar_error(
                    'crear_reserva',
                    f'Error inesperado al crear reserva: {str(e)}',
                    nivel='error'
                )
                messages.error(
                    request,
                    'Ocurrió un problema al procesar su solicitud. Por favor, inténtelo más tarde.'
                )
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
    usuario = request.usuario
    reservas = Reserva.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'usuario': usuario,
    })


@login_requerido
def cancelar_reserva_view(request, reserva_id):
    usuario = request.usuario
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario)

    if reserva.estado != 'confirmada':
        messages.error(request, 'Solo puedes cancelar reservas confirmadas.')
    elif reserva.is_past:
        messages.error(request, 'No puedes cancelar una reserva que ya pasó.')
    else:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')

    return redirect('mis_reservas')


# ──────────────────────────────────────────────
# 8. Validar QR (P5: otorgar puntos, P8: verificar hora)
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
                    # P8: Verificar hora actual vs franja horaria
                    from django.utils import timezone
                    ahora = timezone.localtime(timezone.now()).time()
                    aviso_hora = ''

                    if reserva.fecha == date.today():
                        # Margen de 30 minutos antes y después
                        from datetime import datetime as dt
                        hora_inicio_dt = dt.combine(date.today(), reserva.hora_inicio)
                        hora_fin_dt = dt.combine(date.today(), reserva.hora_fin)
                        ahora_dt = dt.combine(date.today(), ahora)

                        margen = timedelta(minutes=30)
                        if ahora_dt < (hora_inicio_dt - margen):
                            aviso_hora = f' (Nota: La reserva es a las {reserva.hora_inicio.strftime("%H:%M")}, aún es temprano)'
                        elif ahora_dt > (hora_fin_dt + margen):
                            aviso_hora = f' (Nota: La franja horaria ya terminó a las {reserva.hora_fin.strftime("%H:%M")})'

                    # Marcar como asistida
                    reserva.estado = 'asistida'
                    reserva.save()

                    # P5: Otorgar puntos al ASISTIR (no al crear)
                    config = ConfiguracionPuntos.obtener()
                    puntos = config.puntos_por_asistencia

                    PuntosHistorial.objects.create(
                        usuario=reserva.usuario,
                        reserva=reserva,
                        puntos=puntos,
                        tipo_movimiento='otorgado',
                        descripcion=f'Puntos por asistencia confirmada (+{puntos}).',
                    )
                    reserva.usuario.puntos_acumulados += puntos
                    reserva.usuario.save()

                    resultado = {
                        'valido': True,
                        'mensaje': f'Acceso autorizado. Reserva marcada como Asistida. '
                                   f'+{puntos} puntos otorgados a {reserva.usuario.nombre}.{aviso_hora}',
                        'reserva': reserva,
                    }

            except Reserva.DoesNotExist:
                # P3: Registrar QR no encontrado
                registrar_error(
                    'validar_qr',
                    f'Código QR no encontrado: {codigo}',
                    nivel='warning'
                )
                resultado = {
                    'valido': False,
                    'mensaje': 'Código QR no encontrado.',
                }
    else:
        form = ValidacionQRForm()

    usuario = request.usuario
    return render(request, 'reservas/validar_qr.html', {
        'form': form,
        'resultado': resultado,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 8.1. Recepcionista: Crear Reserva para Usuario (P1: atomic)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def crear_reserva_recepcion_view(request):
    usuario_recepcion = request.usuario

    if request.method == 'POST':
        form = ReservaRecepcionForm(request.POST)
        if form.is_valid():
            try:
                # P1: Transacción atómica
                with transaction.atomic():
                    existe = Reserva.objects.select_for_update().filter(
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        estado__in=['confirmada', 'asistida'],
                    ).exists()

                    if existe:
                        messages.error(
                            request,
                            'La cancha ya está reservada en ese horario.'
                        )
                        return redirect('calendario_reservas')

                    usuario_cliente = form.cleaned_data['usuario']
                    reserva = Reserva(
                        usuario=usuario_cliente,
                        cancha=form.cleaned_data['cancha'],
                        fecha=form.cleaned_data['fecha'],
                        hora_inicio=form.cleaned_data['hora_inicio'],
                        hora_fin=form.cleaned_data['hora_fin'],
                        observacion=form.cleaned_data.get('observacion', ''),
                        lista_invitados=form.cleaned_data.get('lista_invitados', ''),
                        codigo_qr=str(uuid.uuid4()),
                        estado='confirmada',
                    )
                    reserva.save()

                # P5: Ya NO se otorgan puntos aquí, se otorgan al validar QR

                messages.success(
                    request,
                    f'Reserva creada para {usuario_cliente.nombre}. '
                    f'Código QR: {reserva.codigo_qr}'
                )
                return redirect('calendario_reservas')

            except IntegrityError:
                registrar_error(
                    'crear_reserva_recepcion',
                    f'IntegrityError: duplicado concurrente en reserva de recepción',
                    nivel='warning'
                )
                messages.error(
                    request,
                    'La cancha ya está reservada en ese horario.'
                )
                return redirect('calendario_reservas')

            except Exception as e:
                registrar_error(
                    'crear_reserva_recepcion',
                    f'Error inesperado: {str(e)}',
                    nivel='error'
                )
                messages.error(
                    request,
                    'Ocurrió un problema al procesar su solicitud. Por favor, inténtelo más tarde.'
                )
    else:
        initial = {}
        if request.GET.get('cancha'):
            initial['cancha'] = request.GET.get('cancha')
        if request.GET.get('fecha'):
            initial['fecha'] = request.GET.get('fecha')
        if request.GET.get('hora_inicio'):
            initial['hora_inicio'] = request.GET.get('hora_inicio')
        if request.GET.get('hora_fin'):
            initial['hora_fin'] = request.GET.get('hora_fin')
        form = ReservaRecepcionForm(initial=initial)

    return render(request, 'reservas/crear_reserva_recepcion.html', {
        'form': form,
        'usuario': usuario_recepcion,
    })


# ──────────────────────────────────────────────
# 8.2. Recepcionista: Calendario de Reservas (P7: semanal)
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def calendario_reservas_view(request):
    fecha_str = request.GET.get('fecha')
    vista = request.GET.get('vista', 'diaria')  # P7: diaria o semanal

    if fecha_str:
        try:
            fecha_obj = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_obj = date.today()
    else:
        fecha_obj = date.today()

    if vista == 'semanal':
        # P7: Calcular lunes-domingo de la semana
        lunes = fecha_obj - timedelta(days=fecha_obj.weekday())
        domingo = lunes + timedelta(days=6)
        reservas = Reserva.objects.select_related('cancha', 'usuario').filter(
            fecha__range=[lunes, domingo]
        ).order_by('fecha', 'hora_inicio')
        dias_semana = [lunes + timedelta(days=i) for i in range(7)]
    else:
        reservas = Reserva.objects.select_related('cancha', 'usuario').filter(
            fecha=fecha_obj
        ).order_by('hora_inicio')
        dias_semana = []
        lunes = None
        domingo = None

    return render(request, 'reservas/calendario.html', {
        'fecha': fecha_obj,
        'fecha_str': fecha_obj.isoformat(),
        'reservas': reservas,
        'usuario': request.usuario,
        'vista': vista,
        'dias_semana': dias_semana,
        'lunes': lunes,
        'domingo': domingo,
    })


# ──────────────────────────────────────────────
# 8.3. Recepcionista: Marcar No Asistida
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def marcar_no_asistida_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.estado != 'confirmada':
        messages.error(request, 'Solo se pueden marcar reservas confirmadas.')
    else:
        reserva.estado = 'no_asistida'
        reserva.save()
        messages.success(request, f'Reserva #{reserva.id} marcada como No Asistida.')

    # Redirigir de vuelta a donde vino (calendario o validación)
    next_url = request.META.get('HTTP_REFERER', 'calendario_reservas')
    return redirect(next_url)


# ──────────────────────────────────────────────
# 8.4. Recepcionista: Historial General
# ──────────────────────────────────────────────

@rol_requerido('recepcionista', 'administrador')
def historial_reservas_view(request):
    busqueda = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')

    reservas = Reserva.objects.select_related('cancha', 'usuario').all()

    if busqueda:
        reservas = reservas.filter(usuario__nombre__icontains=busqueda) | reservas.filter(usuario__correo__icontains=busqueda)
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
            reservas = reservas.filter(fecha=fecha_obj)
        except ValueError:
            pass

    reservas = reservas.order_by('-fecha', '-hora_inicio')[:100]

    return render(request, 'reservas/historial_reservas.html', {
        'reservas': reservas,
        'busqueda': busqueda,
        'fecha': fecha,
        'usuario': request.usuario,
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

    usuario = request.usuario
    return render(request, 'reservas/admin_horarios.html', {
        'horarios': horarios,
        'form': form,
        'horario_editar': horario_editar,
        'usuario': usuario,
    })


# ──────────────────────────────────────────────
# 11. Reportes (P6: municipio puede acceder)
# ──────────────────────────────────────────────

@rol_requerido('administrador', 'municipio')
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

    usuario = request.usuario
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


# ──────────────────────────────────────────────
# 13. Admin: Gestión de usuarios y roles
# ──────────────────────────────────────────────

@rol_requerido('administrador')
def admin_usuarios_view(request):
    """Panel de administración de usuarios y asignación de roles."""
    usuarios = Usuario.objects.all().order_by('-fecha_creacion')

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

    usuario = request.usuario
    return render(request, 'reservas/admin_usuarios.html', {
        'usuarios': usuarios,
        'usuario': usuario,
        'rol_form_class': EditarRolForm,
    })


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


# ──────────────────────────────────────────────
# Generador de Código QR (Imagen)
# ──────────────────────────────────────────────

def generar_qr_view(request, codigo_qr):
    """Genera y devuelve la imagen del código QR a partir de la cadena."""
    # Opcional: Validar que la reserva exista, aunque aquí solo generamos el QR visual
    get_object_or_404(Reserva, codigo_qr=codigo_qr)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type="image/png")
