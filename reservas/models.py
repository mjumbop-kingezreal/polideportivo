import re
from datetime import timedelta

from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone


class Usuario(models.Model):
    """Usuarios del sistema: ciudadanos, recepcionistas y administradores.

    DECISION ARQUITECTONICA: Se utiliza un modelo de usuario personalizado
    en lugar de django.contrib.auth.User para tener control total sobre los
    campos, roles y logica de autenticacion especifica del polideportivo.
    La autenticacion se maneja mediante sesiones de Django con cifrado
    PBKDF2 para las contrasenas (django.contrib.auth.hashers).
    """

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
        # Cifrar la contrasena antes de guardar si no esta cifrada
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
        FUTBOL = 'futbol', 'Futbol'
        BALONCESTO = 'baloncesto', 'Baloncesto'
        VOLEIBOL = 'voleibol', 'Voleibol'
        TENIS = 'tenis', 'Tenis'
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
    tipo_personalizado = models.CharField(max_length=80, blank=True, null=True)
    capacidad_jugadores_min = models.PositiveIntegerField(blank=True, null=True)
    capacidad_jugadores_max = models.PositiveIntegerField(blank=True, null=True)

    @property
    def tipo_deporte_label(self):
        if self.tipo_deporte == self.TipoDeporte.OTRO and self.tipo_personalizado:
            return self.tipo_personalizado
        return self.get_tipo_deporte_display()

    @property
    def capacidad_jugadores_label(self):
        if self.capacidad_jugadores_min and self.capacidad_jugadores_max:
            return f"{self.capacidad_jugadores_min} - {self.capacidad_jugadores_max} jugadores"
        if self.capacidad_jugadores_min:
            return f"Desde {self.capacidad_jugadores_min} jugadores"
        if self.capacidad_jugadores_max:
            return f"Hasta {self.capacidad_jugadores_max} jugadores"
        return 'Sin especificar'

    def __str__(self):
        return f"{self.nombre} - {self.tipo_deporte_label}"

    class Meta:
        db_table = 'cancha'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'


class HorarioDisponible(models.Model):
    """Franjas horarias en las que una cancha puede ser reservada."""

    class DiaSemana(models.IntegerChoices):
        LUNES = 1, 'Lunes'
        MARTES = 2, 'Martes'
        MIERCOLES = 3, 'Miercoles'
        JUEVES = 4, 'Jueves'
        VIERNES = 5, 'Viernes'
        SABADO = 6, 'Sabado'
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
        help_text='Lista de nombres de los acompanantes (ej. Juan, Pedro, Luis)'
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

    @property
    def has_ended(self):
        from django.utils import timezone
        today_date = timezone.localtime(timezone.now()).date()
        now_time = timezone.localtime(timezone.now()).time()
        if self.fecha < today_date:
            return True
        if self.fecha == today_date and self.hora_fin <= now_time:
            return True
        return False

    @property
    def can_cancel(self):
        return self.estado == self.Estado.CONFIRMADA and not self.is_past

    @property
    def estado_visual(self):
        if self.estado == self.Estado.CONFIRMADA and self.has_ended:
            return self.Estado.NO_ASISTIDA
        return self.estado

    @property
    def estado_visual_display(self):
        return dict(self.Estado.choices).get(self.estado_visual, self.estado_visual)

    @staticmethod
    def parsear_lista_invitados(valor):
        if not valor:
            return []

        invitados = []
        for parte in re.split(r'[\n,;]+', valor):
            nombre = ' '.join(parte.strip().split())
            if nombre:
                invitados.append(nombre)
        return invitados

    @property
    def invitados_lista(self):
        return self.parsear_lista_invitados(self.lista_invitados)

    @property
    def cantidad_invitados(self):
        return len(self.invitados_lista)

    @property
    def cantidad_total_personas(self):
        return 1 + self.cantidad_invitados

    @property
    def tiene_invitados(self):
        return self.cantidad_invitados > 0
    class Meta:
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'


