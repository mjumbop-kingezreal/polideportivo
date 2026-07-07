# PoliReserva

Sistema web de reservas de canchas deportivas para un polideportivo, desarrollado con Django y MySQL. El proyecto permite gestionar usuarios, canchas, horarios, reservas, validacion mediante QR, programa de puntos y reportes administrativos.

## Que incluye este proyecto

- Registro e inicio de sesion de usuarios.
- Gestion de roles: usuario, recepcionista, administrador y municipio.
- Consulta de canchas y disponibilidad horaria.
- Creacion y cancelacion de reservas.
- Generacion y validacion de codigos QR.
- Programa de puntos por asistencia.
- Canje de productos del bar con puntos acumulados.
- Paneles administrativos para usuarios, canchas, horarios, puntos y productos.
- Reportes exportables en PDF y Excel.

## Tecnologias usadas

- Python
- Django 6
- MySQL
- HTML, CSS
- `qrcode`
- `reportlab`
- `openpyxl`

## Estructura principal

```text
PROYECTO FINAL/
|-- manage.py
|-- requirements.txt
|-- README.md
|-- polideportivo/     # Configuracion principal del proyecto Django
|-- reservas/          # App principal del sistema
|-- static/            # Archivos estaticos
`-- documentacion/     # Guias y documentos de apoyo
```

## Requisitos previos

Antes de ejecutar el proyecto, asegurate de tener instalado:

- Python 3.12 o compatible
- MySQL Server
- `pip`

## Instalacion

1. Clona el repositorio.
2. Crea y activa un entorno virtual.
3. Instala las dependencias.

```bash
python -m venv venv
```

### Activar entorno virtual

En PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

En CMD:

```bash
.\venv\Scripts\activate.bat
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuracion de base de datos

El proyecto usa MySQL. Crea primero la base de datos:

```sql
CREATE DATABASE reservas_polideportivo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Luego revisa la configuracion en [polideportivo/settings.py](/C:/Users/DELL/Documents/PROYECTO%20FINAL/polideportivo/settings.py) y ajusta:

- `NAME`
- `USER`
- `PASSWORD`
- `HOST`
- `PORT`

Importante:

- No es buena practica subir credenciales reales al repositorio.
- Lo ideal es mover estas configuraciones a variables de entorno antes de publicar el proyecto.

## Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## Ejecutar el proyecto

```bash
python manage.py runserver
```

Abre en el navegador:

- Aplicacion: `http://127.0.0.1:8000/`
- Administracion Django: `http://127.0.0.1:8000/admin/`

## Modulos principales

### Usuarios

El sistema maneja usuarios con distintos roles:

- Usuario
- Recepcionista
- Administrador
- Municipio

### Reservas

Permite:

- consultar disponibilidad,
- reservar canchas,
- cancelar reservas activas,
- visualizar historial y calendario.

### QR

Cada reserva puede generar un codigo QR para control y validacion en recepcion.

### Puntos y canjes

Los usuarios acumulan puntos por asistencia y pueden canjearlos por productos del bar mediante vouchers.

### Reportes

El sistema incluye exportacion de informacion en:

- PDF
- Excel

## Pruebas

El repositorio incluye pruebas en [reservas/tests.py](/C:/Users/DELL/Documents/PROYECTO%20FINAL/reservas/tests.py).

Para ejecutarlas:

```bash
python manage.py test
```

## Documentacion adicional

En la carpeta [documentacion](/C:/Users/DELL/Documents/PROYECTO%20FINAL/documentacion) hay material complementario del proyecto, incluyendo una guia de implementacion.

## Que suele llevar un README

Cuando subes un repositorio, normalmente el `README.md` explica:

- que hace el proyecto,
- que tecnologias usa,
- como instalarlo,
- como ejecutarlo,
- que funcionalidades incluye,
- quien lo puede usar o mantener.

Eso ayuda a que cualquier persona entienda el repositorio sin tener que abrir el codigo primero.
