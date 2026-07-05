# Mapa Tecnico del Proyecto Final

## 1. Resumen rapido

Este proyecto es un sistema web de reservas para un polideportivo hecho con **Django** y base de datos **MySQL**.

La arquitectura real del proyecto es la de un **monolito Django**:

- `polideportivo/` contiene la configuracion global del proyecto.
- `reservas/` contiene casi toda la logica del negocio.
- `static/` contiene CSS e imagenes.
- `documentacion/` guarda material de apoyo para exposicion.

Tecnologias detectadas en `requirements.txt`:

- `Django`: framework web principal.
- `mysqlclient`: conexion con MySQL.
- `qrcode`: generacion de codigos QR.
- `reportlab`: generacion de PDF.
- `openpyxl`: generacion de Excel.
- `pillow`: soporte de imagenes.

---

## 2. Estructura general del proyecto

### Raiz

- `manage.py`
  - Punto de entrada de Django para correr servidor, migraciones y comandos.
- `.gitignore`
  - Ignora archivos temporales, entorno virtual, etc.
- `requirements.txt`
  - Dependencias Python del sistema.
- `venv/`
  - Entorno virtual local. No contiene logica del sistema.

### `polideportivo/`

Carpeta del proyecto Django, enfocada en configuracion e inicio.

- `settings.py`
  - Configuracion general.
  - Base de datos MySQL.
  - apps instaladas.
  - middleware global.
  - configuracion de archivos estaticos.
- `urls.py`
  - Enruta todo el sistema a `reservas.urls`.
- `asgi.py`
  - Punto de arranque ASGI.
- `wsgi.py`
  - Punto de arranque WSGI.
- `__init__.py`
  - Marca la carpeta como paquete Python.

### `reservas/`

Es la carpeta mas importante. Aqui vive el dominio funcional del sistema.

- `models.py`
  - Define entidades/tablas del negocio.
- `forms.py`
  - Valida login, registro, reservas, horarios e interfaces de administracion.
- `urls.py`
  - Mapa de rutas funcionales del sistema.
- `codigos.py`
  - Genera y clasifica codigos de acceso y vouchers.
- `middleware.py`
  - Registra excepciones no controladas en base de datos.
- `admin.py`
  - Registro de modelos para Django admin.
- `tests.py`
  - Pruebas funcionales e integrales del sistema.
- `migrations/`
  - Historial de cambios estructurales de base de datos.
- `views/`
  - Vistas separadas por responsabilidad.
- `templates/reservas/`
  - Pantallas HTML del sistema.

### `static/`

- `static/css/style.css`
  - Estilos globales del frontend.
- `static/img/*`
  - Imagenes de canchas, logo y mapa.

### `documentacion/`

- `Presentacion_Polideportivo.md`
  - Material para exposicion.
- `Guia_Exposicion_Estructura.md`
  - Guia previa de explicacion.
- `documento escrito del polideportivo .pdf`
  - Documento escrito del proyecto.

---

## 3. Que hace cada modulo importante

## 3.1 Configuracion global

### `polideportivo/settings.py`

Funcion tecnica:

- Configura el proyecto Django.
- Declara que la app principal es `reservas`.
- Usa MySQL como motor de base de datos.
- Activa middleware propio para log de errores.
- Configura `STATICFILES_DIRS` para servir CSS e imagenes.

Puntos tecnicos relevantes:

- App instalada: `reservas` en `polideportivo/settings.py:36-44`.
- Middleware custom: `reservas.middleware.ExceptionLoggingMiddleware` en `polideportivo/settings.py:46-55`.
- Base de datos MySQL en `polideportivo/settings.py:80-93`.
- `STRICT_TRANS_TABLES` activado en `polideportivo/settings.py:88-90`.

## 3.2 Ruteo

### `polideportivo/urls.py`

- Conecta el proyecto con `reservas.urls`.
- Django admin queda en `/admin/`.

### `reservas/urls.py`

Agrupa las rutas del sistema por modulos funcionales:

- autenticacion
- canchas
- reservas
- QR
- puntos
- recepcion
- perfil
- administracion
- reportes
- exportaciones

Rutas clave:

- login y registro: `reservas/urls.py:5-8`
- reservas del usuario: `reservas/urls.py:14-19`
- canje de puntos: `reservas/urls.py:21-23`
- recepcion: `reservas/urls.py:25-32`
- reportes PDF/Excel: `reservas/urls.py:45-47`

## 3.3 Modelos de negocio

### `reservas/models.py`

Es el nucleo de datos del sistema.

Modelos definidos:

