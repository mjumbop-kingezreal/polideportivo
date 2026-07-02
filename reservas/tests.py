"""
Tests unitarios para el sistema de reservas del polideportivo.

Cubre: autenticación, registro, reservas, QR, puntos, control de acceso y paginación.
"""
from datetime import date, time, timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from .models import (
    Usuario, Cancha, HorarioDisponible,
    Reserva, PuntosHistorial, ConfiguracionPuntos,
)


class BaseTestCase(TestCase):
    """Clase base que crea los datos necesarios para los tests."""

    def setUp(self):
        """Crear datos de prueba reutilizables."""
        # Usuarios
        self.password_raw = 'TestPassword123'
        self.usuario = Usuario.objects.create(
            nombre='Juan Prueba',
            correo='juan@test.com',
            telefono='0991234567',
            password=make_password(self.password_raw),
            rol='usuario',
        )
        self.recepcionista = Usuario.objects.create(
            nombre='María Recepción',
            correo='maria@test.com',
            password=make_password(self.password_raw),
            rol='recepcionista',
        )
        self.admin = Usuario.objects.create(
            nombre='Carlos Admin',
            correo='carlos@test.com',
            password=make_password(self.password_raw),
            rol='administrador',
        )
        self.municipio = Usuario.objects.create(
            nombre='Ana Municipio',
            correo='ana@test.com',
            password=make_password(self.password_raw),
            rol='municipio',
        )
        self.usuario_inactivo = Usuario.objects.create(
            nombre='Pedro Inactivo',
            correo='pedro@test.com',
            password=make_password(self.password_raw),
            rol='usuario',
            estado='inactivo',
        )

        # Cancha
        self.cancha = Cancha.objects.create(
            nombre='Cancha Principal',
            tipo_deporte='futbol',
            ubicacion='Bloque A',
            estado='disponible',
            descripcion='Cancha de fútbol 5',
        )
        self.cancha_mantenimiento = Cancha.objects.create(
            nombre='Cancha B',
            tipo_deporte='baloncesto',
            ubicacion='Bloque B',
            estado='mantenimiento',
        )

        # Horario disponible (día de hoy y mañana)
        hoy_iso = date.today().isoweekday()
        manana_iso = (date.today() + timedelta(days=1)).isoweekday()
        self.horario_hoy = HorarioDisponible.objects.create(
            cancha=self.cancha,
            dia_semana=hoy_iso,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            activo=True,
        )
        self.horario_manana = HorarioDisponible.objects.create(
            cancha=self.cancha,
            dia_semana=manana_iso,
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            activo=True,
        )

        # Configuración de puntos
        ConfiguracionPuntos.objects.get_or_create(
            pk=1,
            defaults={
                'puntos_por_asistencia': 10,
                'minimo_canje': 50,
            }
        )

        # Cliente HTTP
        self.client = Client()

    def login_como(self, usuario):
        """Helper: inicia sesión como un usuario dado."""
        session = self.client.session
        self.client.post(reverse('login'), {
            'correo': usuario.correo,
            'password': self.password_raw,
        })


# ──────────────────────────────────────────────
# Tests de Login
# ──────────────────────────────────────────────

