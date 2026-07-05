

### Notas del Expositor:
*Buenos días a todos, ingeniero y compañeros. Hoy nuestro equipo va a presentar el proyecto que estuvimos desarrollando este semestre: un Sistema Web de Reservas para un Polideportivo Municipal. Nuestra idea fue automatizar y mejorar la forma en la que la gente interactúa con las instalaciones deportivas de la comunidad.*

---
# 2. Introducción

## ¿Qué es y para qué sirve?

* **El Problema que resuelve:** Elimina el caos de llevar las reservas en papel o en Excel, evitando cruces de horarios y pérdida de información.
* **Por qué se creó:** Para modernizar el polideportivo, brindar un mejor servicio al ciudadano y tener control exacto de quién usa las canchas.
* **A quién está dirigido:** 
  * A los **ciudadanos** (para reservar).
  * A los **recepcionistas** (para controlar el acceso).
  * A la **administración y al municipio** (para gestionar y ver estadísticas).

---

### Notas del Expositor:
*Para empezar, ¿por qué hicimos este sistema? Básicamente, nos dimos cuenta de que la administración de las canchas era muy desordenada. Se usaba papel o Excel, y eso causaba reservas duplicadas y enojos. Así que creamos este sistema dirigido a tres grupos clave: el ciudadano que quiere jugar, el recepcionista que controla la entrada, y la administración que necesita ver qué está pasando y generar reportes.*

---
# 3. Objetivo del Sistema

## ¿Qué queremos lograr?

* **Objetivo General:** 
  Digitalizar y centralizar la gestión de reservas, control de acceso y generación de reportes del polideportivo mediante una plataforma web.

* **Objetivos Específicos:**
  * Permitir a los usuarios reservar canchas desde cualquier lugar.
  * Implementar un control de acceso seguro mediante códigos QR.
  * Crear un programa de puntos para fidelizar a los usuarios.
  * Proveer reportes exportables en Excel y PDF para la toma de decisiones.

---

### Notas del Expositor:
*Nuestro objetivo principal es claro: pasar de lo manual a lo digital. Queremos que todo esté centralizado en una web. Como objetivos más específicos, nos propusimos que la gente pueda reservar desde su casa, que la entrada se controle rápido escaneando un código QR, y que el municipio pueda descargar reportes en PDF y Excel para tomar decisiones reales basadas en datos. Además, agregamos un sistema de puntos para motivar a la gente a hacer deporte.*

---
# 4. Problema Identificado

## El proceso antes del sistema

* **Manejo Manual:** Las reservas se anotaban en cuadernos o planillas sueltas.
* **Dificultades:** 
  * Choque de horarios (dos personas en la misma cancha).
  * Falta de control en la puerta (entraba gente sin reserva).
  * No había forma de saber qué canchas eran las más usadas.
* **¿Qué mejora el sistema?** Automatiza las validaciones para que el error humano desaparezca.

---

### Notas del Expositor:
*Antes de nuestro sistema, imagínense cómo era: alguien llamaba, el encargado lo anotaba en un cuaderno, y a veces se equivocaba de renglón. Cuando llegaban a jugar, había otra persona en la misma cancha. Además, no se sabía cuánta gente realmente usaba las instalaciones al mes. Nuestro sistema viene a arreglar todo esto, porque la computadora no te deja reservar si la cancha ya está ocupada. Elimina el error humano.*

---
# 5. Solución Propuesta

## Nuestra Plataforma Web

* **¿Qué hace?** Es un portal donde cada usuario tiene un perfil, ve qué canchas hay libres y reserva. Luego, va al polideportivo y muestra su QR.
* **Beneficios Principales:**
  * Disponibilidad en tiempo real (24/7).
  * Acceso ágil y seguro (Validación QR).
  * Sistema de recompensas (Vouchers para el bar).
* **¿Por qué es útil?** Ahorra tiempo al personal y mejora la experiencia de los deportistas.

---

### Notas del Expositor:
*Nuestra solución es una página web súper completa. El vecino se crea una cuenta, ve el calendario en tiempo real, elige su horario y listo. Cuando va a la cancha, solo muestra su celular con un código QR, el recepcionista lo escanea y ya está. Es útil porque el vecino no tiene que hacer filas ni llamar por teléfono, y el polideportivo se organiza automáticamente.*

---
# 6. Funcionamiento General

## ¿Cómo fluye la información?

* **Módulos Principales:** Autenticación, Reservas, Recepción (QR), Bar/Puntos, y Administración (Reportes).
* **Flujo del Usuario:**
  1. Inicia sesión.
  2. Revisa el calendario de canchas.
  3. Reserva y recibe un QR.
  4. Asiste, junta puntos y los canjea por snacks.