- `Usuario`
  - Usuario personalizado con nombre, correo, telefono, password, rol, puntos y estado.
- `Cancha`
  - Espacios deportivos disponibles.
- `HorarioDisponible`
  - Bloques de horario validos por cancha y dia.
- `Reserva`
  - Reserva principal hecha por el usuario.
- `ReservaBloqueo`
  - Tabla tecnica para bloquear una franja y evitar doble reserva concurrente.
- `PuntosHistorial`
  - Bitacora de puntos otorgados y canjeados.
- `LogErrores`
  - Auditoria tecnica de errores.
- `ConfiguracionPuntos`
  - Configuracion singleton de reglas de puntos.
- `ProductoBar`
  - Catalogo canjeable con puntos.
- `CanjeProducto`
  - Voucher generado por canje de productos.

## 3.4 Formularios

### `reservas/forms.py`

Centraliza validacion del sistema:

- `LoginForm`
  - Valida correo, estado del usuario y password.
- `RegistroForm`
  - Crea usuarios nuevos.
- `CanchaForm`
  - Alta/edicion de canchas.
- `ReservaForm`
  - Valida cancha, fecha, horario, invitados y conflictos basicos.
- `ReservaRecepcionForm`
  - Reserva hecha por recepcionista para otro usuario.
- `ValidacionQRForm`
  - Entrada de QR o codigo de voucher.
- `ProductoBarForm`
  - Alta/edicion de productos del bar.
- `EditarRolForm`
  - Cambio de rol por administrador.
- `EditarPerfilForm`
  - Edicion de datos del usuario.
- `ConfiguracionPuntosForm`
  - Cambio de puntos por asistencia.

## 3.5 Utilidades

### `reservas/codigos.py`

Se usa para generar codigos del sistema:

- `ACC-...` para reservas.
- `VCH-...` para vouchers.
- identifica codigos antiguos `BAR-...` por compatibilidad.

Ubicaciones:

- prefijos en `reservas/codigos.py:10-12`
- generacion de codigo de acceso en `reservas/codigos.py:33-38`
- generacion de voucher en `reservas/codigos.py:41-46`

### `reservas/middleware.py`

Manejo transversal:

- captura excepciones no manejadas
- guarda el error en `LogErrores`
- devuelve respuesta 500 amigable fuera de `DEBUG`

## 3.6 Vistas por modulo

### `reservas/views/auth.py`

Hace autenticacion por formulario + sesiones:

- `login_view`
  - autentica usuario, guarda datos en sesion y redirige por rol.
- `registro_view`
  - crea cuentas nuevas.
- `logout_view`
  - cierra sesion.

### `reservas/views/helpers.py`

Funciones base usadas en muchas vistas:

- `registrar_error`
  - escribe en `LogErrores`.
- `limpiar_bloqueos_vencidos`
  - elimina bloqueos de franjas ya expiradas.
- `login_requerido`
  - protege vistas con sesion activa.
- `rol_requerido`
  - protege vistas por rol.

### `reservas/views/canchas.py`

Pantallas de consulta:

- lista de canchas
- filtro por tipo
- disponibilidad semanal y diaria por cancha

### `reservas/views/reservas_views.py`

Gestion del usuario final:

- crear reserva
- listar mis reservas
- cancelar reserva

Aqui esta una de las piezas mas importantes de concurrencia del sistema.

### `reservas/views/recepcion.py`

Modulo operativo para recepcion:

- validar QR de reserva
- validar voucher
- crear reserva manual para un cliente
- consultar horarios disponibles por AJAX
- ver calendario diario/semanal
- ver historial mensual
- marcar no asistida
- generar ticket PDF de voucher

### `reservas/views/puntos.py`

Modulo de fidelizacion:

- muestra catalogo de productos
- descuenta puntos
- crea voucher de canje
- registra el movimiento en historial
- administra configuracion de puntos

### `reservas/views/reportes.py`

Modulo analitico:

- dashboard de reportes
- calculo de metricas
- exportacion a PDF
- exportacion a Excel

### `reservas/views/qr.py`

Modulo visual:

- genera imagen PNG del QR de una reserva
- genera imagen PNG del QR de un voucher

### `reservas/views/admin_views.py`

Backoffice:

- administracion de canchas
- administracion de horarios
- administracion de usuarios
- administracion de productos del bar

---

## 4. Donde esta `pbkdf2_sha256`

Este punto es importante: **el proyecto no implementa el hash manualmente**, sino que usa el sistema de hash de Django.

### Dato tecnico exacto

1. El hash se genera en:
   - `reservas/models.py:46-50`
   - Ahi `Usuario.save()` revisa si la password ya empieza con `pbkdf2_`.
   - Si no, ejecuta `make_password(self.password)`.

