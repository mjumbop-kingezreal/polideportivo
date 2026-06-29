# Guía de Implementación - Sistema de Reservas de Canchas

## Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Python 3.10+** → [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **MySQL 8.0+** → [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
- **pip** (viene con Python)
- **Git** (opcional pero recomendado)

Para verificar, abre una terminal (CMD o PowerShell) y ejecuta:

```bash
python --version
mysql --version
pip --version
```

---

## Paso 1: Crear la base de datos en MySQL

Abre la terminal de MySQL (o MySQL Workbench) y ejecuta:

```sql
CREATE DATABASE reservas_polideportivo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



## Paso 2: Crear el entorno virtual de Python

Abre PowerShell o CMD **dentro de la carpeta del proyecto** (`proyecto final`) y ejecuta:

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar el entorno virtual (Windows CMD)
.\venv\Scripts\activate.bat
```

> **Importante:** Cada vez que abras una terminal nueva, debes activar el entorno virtual antes de trabajar.

---

## Paso 3: Instalar dependencias

Con el entorno virtual **activado**, instala Django y el conector de MySQL:

```bash
pip install django mysqlclient pillow qrcode
```

| Paquete       | Para qué sirve                              |
|---------------|---------------------------------------------|
| `django`      | Framework web principal                     |
| `mysqlclient` | Conector para que Django hable con MySQL    |
| `pillow`      | Manejo de imágenes (para los QR)            |
| `qrcode`      | Generación de códigos QR para las reservas  |

Guarda las dependencias en un archivo:

```bash
pip freeze > requirements.txt
```

---

## Paso 4: Crear el proyecto Django

```bash
django-admin startproject polideportivo .
```

> **Nota:** El punto (`.`) al final es importante. Crea el proyecto en la carpeta actual sin agregar una subcarpeta extra.

### Estructura resultante:

```
proyecto final/
├── manage.py
├── polideportivo/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── venv/
├── requirements.txt
├── Modelos y Base de Datos.md
└── Guia de Implementacion.md
```

---

## Paso 5: Configurar la conexión a MySQL

Abre el archivo `polideportivo/settings.py` y busca la sección `DATABASES`. Reemplázala por:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'reservas_polideportivo',
        'USER': 'reservas_user',
        'HOST': 'localhost',
        'PORT': '3306',
        'PASSWORD': 'tu_contraseña_segura',  # La misma del paso 1
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

También configura el idioma y zona horaria en el mismo archivo:

```python
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True
```

---

## Paso 6: Crear la app `reservas`

```bash
python manage.py startapp reservas
```

### Registrar la app en `settings.py`:

Busca `INSTALLED_APPS` y agrega `'reservas'`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservas',  # <-- Agregar aquí
]
```

### Estructura resultante:

```
proyecto final/
├── manage.py
├── polideportivo/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── reservas/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── venv/
├── requirements.txt
└── ...
```

---

## Paso 7: Definir los modelos

Abre `reservas/models.py` y reemplaza todo el contenido por:

```python
from django.db import models
from django.contrib.auth.hashers import make_password


class Usuario(models.Model):
    """Usuarios del sistema: ciudadanos, recepcionistas y administradores."""

    class Rol(models.TextChoices):
        USUARIO = 'usuario', 'Usuario'
        RECEPCIONISTA = 'recepcionista', 'Recepcionista'
        ADMINISTRADOR = 'administrador', 'Administrador'

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

    def __str__(self):
        return (
            f"Reserva #{self.id} | {self.usuario.nombre} | "
            f"{self.cancha.nombre} | {self.fecha}"
        )

    class Meta:
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        # Restricción UNIQUE para evitar reservas duplicadas
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha', 'hora_inicio', 'hora_fin'],
                name='unique_reserva_cancha_horario',
            )
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
```

---

## Paso 8: Registrar modelos en el admin de Django

Abre `reservas/admin.py` y reemplaza por:

```python
from django.contrib import admin
from .models import (
    Usuario,
    Cancha,
    HorarioDisponible,
    Reserva,
    PuntosHistorial,
    LogErrores,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'rol', 'puntos_acumulados', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('nombre', 'correo')


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_deporte', 'ubicacion', 'estado')
    list_filter = ('tipo_deporte', 'estado')
    search_fields = ('nombre',)


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo', 'cancha')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'cancha', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha', 'cancha')
    search_fields = ('usuario__nombre', 'cancha__nombre')