* **Flujo del Administrador/Recepción:**
  1. Escanea el QR para validar el ingreso.
  2. Gestiona horarios y canchas bloqueadas.
  3. Descarga reportes estadísticos.

---

### Notas del Expositor:
*El sistema tiene un flujo muy lógico. Si sos un usuario normal: entrás, mirás los horarios, hacés clic, reservás, y te da un QR. Vas, jugás, y ganás puntos que podés cambiar por un agua o un snack. Si sos administrador o recepcionista: tu pantalla es distinta. Vos te dedicás a escanear esos QR, ver la agenda del día para saber quién viene, y si sos del municipio, podés descargar los gráficos de cuánta plata se ahorró o cuánta gente hizo deporte este mes.*

---
# 7. Estructura del Proyecto

## ¿Cómo está organizado el trabajo?

* **`polideportivo/`**: Carpeta principal de configuración del sistema web.
* **`reservas/`**: Es el "corazón" de la aplicación. Aquí está toda la lógica.
* **`documentacion/`**: Archivos de investigación, manuales y esta guía.
* **`static/`**: Estilos visuales (CSS) e imágenes (`css/`, `img/`).
* **`templates/`**: Las pantallas que ve el usuario (el diseño en HTML).
* **`manage.py`**: El archivo que hace arrancar el servidor.

---

### Notas del Expositor:
*Para los que les interesa la parte interna, dividimos el proyecto de forma muy ordenada. Tenemos la carpeta "polideportivo" que es el cerebro de la configuración. Luego, la aplicación principal se llama "reservas", ahí adentro vive todo nuestro código. Las pantallas que ve el usuario están en la carpeta "templates", y los colores y fotos en "static". Esta separación hace que el código sea limpio y fácil de mantener si mañana queremos agregar más cosas.*

---
# 8. Implementación Técnica

## Las herramientas que usamos

* **Lenguaje:** Python 3 (Robusto y seguro).
* **Framework Backend:** Django 6 (Arquitectura Modelo-Vista-Template).
* **Base de Datos:** MySQL (Relacional y escalable).
* **Frontend:** HTML5, CSS3, Bootstrap 5 (Diseño Responsive).
* **Librerías Clave:**
  * `qrcode`: Para generar los pases de acceso.
  * `reportlab` & `openpyxl`: Para exportar PDFs y Excels.
* **Arquitectura:** Cliente-Servidor.

---

### Notas del Expositor:
*A nivel técnico, usamos herramientas profesionales. El sistema está hecho en Python usando el framework Django versión 6, que es buenísimo para la seguridad. Para guardar los datos usamos MySQL porque necesitamos que no se caiga si hay muchas personas reservando a la vez. Para que se vea bonito en el celular usamos Bootstrap. Además, tuvimos que investigar e integrar librerías especiales para poder generar los códigos QR y armar los reportes en PDF y Excel.*

---
# 9. Explicación del Código

## ¿Cómo se conecta todo por dentro?

* **Modelos (`models.py`):** Definen la base de datos (Usuario, Cancha, Reserva, Puntos, Productos).
* **Vistas (`views/`):** Tienen la lógica. Reciben el clic del usuario, procesan la info y devuelven una respuesta. Se dividieron en archivos (ej: `reservas_views.py`, `recepcion.py`).
* **URLs (`urls.py`):** Las rutas de la web (ej: `/mis-reservas/`, `/validar-qr/`).
* **Forms (`forms.py`):** Cuidan que los datos ingresados sean válidos y seguros.
* **Templates & Static:** El diseño visual donde se muestran los datos al usuario.

---

### Notas del Expositor:
*El código funciona como un restaurante. Las URLs son el menú; cuando el cliente pide algo (por ejemplo, hacer una reserva), la petición va a las Vistas, que son como el chef. Las Vistas hablan con los Modelos, que son la alacena donde están los datos de MySQL, preparan la respuesta y la entregan usando los Templates, que son el plato servido. Todo esto pasa en milisegundos.*

---
# 10. Funcionalidades Principales

## Lo que el sistema hace por nosotros

1. **Gestión de Reservas:** Previene choques de horarios mediante bloqueos en la base de datos.
2. **Validación QR:** Recepción verifica la entrada rápido, marcando asistencia.
3. **Fidelización por Puntos:** El usuario gana puntos por asistir y los canjea por productos del bar (bebidas, snacks).
4. **Múltiples Roles:** El sistema sabe quién sos y te muestra solo lo que te corresponde (Usuario, Recepción, Admin, Municipio).
5. **Dashboard y Reportes:** Gráficos y descargas para auditorías municipales.

---