2. La validacion del hash se hace en:
   - `reservas/forms.py:45-63`
   - `LoginForm.clean()` usa `check_password(password, usuario.password)`.

3. El login crea sesion en:
   - `reservas/views/auth.py:13-44`
   - Guarda `usuario_id`, `usuario_nombre` y `usuario_rol` en `request.session`.

4. La explicacion arquitectonica ya esta escrita en:
   - `reservas/models.py:12-16`
   - El comentario del modelo `Usuario` dice que la autenticacion usa sesiones de Django y cifrado PBKDF2.

### Conclusion tecnica para decir al ingeniero

- El sistema usa **hash de password gestionado por Django**.
- `make_password()` genera el hash.
- `check_password()` lo valida.
- El prefijo esperado del hash es `pbkdf2_sha256` dentro de la cadena almacenada.
- Como en `settings.py` no se redefine `PASSWORD_HASHERS`, se aplica el hasher por defecto de Django.

---

## 5. Donde esta la concurrencia con transacciones atomicas y restriccion `UNIQUE`

Este es uno de los puntos mas fuertes del proyecto.

## 5.1 Reserva concurrente del usuario final

Ubicacion:

- `reservas/views/reservas_views.py:23-58`

Que hace:

- abre `transaction.atomic()`
- bloquea filas candidatas con `select_for_update()`
- verifica si ya existe reserva para misma cancha, fecha y franja
- crea la `Reserva`
- crea el `ReservaBloqueo`

Manejo de colision:

- `reservas/views/reservas_views.py:66-78`
- si dos peticiones compiten al mismo tiempo, captura `IntegrityError`

## 5.2 Reserva concurrente desde recepcion

Ubicacion:

- `reservas/views/recepcion.py:259-294`

Que hace:

- mismo patron: `transaction.atomic()`
- `select_for_update()`
- crea `Reserva`
- crea `ReservaBloqueo`

Manejo de colision:

- `reservas/views/recepcion.py:303-313`

## 5.3 Bloqueo fisico por restriccion `UNIQUE`

Modelo actual:

- `reservas/models.py:264-297`

Regla exacta:

- `ReservaBloqueo` tiene `UniqueConstraint(fields=['cancha', 'fecha', 'hora_inicio', 'hora_fin'])`
- nombre: `unique_bloqueo_franja_reserva`

Esto significa:

- solo puede existir **un bloqueo activo** por cancha + fecha + hora_inicio + hora_fin
- aunque dos requests lleguen casi al mismo tiempo, la base de datos no deja duplicar esa franja

## 5.4 Migracion donde queda aplicada en base de datos

Ubicacion:

- `reservas/migrations/0006_reservabloqueo.py:44-65`

Que hace:

- crea la tabla `ReservaBloqueo`
- agrega la restriccion `UNIQUE`
- migra reservas activas previas hacia bloqueos tecnicos

## 5.5 Evolucion del diseno

Antes:

- la restriccion estaba directamente en `Reserva`
- `reservas/migrations/0001_initial.py:120-123`

Luego:

- esa restriccion se elimino en `reservas/migrations/0002_remove_reserva_unique_reserva_cancha_horario.py:12-16`

Interpretacion tecnica:

- el proyecto evoluciono desde un `UNIQUE` directo en la tabla `Reserva`
- a un modelo tecnico separado `ReservaBloqueo`
- eso permite cancelar reservas o marcar no asistencia liberando la franja sin destruir la trazabilidad historica

## 5.6 Liberacion de franjas

Cuando una reserva deja de ocupar el espacio, el sistema elimina el bloqueo:

- cancelacion por usuario: `reservas/views/reservas_views.py:148-163`
- marcar no asistida en recepcion: `reservas/views/recepcion.py:393-405`
- limpieza automatica de bloqueos vencidos: `reservas/views/helpers.py:24-33`

## 5.7 Otra concurrencia importante: puntos

Ubicacion:

- `reservas/views/puntos.py:70-104`

Que hace:

- usa `transaction.atomic()`
- bloquea el usuario con `select_for_update()`
- descuenta puntos
- crea el voucher
- registra el historial de puntos

Esto evita doble canje simultaneo con el mismo saldo.

---

## 6. Donde se generan PDF y Excel

## 6.1 PDF de reportes ejecutivos

Ubicacion principal:

- `reservas/views/reportes.py:193-372`

Biblioteca:

- `reportlab`

Detalles tecnicos:

- usa `SimpleDocTemplate`
- usa `Paragraph`, `Table`, `TableStyle`, `Spacer`
- genera un PDF horizontal tipo informe ejecutivo
- devuelve `HttpResponse(..., content_type='application/pdf')`

Conclusion:

- el PDF no sale desde HTML ni desde plantilla web
- se construye **programaticamente** con ReportLab

## 6.2 Excel de reportes

Ubicacion principal:

- `reservas/views/reportes.py:376-541`

Biblioteca:

- `openpyxl`

Detalles tecnicos:

- crea `Workbook()`
- arma varias hojas:
  - `Resumen`
  - `Reservas`
  - `Usuarios`
  - `Canchas`
  - `Tendencias`
- aplica estilos, filtros, freeze panes y anchos de columna

Conclusion:

- el Excel tambien se construye **programaticamente**
- no se exporta desde una tabla HTML

## 6.3 PDF de ticket voucher

Ubicacion principal:

- generador: `reservas/views/recepcion.py:503-607`
- vista HTTP: `reservas/views/recepcion.py:610-615`

Biblioteca:

- `reportlab.pdfgen.canvas`

Tipo de salida:

- ticket pequeno tipo termico
- pensado para entregar o imprimir un comprobante de canje

## 6.4 Pantallas desde donde se dispara

Rutas:

- PDF reportes: `reservas/urls.py:45-46`
- Excel reportes: `reservas/urls.py:46-47`
- ticket voucher: `reservas/urls.py:31-32`

---

## 7. Donde estan los QR y vouchers

## 7.1 Generacion de imagen QR

Ubicacion:

- QR de reserva: `reservas/views/qr.py:13-38`
- QR de voucher: `reservas/views/qr.py:41-66`

Biblioteca:

- `qrcode`

Salida:

- `image/png`

## 7.2 Codigos de negocio

Ubicacion:

- `reservas/codigos.py`

Tipos:

- `ACC-...` para acceso a reserva
- `VCH-...` para voucher de canje
- `BAR-...` como compatibilidad legacy

## 7.3 Validacion operativa en recepcion

Ubicacion:

- `reservas/views/recepcion.py:29-203`

Que hace:

- reconoce si el codigo es de acceso o voucher
- bloquea el registro con `select_for_update()`
- cambia estados
- suma puntos por asistencia
- marca voucher como entregado

---

## 8. Estructura funcional de templates

La carpeta `reservas/templates/reservas/` representa la capa de presentacion.

### Base

- `base.html`
  - layout general, menu y estructura comun.

### Autenticacion y perfil

- `login.html`
- `registro.html`
- `perfil.html`

### Usuario final

- `lista_canchas.html`
- `disponibilidad.html`
- `crear_reserva.html`
- `mis_reservas.html`

### Recepcion

- `validar_qr.html`
- `crear_reserva_recepcion.html`
- `calendario.html`
- `historial_reservas.html`
- `ticket_voucher.html`

### Administracion

- `admin_usuarios.html`
- `admin_canchas.html`
- `admin_horarios.html`
- `admin_config_puntos.html`
- `admin_productos_bar.html`

### Analitica y puntos

- `reportes.html`
- `canjear_puntos.html`

Interpretacion tecnica:

- la UI esta separada por **rol y caso de uso**
- usuario, recepcionista, administrador y municipio tienen pantallas distintas

---

## 9. Estructura de migraciones y que significan

### `0001_initial.py`

- crea tablas base:
  - `Usuario`
  - `Cancha`
  - `HorarioDisponible`
  - `Reserva`
  - `PuntosHistorial`
- crea restricciones iniciales, incluyendo `correo unique` y `codigo_qr unique`

### `0002_remove_reserva_unique_reserva_cancha_horario.py`

- elimina el `UNIQUE` viejo de `Reserva`

### `0006_reservabloqueo.py`

- introduce `ReservaBloqueo`
- mueve la exclusividad de franja a una tabla tecnica separada

### `0008_productobar_alter_configuracionpuntos_options_and_more.py`

- agrega:
  - `ProductoBar`
  - `CanjeProducto`
- define `codigo` del voucher como `unique=True`

---

## 10. Tablas clave para diagrama entidad-relacion

Si vas a hacer un ERD, estas son las entidades principales:

- `Usuario`
- `Cancha`
- `HorarioDisponible`
- `Reserva`
- `ReservaBloqueo`
- `PuntosHistorial`
- `ConfiguracionPuntos`
- `ProductoBar`
- `CanjeProducto`
- `LogErrores`

Relaciones:

- `Usuario 1 --- N Reserva`
- `Cancha 1 --- N HorarioDisponible`
- `Cancha 1 --- N Reserva`
- `Reserva 1 --- 0..1 ReservaBloqueo`
- `Usuario 1 --- N PuntosHistorial`
- `Reserva 1 --- N PuntosHistorial` (opcional)
- `Usuario 1 --- N CanjeProducto`
- `ProductoBar 1 --- N CanjeProducto`

Restricciones importantes para explicar:

- `Usuario.correo` es `UNIQUE` en `reservas/models.py:30`
- `Reserva.codigo_qr` es `UNIQUE` en `reservas/models.py:180`
- `CanjeProducto.codigo` es `UNIQUE` en `reservas/models.py:447-450`
- `ReservaBloqueo` tiene `UNIQUE` compuesto en `reservas/models.py:292-296`

---

## 11. Diagramas recomendados para la exposicion

## 11.1 Diagrama de arquitectura

Componentes:

- Navegador
- Django URLs
- Views
- Forms
- Models
- MySQL
- Static files

Secuencia sugerida:

- navegador envia request
- `urls.py` enruta
- vista llama formulario o modelo
- modelo consulta MySQL
- vista responde HTML / PNG / PDF / XLSX

## 11.2 Diagrama de login

Flujo:

1. usuario envia correo y password
2. `LoginForm.clean()` busca usuario activo
3. `check_password()` valida hash
4. `login_view()` guarda sesion
5. redireccion segun rol

Archivos:

- `reservas/forms.py:45-63`
- `reservas/views/auth.py:13-32`

## 11.3 Diagrama de reserva concurrente

Flujo:

1. usuario envia formulario
2. `ReservaForm` valida datos
3. vista abre `transaction.atomic()`
4. `select_for_update()` revisa conflictos
5. crea `Reserva`
6. crea `ReservaBloqueo`
7. si hay carrera, la base dispara `IntegrityError`

Archivos:

- `reservas/forms.py:333-423`
- `reservas/views/reservas_views.py:23-78`
- `reservas/models.py:264-297`

## 11.4 Diagrama de validacion QR

Flujo:

1. recepcion escanea codigo
2. sistema detecta si es acceso o voucher
3. bloquea el registro con `select_for_update()`
4. si es reserva:
   - marca asistida
   - suma puntos
5. si es voucher:
   - marca entregado
   - permite ticket PDF

Archivos:

- `reservas/views/recepcion.py:29-203`
- `reservas/views/puntos.py:70-104`

## 11.5 Diagrama de exportacion

PDF:

- `reservas/views/reportes.py:193-372`

Excel:

- `reservas/views/reportes.py:376-541`

Ticket voucher:

- `reservas/views/recepcion.py:503-615`

---

## 12. Donde estan las pruebas utiles para defender el proyecto

Archivo:

- `reservas/tests.py`

Cobertura funcional visible por nombres:

- login
- registro
- reservas
- recepcion
- QR
- puntos
- accesos por rol
- administracion de canchas
- reportes
- exportacion PDF
- exportacion Excel

Ejemplos importantes:

- exportacion PDF: `reservas/tests.py:903`
- exportacion Excel: `reservas/tests.py:910`
- validacion de voucher: `reservas/tests.py:551`
- ticket voucher termico: `reservas/tests.py:575`
- reserva manual de recepcion: `reservas/tests.py:402`

---

## 13. Explicacion corta para decirle al ingeniero

Puedes resumirlo asi:

> El proyecto esta hecho en Django con una sola app de negocio llamada `reservas`.  
> Usa un modelo de usuario propio, autenticacion por sesiones y contrasenas cifradas con el sistema PBKDF2 de Django.  
> La parte critica de concurrencia esta en la creacion de reservas, donde se combinan `transaction.atomic()`, `select_for_update()` y una restriccion `UNIQUE` en la tabla tecnica `ReservaBloqueo` para impedir doble reserva de la misma franja.  
> Los reportes se exportan directamente desde Python: PDF con ReportLab y Excel con OpenPyXL.  
> Los QR se generan con `qrcode`, y recepcion valida reservas y vouchers cambiando estados y otorgando puntos en transacciones seguras.

---

## 14. Archivos mas importantes si solo vas a revisar lo esencial

Si el ingeniero quiere ver solo el corazon del sistema, ensenale estos archivos:

- `polideportivo/settings.py`
- `reservas/models.py`
- `reservas/forms.py`
- `reservas/urls.py`
- `reservas/views/reservas_views.py`
- `reservas/views/recepcion.py`
- `reservas/views/puntos.py`
- `reservas/views/reportes.py`
- `reservas/codigos.py`
- `reservas/migrations/0006_reservabloqueo.py`