@admin.register(PuntosHistorial)
class PuntosHistorialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntos', 'tipo_movimiento', 'fecha')
    list_filter = ('tipo_movimiento',)


@admin.register(LogErrores)
class LogErroresAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'modulo_origen', 'nivel_severidad')
    list_filter = ('nivel_severidad',)
    search_fields = ('modulo_origen', 'descripcion_error')
```

---

## Paso 9: Crear y ejecutar migraciones

```bash
# Generar los archivos de migración
python manage.py makemigrations reservas

# Aplicar las migraciones (crea las tablas en MySQL)
python manage.py migrate
```

---

## Paso 10: Crear un superusuario para el admin

```bash
python manage.py createsuperuser
```

Te pedirá nombre de usuario, correo y contraseña. Estos datos son para acceder al panel de administración de Django.

---

## Paso 11: Probar el servidor

```bash
python manage.py runserver
```

Abre tu navegador en:

- **Página principal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Panel de administración:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Inicia sesión con el superusuario que creaste y verás todos los modelos registrados.

---

## Paso 12: Verificar las tablas en MySQL

Abre la terminal de MySQL y ejecuta:

```sql
USE reservas_polideportivo;
SHOW TABLES;
```

Deberías ver estas tablas:

```
+------------------------------------+
| Tables_in_reservas_polideportivo   |
+------------------------------------+
| auth_group                         |
| auth_group_permissions             |
| auth_permission                    |
| auth_user                          |
| cancha                             |
| django_admin_log                   |
| django_content_type                |
| django_migrations                  |
| django_session                     |
| horario_disponible                 |
| log_errores                        |
| puntos_historial                   |
| reserva                            |
| usuario                            |
+------------------------------------+
```

---

## Estructura final del proyecto

```
proyecto final/
├── manage.py
├── requirements.txt
├── Modelos y Base de Datos.md
├── Guia de Implementacion.md
│
├── polideportivo/              ← Configuración del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             ← Conexión a MySQL aquí
│   ├── urls.py
│   └── wsgi.py
│
├── reservas/                   ← App principal
│   ├── __init__.py
│   ├── admin.py                ← Registro de modelos en admin
│   ├── apps.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py     ← Se genera automáticamente
│   ├── models.py               ← Los 6 modelos aquí
│   ├── tests.py
│   └── views.py
│
└── venv/                       ← Entorno virtual (no tocar)
```

---

## Resumen de comandos en orden

```bash
# 1. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install django mysqlclient pillow qrcode
pip freeze > requirements.txt

# 3. Crear proyecto Django
django-admin startproject polideportivo .

# 4. Crear app reservas
python manage.py startapp reservas

# 5. (Editar settings.py, models.py y admin.py según la guía)

# 6. Migraciones
python manage.py makemigrations reservas
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Ejecutar servidor
python manage.py runserver
```

---

## Posibles errores comunes

| Error | Solución |
|-------|----------|
| `mysqlclient` no se instala | Instala Visual C++ Build Tools o usa `pip install pymysql` como alternativa |
| `Access denied for user` | Verifica usuario y contraseña en `settings.py` y en MySQL |
| `No module named 'reservas'` | Asegúrate de haber agregado `'reservas'` en `INSTALLED_APPS` |
| `django.db.utils.OperationalError` | Verifica que MySQL esté corriendo y la base de datos exista |
| Error de permisos en PowerShell | Ejecuta `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## ¿Qué sigue después?

Una vez que tengas la base de datos funcionando, los próximos pasos serían:

1. **Crear las vistas** (`views.py`) para cada funcionalidad
2. **Crear las URLs** (`urls.py`) de la app
3. **Crear los templates HTML** para la interfaz de usuario
4. **Implementar la lógica del QR** en la creación de reservas
5. **Implementar el sistema de puntos** automático
6. **Agregar autenticación** (login, logout, registro)