class LoginTests(BaseTestCase):
    """Tests para la vista de inicio de sesión."""

    def test_login_page_loads(self):
        """La página de login carga correctamente."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_valido(self):
        """Login con credenciales válidas redirige correctamente."""
        response = self.client.post(reverse('login'), {
            'correo': self.usuario.correo,
            'password': self.password_raw,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['usuario_id'], self.usuario.id)

    def test_login_password_incorrecto(self):
        """Login con contraseña incorrecta muestra error."""
        response = self.client.post(reverse('login'), {
            'correo': self.usuario.correo,
            'password': 'PasswordIncorrecta',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_correo_no_registrado(self):
        """Login con correo no registrado muestra error."""
        response = self.client.post(reverse('login'), {
            'correo': 'noexiste@test.com',
            'password': self.password_raw,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_cuenta_inactiva(self):
        """Login con cuenta inactiva no permite acceso."""
        response = self.client.post(reverse('login'), {
            'correo': self.usuario_inactivo.correo,
            'password': self.password_raw,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_admin_redirige_a_admin(self):
        """Admin es redirigido al panel de usuarios."""
        response = self.client.post(reverse('login'), {
            'correo': self.admin.correo,
            'password': self.password_raw,
        })
        self.assertRedirects(response, reverse('admin_usuarios'))

    def test_login_recepcionista_redirige_a_qr(self):
        """Recepcionista es redirigido a validar QR."""
        response = self.client.post(reverse('login'), {
            'correo': self.recepcionista.correo,
            'password': self.password_raw,
        })
        self.assertRedirects(response, reverse('validar_qr'))

    def test_login_municipio_redirige_a_reportes(self):
        """Municipio es redirigido a reportes."""
        response = self.client.post(reverse('login'), {
            'correo': self.municipio.correo,
            'password': self.password_raw,
        })
        self.assertRedirects(response, reverse('reportes'))


# ──────────────────────────────────────────────
# Tests de Registro
# ──────────────────────────────────────────────

class RegistroTests(BaseTestCase):
    """Tests para la vista de registro."""

    def test_registro_page_loads(self):
        """La página de registro carga correctamente."""
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_exitoso(self):
        """Registro con datos válidos crea usuario y redirige a login."""
        response = self.client.post(reverse('registro'), {
            'nombre': 'Nuevo Usuario',
            'correo': 'nuevo@test.com',
            'telefono': '0997654321',
            'password': 'NuevaPassword123',
            'confirmar_password': 'NuevaPassword123',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(Usuario.objects.filter(correo='nuevo@test.com').exists())

    def test_registro_passwords_no_coinciden(self):
        """Registro con contraseñas distintas muestra error."""
        response = self.client.post(reverse('registro'), {
            'nombre': 'Test',
            'correo': 'test_fail@test.com',
            'password': 'Password123',
            'confirmar_password': 'OtraPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(correo='test_fail@test.com').exists())

    def test_registro_correo_duplicado(self):
        """Registro con correo ya existente muestra error."""
        response = self.client.post(reverse('registro'), {
            'nombre': 'Duplicado',
            'correo': self.usuario.correo,  # Ya existe
            'password': 'Password123',
            'confirmar_password': 'Password123',
        })
        self.assertEqual(response.status_code, 200)

    def test_registro_password_muy_corta(self):
        """Registro con contraseña menor a 8 chars muestra error."""
        response = self.client.post(reverse('registro'), {
            'nombre': 'Corto',
            'correo': 'corto@test.com',
            'password': 'abc',
            'confirmar_password': 'abc',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(correo='corto@test.com').exists())


# ──────────────────────────────────────────────
# Tests de Reservas
# ──────────────────────────────────────────────

class ReservaTests(BaseTestCase):
    """Tests para creación y cancelación de reservas."""

    def test_crear_reserva_sin_login_redirige(self):
        """Intentar crear reserva sin sesión redirige a login."""
        response = self.client.get(reverse('crear_reserva'))
        self.assertRedirects(response, reverse('login'))

    def test_crear_reserva_exitosa(self):
        """Crear reserva válida funciona y redirige a mis reservas."""
        self.login_como(self.usuario)
        fecha_manana = date.today() + timedelta(days=1)
        response = self.client.post(reverse('crear_reserva'), {
            'cancha': self.cancha.id,
            'fecha': fecha_manana.isoformat(),
            'hora_inicio': '14:00',
            'hora_fin': '15:00',
            'lista_invitados': 'Pedro, Luis, Ana',
            'observacion': 'Traer balón',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Reserva.objects.filter(
                usuario=self.usuario,
                cancha=self.cancha,
                fecha=fecha_manana,
            ).exists()
        )

    def test_crear_reserva_duplicada_falla(self):
        """No se puede crear reserva en franja ya ocupada."""
        self.login_como(self.usuario)
        fecha_manana = date.today() + timedelta(days=1)

        # Crear primera reserva
        Reserva.objects.create(
            usuario=self.usuario,
            cancha=self.cancha,
            fecha=fecha_manana,
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            estado='confirmada',
            codigo_qr='test-qr-unique-1',
            lista_invitados='Juan',
        )

        # Intentar crear duplicada
        response = self.client.post(reverse('crear_reserva'), {
            'cancha': self.cancha.id,
            'fecha': fecha_manana.isoformat(),
            'hora_inicio': '14:00',
            'hora_fin': '15:00',
            'lista_invitados': 'Otro grupo',
        })
        # Debería mostrar error (no crear segunda reserva)
        count = Reserva.objects.filter(
            cancha=self.cancha,
            fecha=fecha_manana,
            hora_inicio=time(14, 0),
            estado='confirmada',
        ).count()
        self.assertEqual(count, 1)

    def test_cancelar_reserva(self):
        """Cancelar reserva confirmada la marca como cancelada."""
        self.login_como(self.usuario)
        fecha_manana = date.today() + timedelta(days=1)
        reserva = Reserva.objects.create(
            usuario=self.usuario,
            cancha=self.cancha,
            fecha=fecha_manana,
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            estado='confirmada',
            codigo_qr='test-cancel-qr',
            lista_invitados='Test',
        )
        response = self.client.get(reverse('cancelar_reserva', args=[reserva.id]))
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')

    def test_cancelar_reserva_ajena_falla(self):
        """No se puede cancelar la reserva de otro usuario."""
        self.login_como(self.usuario)
        fecha_manana = date.today() + timedelta(days=1)
        reserva_ajena = Reserva.objects.create(
            usuario=self.recepcionista,
            cancha=self.cancha,
            fecha=fecha_manana,
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            estado='confirmada',
            codigo_qr='test-ajena-qr',
            lista_invitados='Test',
        )
        response = self.client.get(reverse('cancelar_reserva', args=[reserva_ajena.id]))
        self.assertEqual(response.status_code, 404)

    def test_mis_reservas_solo_propias(self):
        """Un usuario solo ve sus propias reservas."""
        self.login_como(self.usuario)
        # Crear reserva propia
        Reserva.objects.create(
            usuario=self.usuario,
            cancha=self.cancha,
            fecha=date.today() + timedelta(days=1),
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            estado='confirmada',
            codigo_qr='test-mis-1',
            lista_invitados='Test',
        )
        # Crear reserva ajena
        Reserva.objects.create(
            usuario=self.recepcionista,
            cancha=self.cancha,
            fecha=date.today() + timedelta(days=2),
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            estado='confirmada',
            codigo_qr='test-mis-2',
            lista_invitados='Test',
        )
        response = self.client.get(reverse('mis_reservas'))
        self.assertEqual(response.status_code, 200)
        # Solo debe ver 1 reserva (la propia)
        reservas_en_pagina = response.context['reservas']
        ids = [r.usuario_id for r in reservas_en_pagina]
        self.assertTrue(all(uid == self.usuario.id for uid in ids))


# ──────────────────────────────────────────────
# Tests de QR y Puntos
# ──────────────────────────────────────────────

class QRPuntosTests(BaseTestCase):
    """Tests para validación de QR y sistema de puntos."""

    def setUp(self):
        super().setUp()
        self.reserva = Reserva.objects.create(
            usuario=self.usuario,
            cancha=self.cancha,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            estado='confirmada',
            codigo_qr='qr-test-001',
            lista_invitados='Pedro',
        )

    def test_validar_qr_exitoso(self):
        """Validar QR marca como asistida y otorga puntos."""
        self.login_como(self.recepcionista)
        puntos_antes = self.usuario.puntos_acumulados

        response = self.client.post(reverse('validar_qr'), {
            'codigo_qr': 'qr-test-001',
        })
        self.assertEqual(response.status_code, 200)

        # Reserva marcada como asistida
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'asistida')

        # Puntos otorgados
        self.usuario.refresh_from_db()
        config = ConfiguracionPuntos.obtener()
        self.assertEqual(
            self.usuario.puntos_acumulados,
            puntos_antes + config.puntos_por_asistencia
        )

        # Historial de puntos creado
        self.assertTrue(
            PuntosHistorial.objects.filter(
                usuario=self.usuario,
                reserva=self.reserva,
                tipo_movimiento='otorgado',
            ).exists()
        )

    def test_validar_qr_inexistente(self):
        """Validar QR inexistente muestra error."""
        self.login_como(self.recepcionista)
        response = self.client.post(reverse('validar_qr'), {
            'codigo_qr': 'qr-no-existe',
        })
        self.assertEqual(response.status_code, 200)
        resultado = response.context['resultado']
        self.assertFalse(resultado['valido'])

    def test_validar_qr_ya_asistida(self):
        """No se puede validar una reserva ya asistida."""
        self.login_como(self.recepcionista)
        self.reserva.estado = 'asistida'
        self.reserva.save()

        response = self.client.post(reverse('validar_qr'), {
            'codigo_qr': 'qr-test-001',
        })
        resultado = response.context['resultado']
        self.assertFalse(resultado['valido'])

    def test_usuario_no_puede_validar_qr(self):
        """Un usuario normal no puede acceder a validar QR."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('validar_qr'))
        self.assertEqual(response.status_code, 403)