class ReservaBloqueo(models.Model):
    """Bloqueo unico para una franja activa de reserva."""

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE,
        related_name='bloqueos_reserva',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,
        related_name='bloqueo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.cancha.nombre} | {self.fecha} | "
            f"{self.hora_inicio} - {self.hora_fin}"
        )

    class Meta:
        db_table = 'reserva_bloqueo'
        verbose_name = 'Bloqueo de Reserva'
        verbose_name_plural = 'Bloqueos de Reserva'
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha', 'hora_inicio', 'hora_fin'],
                name='unique_bloqueo_franja_reserva',
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
    """Registro de errores del sistema para auditoria."""

    class NivelSeveridad(models.TextChoices):
        INFO = 'info', 'Informacion'
        WARNING = 'warning', 'Advertencia'
        ERROR = 'error', 'Error'
        CRITICAL = 'critical', 'Critico'

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
    """Configuracion singleton para las reglas del programa de puntos."""

    puntos_por_asistencia = models.IntegerField(
        default=10,
        help_text='Puntos otorgados al usuario por cada asistencia confirmada.'
    )

    def save(self, *args, **kwargs):
        # Patron singleton: solo permite un registro
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        """Obtiene o crea la configuracion singleton."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'Configuracion de Puntos (asistencia={self.puntos_por_asistencia})'

    class Meta:
        db_table = 'configuracion_puntos'
        verbose_name = 'Configuracion de Puntos'
        verbose_name_plural = 'Configuracion de Puntos'


class ProductoBar(models.Model):
    """Productos del bar canjeables con puntos acumulados."""

    class Categoria(models.TextChoices):
        BEBIDA = 'bebida', 'Bebida'
        SNACK = 'snack', 'Snack'
        OTRO = 'otro', 'Otro'

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
    )
    puntos_requeridos = models.PositiveIntegerField(
        help_text='Cantidad de puntos necesarios para canjear este producto.'
    )
    stock = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Cantidad disponible. Si se deja vacio, el producto no tendra limite de stock.'
    )
    disponible = models.BooleanField(default=True)
    descripcion = models.CharField(max_length=200, blank=True)

    @property
    def tiene_stock(self):
        return self.stock is None or self.stock > 0

    @property
    def stock_resumen(self):
        if self.stock is None:
            return 'Sin limite'
        if self.stock == 0:
            return 'Agotado'
        return str(self.stock)

    def __str__(self):
        return f"{self.nombre} ({self.puntos_requeridos} pts)"

    class Meta:
        db_table = 'producto_bar'
        verbose_name = 'Producto del Bar'
        verbose_name_plural = 'Productos del Bar'
        ordering = ['categoria', 'puntos_requeridos']


class CanjeProducto(models.Model):
    """Registro de canjes de productos del bar (vouchers)."""

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ENTREGADO = 'entregado', 'Entregado'
        CANCELADO = 'cancelado', 'Cancelado'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='canjes_productos',
    )
    producto = models.ForeignKey(
        ProductoBar,
        on_delete=models.PROTECT,
        related_name='canjes',
    )
    puntos_usados = models.PositiveIntegerField()
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text='Codigo unico para presentar en el bar.'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    VIGENCIA_DIAS = 30

    def __str__(self):
        return (
            f"Canje #{self.id} | {self.usuario.nombre} | "
            f"{self.producto.nombre} | {self.codigo}"
        )

    @property
    def fecha_caducidad(self):
        return self.fecha + timedelta(days=self.VIGENCIA_DIAS)

    @property
    def esta_caducado(self):
        return timezone.now() >= self.fecha_caducidad

    @property
    def dias_restantes(self):
        if self.esta_caducado:
            return 0
        delta = self.fecha_caducidad.date() - timezone.localdate()
        return max(delta.days, 0)

    @property
    def esta_vigente(self):
        return self.estado == self.Estado.PENDIENTE and not self.esta_caducado

    @property
    def estado_visual(self):
        if self.estado == self.Estado.ENTREGADO:
            return 'canjeado'
        if self.estado == self.Estado.CANCELADO:
            return 'cancelado'
        if self.esta_caducado:
            return 'caducado'
        return 'vigente'

    @property
    def estado_visual_label(self):
        labels = {
            'vigente': 'Vigente',
            'caducado': 'Caducado',
            'canjeado': 'Canjeado',
            'cancelado': 'Cancelado',
        }
        return labels.get(self.estado_visual, self.estado_visual.title())

    @property
    def vigencia_resumen(self):
        if self.estado == self.Estado.ENTREGADO:
            return 'Canjeado en barra'
        if self.estado == self.Estado.CANCELADO:
            return 'Cancelado'
        if self.esta_caducado:
            return 'Caducado'
        if self.dias_restantes == 0:
            return 'Vence hoy'
        if self.dias_restantes == 1:
            return 'Vence manana'
        return f'Vence en {self.dias_restantes} dias'

    class Meta:
        db_table = 'canje_producto'
        verbose_name = 'Canje de Producto'
        verbose_name_plural = 'Canjes de Productos'
        ordering = ['-fecha']


