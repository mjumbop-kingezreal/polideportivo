# 🔍 Auditoría: Documento Escrito vs. Código Implementado

Comparación línea por línea del [documentancion de todo.md](file:///c:/Users/DELL/Documents/PROYECTO FINAL/documentancion de todo.md) (PDF convertido) contra el código fuente del proyecto.

---

## 📋 Resumen Ejecutivo

| Categoría | Documentado | Implementado | Estado |
|---|---|---|---|
| **RF (Funcionales)** | 12 | 11 completos, 1 parcial | ⚠️ 92% |
| **RNF (No Funcionales)** | 8 | 6 completos, 1 parcial, 1 faltante | ⚠️ 81% |
| **Actores/Roles** | 4 definidos | 3 implementados | ⚠️ 75% |
| **Modelos de datos** | 6 tablas | 6 tablas | ✅ 100% |
| **Herramientas** | 5 tecnologías | 5 tecnologías | ✅ 100% |
| **Cuestiones de diseño** | 4 cuestiones | 3 completas, 1 parcial | ⚠️ 88% |

---

## 👥 Actores del Sistema (Documento vs. Código)

El documento define **4 actores**:

### ✅ Actor 1: Usuario (Ciudadano)
**Documento dice:** *"Consulta disponibilidad de canchas, realiza reservas gratuitas, puede cancelarlas, acumula puntos por uso responsable y presenta el código QR al ingresar al polideportivo."*

| Función documentada | ¿Implementado? | Ubicación en código |
|---|---|---|
| Consultar disponibilidad | ✅ | [disponibilidad_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L174-L243) |
| Realizar reservas | ✅ | [crear_reserva_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L250-L301) |
| Cancelar reservas | ✅ | [cancelar_reserva_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L318-L338) |
| Acumular puntos | ✅ | +10 puntos al crear reserva (líneas 270-278) |
| Presentar código QR | ✅ | [generar_qr_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L727-L744) genera imagen QR |

**Veredicto:** ✅ **100% implementado**

---

### ✅ Actor 2: Personal Recepcionista
**Documento dice:** *"Registra reservas presenciales o telefónicas en el sistema, consulta el calendario diario y semanal, escanea el código QR con el teléfono para validar el acceso y puede consultar el historial de uso."*

| Función documentada | ¿Implementado? | Ubicación en código |
|---|---|---|
| Registrar reservas presenciales | ✅ | [crear_reserva_recepcion_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L395-L447) |
| Consultar calendario diario | ✅ | [calendario_reservas_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L454-L474) |
| Consultar calendario semanal | ⚠️ | Solo filtra por **un día**, no por semana completa |
| Escanear QR para validar acceso | ✅ | [validar_qr_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L345-L388) |
| Consultar historial de uso | ✅ | [historial_reservas_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L501-L524) |

**Veredicto:** ⚠️ **90% implementado** — Falta vista semanal del calendario (solo tiene diaria)

---

### ✅ Actor 3: Administrador
**Documento dice:** *"Crea y actualiza canchas, define horarios disponibles, administra usuarios y roles, configura las reglas del programa de puntos y consulta reportes de uso y estadísticas."*

| Función documentada | ¿Implementado? | Ubicación en código |
|---|---|---|
| Crear/actualizar canchas | ✅ | [admin_canchas_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L531-L562) |
| Definir horarios disponibles | ✅ | [admin_horarios_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L569-L599) |
| Administrar usuarios y roles | ✅ | [admin_usuarios_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L669-L720) |
| Configurar reglas de puntos | ❌ | **No existe** — Los puntos están hardcodeados a 10 por reserva |
| Consultar reportes y estadísticas | ✅ | [reportes_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L606-L634) |

**Veredicto:** ⚠️ **80% implementado** — Falta panel de configuración de reglas de puntos

---

### ❌ Actor 4: Municipio
**Documento dice:** *"Como propietario y gestor del polideportivo, el Municipio es un actor directo que utiliza el panel administrativo del sistema para gestionar la infraestructura, configurar los horarios disponibles, establecer las reglas del programa de puntos y extraer reportes estadísticos operativos."*

| Función documentada | ¿Implementado? | Detalle |
|---|---|---|
| Rol "Municipio" separado | ❌ | No existe como rol en el modelo |
| Panel administrativo propio | ❌ | No hay diferenciación con Administrador |

> [!IMPORTANT]
> El documento define 4 actores pero el código solo implementa 3 roles: `usuario`, `recepcionista`, `administrador`. El actor **"Municipio"** no tiene un rol propio. En la práctica, las funciones del Municipio las cumple el Administrador, lo cual es aceptable si se documenta así, pero no coincide exactamente con el documento.

---

## ✅ Requerimientos Funcionales (RF-01 a RF-12)

### RF-01: Registro de usuarios
**Documento:** *"El sistema permite registrar usuarios con nombre, correo, contraseña y rol asignado"*

| Aspecto | Estado | Código |
|---|---|---|
| Campos: nombre, correo, contraseña | ✅ | [RegistroForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L42-L92) |
| Rol asignado automáticamente | ✅ | `usuario.rol = 'usuario'` en línea 89 |
| Teléfono (adicional al doc) | ✅ | Campo extra implementado |

**Veredicto:** ✅ **Cumple**

---

### RF-02: Inicio de sesión seguro
**Documento:** *"Los usuarios ingresan con usuario y contraseña; el acceso se controla por roles"*

| Aspecto | Estado | Código |
|---|---|---|
| Login con correo + contraseña | ✅ | [LoginForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L6-L39) |
| Control de acceso por roles | ✅ | Decoradores `login_requerido` y `rol_requerido` |
| Verificación cuenta activa | ✅ | `estado='activo'` en consulta |
| Redirección según rol | ✅ | Admin → usuarios, Recep → QR, User → canchas |

**Veredicto:** ✅ **Cumple**

---

### RF-03: Consulta de disponibilidad
**Documento:** *"El usuario puede ver las canchas y franjas horarias disponibles por fecha"*

| Aspecto | Estado | Código |
|---|---|---|
| Ver canchas disponibles | ✅ | [lista_canchas_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L147-L167) |
| Consultar por fecha | ✅ | [disponibilidad_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L174-L243) |
| Mostrar franjas horarias | ✅ | Filtra `HorarioDisponible` por día de semana |
| Indicar horarios ocupados | ✅ | `h.is_ocupado = True` |
| Indicar horarios pasados | ✅ | `h.is_past = True` |

**Veredicto:** ✅ **Cumple**

---

### RF-04: Realizar reserva
**Documento:** *"El usuario selecciona cancha y horario; el sistema confirma mediante transacción atómica"*

| Aspecto | Estado | Código |
|---|---|---|
| Seleccionar cancha y horario | ✅ | [ReservaForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L146-L241) |
| Validación de duplicados | ✅ | Verifica reservas `confirmada` o `asistida` |
| Validación de franja válida | ✅ | Consulta `HorarioDisponible` |
| **Transacción atómica** | ❌ | **No usa `transaction.atomic()`** — La verificación y el INSERT no están en transacción |
| Restricción UNIQUE en BD | ❌ | **No existe** `unique_together` en el modelo `Reserva` |

> [!CAUTION]
> **Hallazgo crítico**: El documento especifica que las reservas deben usar **transacciones atómicas** y una **restricción UNIQUE** en BD sobre `(cancha, fecha, hora_inicio, hora_fin)`. Ninguna de las dos está implementada. La validación solo se hace a nivel de aplicación en el `clean()` del formulario, lo cual **no previene condiciones de carrera** si dos usuarios envían la reserva al mismo tiempo.

**Veredicto:** ⚠️ **Parcialmente cumple** — Funciona pero sin protección de concurrencia real

---

### RF-05: Cancelar reserva
**Documento:** *"El usuario puede cancelar una reserva activa desde su cuenta"*

| Aspecto | Estado | Código |
|---|---|---|
| Cancelar reserva confirmada | ✅ | [cancelar_reserva_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L318-L338) |
| Solo reservas propias | ✅ | Filtra `usuario=usuario` |
| No cancelar pasadas | ✅ | Verifica `reserva.is_past` |
| Cambio a estado 'cancelada' | ✅ | `reserva.estado = 'cancelada'` |

**Veredicto:** ✅ **Cumple**

---

### RF-06: Registro de reserva presencial
**Documento:** *"El recepcionista puede registrar reservas en nombre de un usuario"*

| Aspecto | Estado | Código |
|---|---|---|
| Recepcionista crea reserva para otro | ✅ | [crear_reserva_recepcion_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L395-L447) |
| Selección de cliente | ✅ | [ReservaRecepcionForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L244-L255) con campo `usuario` |
| Otorga puntos al cliente | ✅ | +10 puntos al cliente (no al recepcionista) |

**Veredicto:** ✅ **Cumple**

---

### RF-07: Generación de código QR
**Documento:** *"Al confirmar la reserva, el sistema genera un código QR único e irrepetible"*

| Aspecto | Estado | Código |
|---|---|---|
| Generación UUID único | ✅ | `codigo_qr=str(uuid.uuid4())` en línea 264 |
| Campo unique en BD | ✅ | `unique=True` en [models.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/models.py#L150) |
| Generación imagen QR | ✅ | [generar_qr_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L727-L744) con librería `qrcode` |

**Veredicto:** ✅ **Cumple**

---

### RF-08: Validación de acceso por QR
**Documento:** *"El recepcionista escanea el QR para verificar fecha, hora, token y estado de la reserva"*

| Aspecto | Estado | Código |
|---|---|---|
| Buscar por código QR | ✅ | `Reserva.objects.get(codigo_qr=codigo)` |
| Verificar estado confirmada | ✅ | `if reserva.estado != 'confirmada'` |
| Verificar fecha vigente | ✅ | `reserva.fecha < date.today()` |
| Marcar como asistida | ✅ | `reserva.estado = 'asistida'` |
| Solo recepcionista/admin | ✅ | `@rol_requerido('recepcionista', 'administrador')` |
| **Verificar hora** | ⚠️ | Solo verifica la **fecha**, no verifica si la **hora** actual coincide con la franja |

**Veredicto:** ⚠️ **Casi cumple** — El documento dice verificar "fecha, hora, token y estado" pero solo verifica fecha, token y estado (no la hora)

---

### RF-09: Gestión de canchas y horarios
**Documento:** *"El administrador crea, edita y desactiva canchas y sus franjas horarias disponibles"*

| Aspecto | Estado | Código |
|---|---|---|
| Crear canchas | ✅ | [admin_canchas_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L531-L562) |
| Editar canchas | ✅ | GET `?editar=ID` |
| Desactivar canchas | ✅ | Campo `estado` con opción "Fuera de Servicio" |
| Crear horarios | ✅ | [admin_horarios_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L569-L599) |
| Editar horarios | ✅ | GET `?editar=ID` |
| Desactivar horarios | ✅ | Campo `activo` (checkbox) |
| **Eliminar canchas/horarios** | ❌ | No hay funcionalidad de eliminación |

**Veredicto:** ✅ **Cumple** (el doc dice "crea, edita y desactiva", no menciona eliminar)

---

### RF-10: Administración de usuarios y roles
**Documento:** *"El administrador gestiona cuentas, roles y permisos del personal"*

| Aspecto | Estado | Código |
|---|---|---|
| Listar usuarios | ✅ | [admin_usuarios_view](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/views.py#L669-L720) |
| Cambiar rol | ✅ | Acción `cambiar_rol` con [EditarRolForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L290-L298) |
| Activar/desactivar cuenta | ✅ | Acción `toggle_estado` |
| Auto-protección | ✅ | No puede desactivar su propia cuenta |

**Veredicto:** ✅ **Cumple**

---

### RF-11: Programa de puntos
**Documento:** *"El sistema otorga puntos por asistencia y permite su canje por beneficios"*

| Aspecto | Estado | Código |
|---|---|---|
| Otorgar puntos por reserva | ✅ | +10 puntos al crear reserva |
| Modelo PuntosHistorial | ✅ | [PuntosHistorial](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/models.py#L182-L219) |
| Formulario de canje | ✅ | [CanjePuntosForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L268-L288) |
| **Vista para canjear** | ❌ | **No existe vista, URL ni template** |
| **Puntos por asistencia (no solo reserva)** | ❌ | Otorga puntos al **crear** reserva, no al **asistir** |
| **Configurar reglas de puntos** | ❌ | Puntos hardcodeados a 10, sin panel de config |

> [!CAUTION]
> El documento dice *"otorga puntos por asistencia"* pero el código otorga puntos al **crear** la reserva (líneas 270-278 de views.py). Según el documento, debería otorgar puntos cuando el QR se valida (asistencia confirmada). Además, no existe la funcionalidad de **canje de puntos** — el formulario existe pero no tiene vista.

**Veredicto:** ⚠️ **Parcialmente cumple** — 3 aspectos sin implementar

---

### RF-12: Consulta de reportes y estadísticas
**Documento:** *"El administrador y el Municipio pueden extraer reportes de uso del polideportivo"*

| Aspecto | Estado | Código |
|---|---|---|
| Total reservas | ✅ | `Reserva.objects.count()` |
| Reservas por estado | ✅ | Confirmadas, canceladas, no asistidas |
| Total usuarios | ✅ | `Usuario.objects.count()` |
| Total canchas | ✅ | `Cancha.objects.count()` |
| Historial de puntos | ✅ | Últimos 50 movimientos |
| Últimas reservas | ✅ | Últimas 20 con relación a usuario/cancha |
| Solo admin | ✅ | `@rol_requerido('administrador')` |
| Acceso del Municipio | ❌ | No hay rol Municipio |

**Veredicto:** ✅ **Cumple** (si se asume Municipio = Administrador)

---

## 🔧 Requerimientos No Funcionales (RNF-01 a RNF-08)

### ✅ RNF-01: Seguridad en el acceso
**Documento:** *"Contraseñas cifradas con PBKDF2; tokens QR firmados criptográficamente; protección CSRF"*

| Aspecto | Estado | Código |
|---|---|---|
| PBKDF2 para contraseñas | ✅ | `make_password()` / `check_password()` de Django |
| Tokens QR con UUID | ✅ | `uuid.uuid4()` — aunque no es "firmado criptográficamente" |
| Protección CSRF | ✅ | `CsrfViewMiddleware` en [settings.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/polideportivo/settings.py#L47) |

> [!NOTE]
> El documento menciona "tokens QR firmados criptográficamente". En el código se usa `uuid.uuid4()` que es aleatorio pero **no firmado criptográficamente**. Funcionalmente es seguro porque se valida contra la BD, pero técnicamente no es una firma criptográfica.

**Veredicto:** ✅ **Cumple** (con nota menor sobre firma criptográfica)

---

### ✅ RNF-02: Autorización por roles
**Documento:** *"Tres niveles de acceso: Usuario, Personal y Administrador, con permisos diferenciados"*

| Aspecto | Estado | Código |
|---|---|---|
| Rol Usuario | ✅ | `Rol.USUARIO = 'usuario'` |
| Rol Personal (recepcionista) | ✅ | `Rol.RECEPCIONISTA = 'recepcionista'` |
| Rol Administrador | ✅ | `Rol.ADMINISTRADOR = 'administrador'` |
| Permisos diferenciados | ✅ | Decoradores `@login_requerido` y `@rol_requerido` |

**Veredicto:** ✅ **Cumple**

---

### ⚠️ RNF-03: Integridad de datos
**Documento:** *"Restricción UNIQUE en la BD sobre (idCancha, fecha, horaInicio, horaFin) para evitar duplicados"*

| Aspecto | Estado | Código |
|---|---|---|
| Restricción UNIQUE en BD | ❌ | **No existe `unique_together` en modelo Reserva** |
| Validación a nivel aplicación | ✅ | `clean()` en [ReservaForm](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py#L228-L239) |

> [!WARNING]
> El documento requiere explícitamente una restricción `UNIQUE` a nivel de base de datos. Esto no está implementado. Solo se valida en el formulario, lo cual no protege contra inserciones concurrentes.

**Veredicto:** ❌ **No cumple** — Falta la restricción a nivel de BD

---

### ✅ RNF-04: Disponibilidad del sistema
**Documento:** *"Plataforma web accesible desde cualquier navegador en dispositivo móvil o escritorio"*

| Aspecto | Estado | Código |
|---|---|---|
| Plataforma web | ✅ | Django web app |
| Responsivo (móvil/escritorio) | ✅ | CSS con `viewport` y diseño adaptable en [base.html](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/templates/reservas/base.html) |

**Veredicto:** ✅ **Cumple**

---

### ✅ RNF-05: Tiempo de respuesta eficiente
**Documento:** *"La consulta de disponibilidad y el registro de reservas deben ejecutarse con respuesta inmediata"*

| Aspecto | Estado | Código |
|---|---|---|
| Consultas optimizadas | ✅ | `select_related()` para evitar N+1 queries |
| Sin procesamiento pesado | ✅ | Operaciones simples de BD |
| Paginación de resultados | ✅ | Reportes limitan a 50/20 registros |

**Veredicto:** ✅ **Cumple**

---

### ✅ RNF-06: Mantenibilidad
**Documento:** *"Arquitectura MVC que permite modificar cada capa de forma independiente sin afectar las demás"*

| Aspecto | Estado | Código |
|---|---|---|
| Separación Modelo-Vista-Template | ✅ | `models.py`, `views.py`, `templates/` |
| Forms separados | ✅ | [forms.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/forms.py) con 9 formularios |
| URLs separadas | ✅ | [urls.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/urls.py) |
| Admin separado | ✅ | [admin.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/admin.py) |

**Veredicto:** ✅ **Cumple**

---

### ✅ RNF-07: Escalabilidad
**Documento:** *"El diseño permite incorporar futuras funcionalidades como app móvil o notificaciones"*

| Aspecto | Estado | Código |
|---|---|---|
| Arquitectura modular | ✅ | App Django independiente `reservas` |
| Modelos extensibles | ✅ | Modelos bien definidos con relaciones claras |
| URLs RESTful | ✅ | Rutas limpias y organizadas |

**Veredicto:** ✅ **Cumple**

---

### ❌ RNF-08: Trazabilidad y auditoría
**Documento:** *"Todos los errores se registran en la tabla log_errores con fecha, módulo y nivel de severidad"*

| Aspecto | Estado | Código |
|---|---|---|
| Modelo LogErrores | ✅ | [LogErrores](file:///c:/Users/DELL/Documents/PROYECTO FINAL/reservas/models.py#L222-L250) |
| Campos: fecha, módulo, severidad | ✅ | `fecha`, `modulo_origen`, `nivel_severidad` |
| Admin para LogErrores | ✅ | Registrado en admin.py |
| **Registrar errores en vistas** | ❌ | **No se usa en ninguna vista** |
| **Middleware de excepciones** | ❌ | **No hay middleware personalizado** |

> [!CAUTION]
> El documento dice *"Todos los errores se registran en la tabla log_errores"* y menciona un *"middleware global de excepciones"*. En el código, el modelo existe pero **nunca se usa**. No hay ningún `LogErrores.objects.create()` ni middleware personalizado en todo el proyecto.

**Veredicto:** ❌ **No cumple** — El modelo existe pero nunca registra errores

---

## 🏗️ Cuestiones Clave del Diseño

### ⚠️ Concurrencia
**Documento dice:** *"La operación de crear una reserva se ejecuta dentro de una transacción atómica... se define una restricción UNIQUE a nivel de base de datos sobre (idCancha, fecha, horaInicio, horaFin)"*

| Aspecto | ¿Implementado? |
|---|---|
| `transaction.atomic()` | ❌ No se usa |
| `SELECT FOR UPDATE` | ❌ No se usa |
| Restricción UNIQUE en BD | ❌ No existe `unique_together` |
| Validación en formulario | ✅ Solo a nivel aplicación |

> [!CAUTION]
> Este es el **hallazgo más crítico**. El documento dedica un párrafo completo a explicar cómo se resuelve la concurrencia con transacciones atómicas y restricciones UNIQUE, pero **nada de eso está implementado**.

---

### ✅ Persistencia de datos
**Documento dice:** *"6 tablas: usuarios, canchas, horarios_disponibles, reservas, puntos_historial, log_errores"*

| Tabla documentada | Modelo implementado | Estado |
|---|---|---|
| usuarios | `Usuario` | ✅ |
| canchas | `Cancha` | ✅ |
| horarios_disponibles | `HorarioDisponible` | ✅ |
| reservas | `Reserva` | ✅ |
| puntos_historial | `PuntosHistorial` | ✅ |
| log_errores | `LogErrores` | ✅ |

**Veredicto:** ✅ **100% cumple**

---

### ⚠️ Manejo de errores y excepciones
**Documento dice:** *"Si ocurre un fallo de conexión con la base de datos, el error se registra en la tabla log_errores... El manejo de excepciones se centraliza en la capa de aplicación mediante middleware global"*

| Aspecto | ¿Implementado? |
|---|---|
| Validaciones de formulario | ✅ |
| Mensajes claros al usuario | ✅ (via `django.contrib.messages`) |
| Registro en log_errores | ❌ |
| Middleware global de excepciones | ❌ |
| QR inválido/expirado informado | ✅ |

**Veredicto:** ⚠️ **Parcial** — Mensajes al usuario sí, registro en BD no

---

### ✅ Seguridad del sistema
| Aspecto documentado | ¿Implementado? |
|---|---|
| PBKDF2 para contraseñas | ✅ |
| 3 niveles de roles | ✅ |
| UUID para tokens QR | ✅ |
| Validación fecha/hora/estado del QR | ⚠️ (no verifica hora exacta) |
| Tokens con vigencia limitada | ✅ (por fecha de la reserva) |

**Veredicto:** ✅ **Cumple en lo esencial**

---

## 🔑 Herramientas (Documento vs. Código)

| Herramienta documentada | ¿Usada? | Evidencia |
|---|---|---|
| Python | ✅ | Todo el backend |
| Django (MVT) | ✅ | Framework principal |
| MySQL | ✅ | `ENGINE: django.db.backends.mysql` en [settings.py](file:///c:/Users/DELL/Documents/PROYECTO FINAL/polideportivo/settings.py#L78) |
| ORM de Django | ✅ | Models con QuerySet API |
| PBKDF2 | ✅ | `make_password()` de Django |
| UUID para QR | ✅ | `uuid.uuid4()` |
| Librería qrcode | ✅ | `import qrcode` en views.py (adicional al doc) |

**Veredicto:** ✅ **100% cumple** (incluso tiene más: librería qrcode para generar imágenes)

---

## 🚨 Resumen de Hallazgos Críticos

### ❌ Problemas que DEBEN corregirse

| # | Problema | Severidad | Referencia en documento |
|---|---|---|---|
| 1 | **No hay `transaction.atomic()`** para reservas | 🔴 Alta | Sección "Concurrencia" y RF-04 |
| 2 | **No hay `unique_together`** en Reserva | 🔴 Alta | RNF-03 y sección "Concurrencia" |
| 3 | **LogErrores nunca se usa** en las vistas | 🟡 Media | RNF-08 y sección "Manejo de errores" |
| 4 | **Canje de puntos sin vista** | 🟡 Media | RF-11 |
| 5 | **Puntos se dan al crear, no al asistir** | 🟡 Media | RF-11 dice "por asistencia" |

### ⚠️ Diferencias menores

| # | Diferencia | Severidad |
|---|---|---|
| 6 | Actor "Municipio" no tiene rol propio | 🟢 Baja |
| 7 | Calendario solo diario, no semanal | 🟢 Baja |
| 8 | QR no verifica hora exacta, solo fecha | 🟢 Baja |
| 9 | No hay middleware global de excepciones | 🟢 Baja |
| 10 | Puntos hardcodeados (sin panel de configuración) | 🟢 Baja |

---

## ✅ Veredicto Final

> [!IMPORTANT]
> El sistema tiene un **buen nivel de implementación general (~85-90%)**, con los flujos principales funcionando correctamente. Sin embargo, hay **2 hallazgos críticos** que no coinciden con lo descrito en el documento:
> 
> 1. **Concurrencia**: El documento dedica un párrafo entero a explicar transacciones atómicas y restricciones UNIQUE, pero el código no implementa ninguna de las dos.
> 2. **LogErrores**: El documento dice que "todos los errores se registran", pero el modelo nunca se usa.
> 
> Estos son los puntos que un evaluador notaría como inconsistentes entre el documento escrito y el código entregado.