### Notas del Expositor:
*Las funciones más fuertes que tenemos son cinco. Primero, las reservas inteligentes que bloquean el horario para que nadie te lo robe. Segundo, el escáner QR que agiliza la entrada. Tercero, nuestro sistema de puntos, que es un plus buenísimo porque incentiva a la gente a no faltar. Cuarto, la seguridad de roles: un vecino no puede entrar a ver los reportes del municipio. Y quinto, el panel de control que genera documentos oficiales con un solo clic.*

---
# 11. Seguridad y Validaciones

## ¿Por qué el sistema es seguro?

* **Contraseñas Encriptadas:** Se usa hash (`pbkdf2_sha256`), ni siquiera nosotros conocemos las claves.
* **Control de Sesiones y Roles:** Decoradores como `@login_requerido` impiden entrar a pantallas privadas copiando el link.
* **Concurrencia de Datos:** Se implementó una tabla especial (`ReservaBloqueo`) con transacciones atómicas para que dos personas no puedan reservar el mismo segundo.
* **Auditoría:** Existe un modelo `LogErrores` que guarda cualquier fallo para su revisión.

---

### Notas del Expositor:
*A nivel de seguridad, nos tomamos las cosas en serio. Las contraseñas viajan y se guardan encriptadas, son imposibles de leer. Si alguien intenta copiar un link de administrador y no tiene los permisos, el sistema lo patea afuera. Y lo más difícil que logramos fue controlar que, si dos personas hacen clic en "Reservar" exactamente al mismo milisegundo, el sistema usa "transacciones atómicas" para bloquear la cancha y darle lugar solo al primero.*

---
# 12. Beneficios del Sistema

## El impacto real

* ⏱️ **Ahorro de tiempo:** Cero llamadas o filas para reservar.
* 📂 **Mejor organización:** Todo centralizado en la nube, nada de papeles perdidos.
* ✅ **Menos errores:** Las reglas del sistema evitan los cruces de horarios.
* 📊 **Mejor control:** Sabemos exactamente quién entró, a qué hora y qué cancha usó.
* 📱 **Facilidad de uso:** Interfaz intuitiva, diseñada para usarse desde el celular.

---

### Notas del Expositor:
*Si me preguntan qué ganamos con esto, les diría: tiempo y paz mental. El personal ya no está todo el día atendiendo el teléfono o peleando porque se cruzó un horario. Los deportistas lo hacen todo desde el celular en un minuto. El municipio gana transparencia, porque ahora saben exactamente cuánta gente usa el polideportivo de verdad.*

---
# 13. Cómo Vender el Sistema

## ¿Por qué invertir en esto?

* **Valor Comercial:** Es un sistema "llave en mano" adaptable a cualquier club deportivo privado o público.
* **¿Quién lo usaría?** Municipios, clubes de barrio, complejos de fútbol sintético, academias de tenis.
* **El Retorno de Inversión:** Se paga solo. Al reducir tiempos muertos y evitar canchas vacías por "ausencias no avisadas", el complejo maximiza su uso y sus ingresos.
* **Diferencia con lo manual:** La información (datos analíticos) hoy en día vale oro para tomar decisiones.

---

### Notas del Expositor:
*Si tuviéramos que vender este proyecto, es un producto altamente comercializable. Se lo podemos vender a la municipalidad, pero también a las canchas de fútbol 5 de la esquina. ¿Por qué lo comprarían? Porque les profesionaliza el negocio. Al tener el sistema de puntos, fidelizan clientes; al tener reservas automáticas, el dueño puede dormir tranquilo sabiendo que su cancha está trabajando y no tiene que estar pegado al teléfono.*

---
# 14. Conclusiones y Mejoras Futuras

## Cierre del Proyecto

* **¿Qué se logró?** Construimos un software funcional, seguro y escalable que soluciona un problema real de la comunidad.
* **¿Qué aprendimos?** A manejar bases de datos complejas, controlar concurrencia de usuarios y estructurar proyectos profesionales.
* **Mejoras Futuras:**
  * Integrar pagos en línea (tarjeta o billeteras virtuales).
  * Enviar notificaciones por WhatsApp.
  * Crear una app nativa para Android y iOS.

---

### Notas del Expositor:
*Para terminar, logramos hacer un sistema de principio a fin que realmente funciona y se puede instalar hoy mismo. Como equipo, aprendimos muchísimo sobre cómo organizar el código y manejar bases de datos de verdad. A futuro, este sistema puede crecer un montón: le podemos agregar pagos con MercadoPago o Stripe, y mandar recordatorios por WhatsApp. Muchas gracias por su atención, si tienen alguna pregunta estamos a su disposición.*
