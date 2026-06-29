from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models import Q


class Usuario(models.Model):
    """Usuarios del sistema: ciudadanos, recepcionistas y administradores."""

    class Rol(models.TextChoices):
        USUARIO = 'usuario', 'Usuario'
        RECEPCIONISTA = 'recepcionista', 'Recepcionista'
        ADMINISTRADOR = 'administrador', 'Administrador'
        MUNICIPIO = 'municipio', 'Municipio'

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'

    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.USUARIO,
    )
    puntos_acumulados = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )

    def save(self, *args, **kwargs):
        # Cifrar la contraseña antes de guardar si no está cifrada
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Cancha(models.Model):
    """Canchas deportivas disponibles en el polideportivo."""

    class TipoDeporte(models.TextChoices):
        FUTBOL = 'futbol', 'Fútbol'
        BALONCESTO = 'baloncesto', 'Baloncesto'
        VOLEIBOL = 'voleibol', 'Voleibol'
        TENIS = 'tenis', 'Tenis'
        MICROFUTBOL = 'microfutbol', 'Microfútbol'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        MANTENIMIENTO = 'mantenimiento', 'En Mantenimiento'
        FUERA_SERVICIO = 'fuera_servicio', 'Fuera de Servicio'

    nombre = models.CharField(max_length=100)
    tipo_deporte = models.CharField(
        max_length=20,
        choices=TipoDeporte.choices,
    )
    ubicacion = models.CharField(max_length=200)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_deporte_display()}"

    class Meta:
        db_table = 'cancha'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'


class HorarioDisponible(models.Model):
    """Franjas horarias en las que una cancha puede ser reservada."""

    class DiaSemana(models.IntegerChoices):
        LUNES = 1, 'Lunes'
        MARTES = 2, 'Martes'
        MIERCOLES = 3, 'Miércoles'
        JUEVES = 4, 'Jueves'
        VIERNES = 5, 'Viernes'
        SABADO = 6, 'Sábado'
        DOMINGO = 7, 'Domingo'

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE,
        related_name='horarios',
    )
    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.cancha.nombre} | "
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio} - {self.hora_fin}"
        )

    class Meta:
        db_table = 'horario_disponible'
        verbose_name = 'Horario Disponible'
        verbose_name_plural = 'Horarios Disponibles'
        ordering = ['dia_semana', 'hora_inicio']


class Reserva(models.Model):
    """Reservas de canchas realizadas por los usuarios."""

    class Estado(models.TextChoices):
        CONFIRMADA = 'confirmada', 'Confirmada'
        CANCELADA = 'cancelada', 'Cancelada'
        NO_ASISTIDA = 'no_asistida', 'No Asistida'
        ASISTIDA = 'asistida', 'Asistida'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.CONFIRMADA,
    )
    codigo_qr = models.CharField(max_length=255, unique=True, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    lista_invitados = models.TextField(
        blank=True, 
        null=True,
        help_text="Lista de nombres de los acompañantes (ej. Juan, Pedro, Luis)"
    )

    def __str__(self):
        return (
            f"Reserva #{self.id} | {self.usuario.nombre} | "
            f"{self.cancha.nombre} | {self.fecha}"
        )

    @property
    def is_past(self):
        from django.utils import timezone
        today_date = timezone.localtime(timezone.now()).date()
        now_time = timezone.localtime(timezone.now()).time()
        if self.fecha < today_date:
            return True
        if self.fecha == today_date and self.hora_inicio < now_time:
            return True
        return False

    class Meta:
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha', 'hora_inicio', 'hora_fin'],
                condition=Q(estado__in=['confirmada', 'asistida']),
                name='unique_reserva_activa_por_franja',
            ),
        ]


class PuntosHistorial(models.Model):
    """Historial de movimientos de puntos por usuario."""

    class TipoMovimiento(models.TextChoices):
        OTORGADO = 'otorgado', 'Otorgado'
        CANJEADO = 'canjeado', 'Canjeado'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='puntos_historial',
    )
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='puntos',
    )
    puntos = models.IntegerField()
    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TipoMovimiento.choices,
    )
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.usuario.nombre} | "
            f"{self.get_tipo_movimiento_display()} | "
            f"{self.puntos} pts"
        )

    class Meta:
        db_table = 'puntos_historial'
        verbose_name = 'Historial de Puntos'
        verbose_name_plural = 'Historial de Puntos'


class LogErrores(models.Model):
    """Registro de errores del sistema para auditoría."""

    class NivelSeveridad(models.TextChoices):
        INFO = 'info', 'Información'
        WARNING = 'warning', 'Advertencia'
        ERROR = 'error', 'Error'
        CRITICAL = 'critical', 'Crítico'

    fecha = models.DateTimeField(auto_now_add=True)
    modulo_origen = models.CharField(max_length=100)
    descripcion_error = models.TextField()
    nivel_severidad = models.CharField(
        max_length=10,
        choices=NivelSeveridad.choices,
        default=NivelSeveridad.ERROR,
    )

    def __str__(self):
        return (
            f"[{self.get_nivel_severidad_display()}] "
            f"{self.modulo_origen} - {self.fecha}"
        )

    class Meta:
        db_table = 'log_errores'
        verbose_name = 'Log de Error'
        verbose_name_plural = 'Log de Errores'
        ordering = ['-fecha']

class ConfiguracionPuntos(models.Model):
    """Configuración singleton para las reglas del programa de puntos."""
    puntos_por_asistencia = models.IntegerField(
        default=10,
        help_text='Puntos otorgados al usuario por cada asistencia confirmada.'
    )
    minimo_canje = models.IntegerField(
        default=50,
        help_text='Cantidad mínima de puntos requerida para realizar un canje.'
    )
    descripcion_beneficio = models.TextField(
        default='Canjea tus puntos por bebidas en el bar, minutos adicionales de uso o prioridad en torneos.',
        help_text='Descripción de los beneficios disponibles al canjear puntos.'
    )

    def save(self, *args, **kwargs):
        # Patrón singleton: solo permite un registro
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        """Obtiene o crea la configuración singleton."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'Configuración de Puntos (asistencia={self.puntos_por_asistencia}, mín. canje={self.minimo_canje})'

    class Meta:
        db_table = 'configuracion_puntos'
        verbose_name = 'Configuración de Puntos'
        verbose_name_plural = 'Configuración de Puntos'
