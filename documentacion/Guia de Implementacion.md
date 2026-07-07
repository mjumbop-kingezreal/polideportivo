# Guía de Implementación - Sistema de Reservas de Canchas
## Paso : Instalar dependencias



| Paquete       | Para qué sirve                              |
|---------------|---------------------------------------------|
| `Django`      | Framework web principal                     |
| `mysqlclient` | Conector para que Django hable con MySQL    |
| `pillow`      | Manejo de imágenes (para los QR)            |
| `qrcode`      | Generación de códigos QR para las reservas  |
| `sqlparse`    | Manejo de SQL                               |
| `tzdata`      | Manejo de la zona horaria                   |
| `openpyxl`    | Generación de reportes en Excel             |


---

## Paso : Crear el entorno virtual de Python

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
Con el entorno virtual **activado**, instala todas las dependencias usando el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```


## Paso : Crear el proyecto Django

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

## Paso :Crear la base de datos en MySQL y Configurar la conexión a MySQL  

Abre la terminal de MySQL (o MySQL Workbench) y ejecuta:

```sql
CREATE DATABASE reservas_polideportivo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
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


## Paso 9: Crear y ejecutar migraciones

```bash
# Generar los archivos de migración
python manage.py makemigrations reservas

# Aplicar las migraciones (crea las tablas en MySQL)
python manage.py migrate
```

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

1. **Crear las vistas** (`views.py`) para cada funcionalidad
2. **Crear las URLs** (`urls.py`) de la app
3. **Crear los templates HTML** para la interfaz de usuario
4. **Implementar la lógica del QR** en la creación de reservas
5. **Implementar el sistema de puntos** automático
6. **Agregar autenticación** (login, logout, registro)