# ──────────────────────────────────────────────
# Tests de Puntos (Canje)
# ──────────────────────────────────────────────

class CanjePuntosTests(BaseTestCase):
    """Tests para el canje de puntos."""

    def test_canjear_puntos_exitoso(self):
        """Canje exitoso descuenta puntos y crea historial."""
        self.usuario.puntos_acumulados = 100
        self.usuario.save()
        self.login_como(self.usuario)

        response = self.client.post(reverse('canjear_puntos'), {
            'puntos_a_canjear': 50,
        })
        self.assertEqual(response.status_code, 302)

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.puntos_acumulados, 50)

        # Historial creado
        self.assertTrue(
            PuntosHistorial.objects.filter(
                usuario=self.usuario,
                tipo_movimiento='canjeado',
                puntos=50,
            ).exists()
        )

    def test_canjear_puntos_insuficientes(self):
        """No se puede canjear más puntos de los que se tienen."""
        self.usuario.puntos_acumulados = 20
        self.usuario.save()
        self.login_como(self.usuario)

        response = self.client.post(reverse('canjear_puntos'), {
            'puntos_a_canjear': 50,
        })
        self.assertEqual(response.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.puntos_acumulados, 20)  # Sin cambio

    def test_canjear_puntos_menor_al_minimo(self):
        """No se puede canjear menos del mínimo configurado."""
        self.usuario.puntos_acumulados = 100
        self.usuario.save()
        config = ConfiguracionPuntos.obtener()
        self.login_como(self.usuario)

        response = self.client.post(reverse('canjear_puntos'), {
            'puntos_a_canjear': config.minimo_canje - 1,
        })
        # Debería quedar igual
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.puntos_acumulados, 100)


# ──────────────────────────────────────────────
# Tests de Control de Acceso
# ──────────────────────────────────────────────

class AccesoTests(BaseTestCase):
    """Tests para el control de acceso basado en roles."""

    def test_usuario_no_puede_acceder_admin_usuarios(self):
        """Usuario normal recibe 403 en admin de usuarios."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('admin_usuarios'))
        self.assertEqual(response.status_code, 403)

    def test_usuario_no_puede_acceder_admin_canchas(self):
        """Usuario normal recibe 403 en admin de canchas."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('admin_canchas'))
        self.assertEqual(response.status_code, 403)

    def test_usuario_no_puede_acceder_reportes(self):
        """Usuario normal recibe 403 en reportes."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 403)

    def test_recepcionista_no_puede_acceder_admin(self):
        """Recepcionista recibe 403 en admin de usuarios."""
        self.login_como(self.recepcionista)
        response = self.client.get(reverse('admin_usuarios'))
        self.assertEqual(response.status_code, 403)

    def test_admin_puede_acceder_admin(self):
        """Administrador puede acceder al panel de admin."""
        self.login_como(self.admin)
        response = self.client.get(reverse('admin_usuarios'))
        self.assertEqual(response.status_code, 200)

    def test_admin_puede_acceder_reportes(self):
        """Administrador puede acceder a reportes."""
        self.login_como(self.admin)
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 200)

    def test_municipio_puede_acceder_reportes(self):
        """Municipio puede acceder a reportes."""
        self.login_como(self.municipio)
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 200)

    def test_recepcionista_puede_acceder_calendario(self):
        """Recepcionista puede acceder al calendario."""
        self.login_como(self.recepcionista)
        response = self.client.get(reverse('calendario_reservas'))
        self.assertEqual(response.status_code, 200)

    def test_sin_login_redirige_a_login(self):
        """Sin sesión activa, todas las vistas protegidas redirigen a login."""
        urls_protegidas = [
            'lista_canchas', 'disponibilidad', 'crear_reserva',
            'mis_reservas', 'perfil', 'canjear_puntos',
        ]
        for url_name in urls_protegidas:
            response = self.client.get(reverse(url_name))
            self.assertRedirects(
                response, reverse('login'),
                msg_prefix=f'Falla en {url_name}'
            )

    def test_logout(self):
        """Logout limpia la sesión y redirige a login."""
        self.login_como(self.usuario)
        self.assertIn('usuario_id', self.client.session)

        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)


# ──────────────────────────────────────────────
# Tests de Canchas y Disponibilidad
# ──────────────────────────────────────────────

class CanchasTests(BaseTestCase):
    """Tests para las vistas de canchas y disponibilidad."""

    def test_lista_canchas(self):
        """Lista de canchas carga y muestra las canchas."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('lista_canchas'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('canchas', response.context)

    def test_filtrar_canchas_por_tipo(self):
        """Filtrar canchas por tipo de deporte funciona."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('lista_canchas'), {'tipo': 'futbol'})
        self.assertEqual(response.status_code, 200)
        for cancha in response.context['canchas']:
            self.assertEqual(cancha.tipo_deporte, 'futbol')

    def test_disponibilidad_con_cancha_y_fecha(self):
        """Consulta de disponibilidad con cancha y fecha muestra horarios."""
        self.login_como(self.usuario)
        fecha_manana = (date.today() + timedelta(days=1)).isoformat()
        response = self.client.get(reverse('disponibilidad'), {
            'cancha': self.cancha.id,
            'fecha': fecha_manana,
        })
        self.assertEqual(response.status_code, 200)


# ──────────────────────────────────────────────
# Tests de Exportación
# ──────────────────────────────────────────────

class ExportacionTests(BaseTestCase):
    """Tests para la exportación de reportes a PDF y Excel."""

    def test_exportar_pdf_como_admin(self):
        """Admin puede exportar reportes a PDF."""
        self.login_como(self.admin)
        response = self.client.get(reverse('exportar_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_exportar_excel_como_admin(self):
        """Admin puede exportar reportes a Excel."""
        self.login_como(self.admin)
        response = self.client.get(reverse('exportar_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])

    def test_usuario_no_puede_exportar_pdf(self):
        """Usuario normal no puede exportar PDF."""
        self.login_como(self.usuario)
        response = self.client.get(reverse('exportar_pdf'))
        self.assertEqual(response.status_code, 403)

    def test_municipio_puede_exportar(self):
        """Municipio puede exportar reportes."""
        self.login_como(self.municipio)
        response = self.client.get(reverse('exportar_pdf'))
        self.assertEqual(response.status_code, 200)
