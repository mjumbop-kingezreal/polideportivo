from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Canchas y disponibilidad
    path('canchas/', views.lista_canchas_view, name='lista_canchas'),
    path('disponibilidad/', views.disponibilidad_view, name='disponibilidad'),

    # Reservas
    path('reservar/', views.crear_reserva_view, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('cancelar-reserva/<int:reserva_id>/',
         views.cancelar_reserva_view, name='cancelar_reserva'),
    path('qr/<str:codigo_qr>/', views.generar_qr_view, name='generar_qr'),

    # Puntos (P4: canje de puntos)
    path('canjear-puntos/', views.canjear_puntos_view, name='canjear_puntos'),

    # Recepcionista
    path('validar-qr/', views.validar_qr_view, name='validar_qr'),
    path('recepcion/reservar/', views.crear_reserva_recepcion_view, name='crear_reserva_recepcion'),
    path('recepcion/calendario/', views.calendario_reservas_view, name='calendario_reservas'),
    path('recepcion/historial/', views.historial_reservas_view, name='historial_reservas'),
    path('recepcion/marcar-no-asistida/<int:reserva_id>/', views.marcar_no_asistida_view, name='marcar_no_asistida'),

    # Perfil de usuario
    path('perfil/', views.perfil_view, name='perfil'),

    # Administración
    path('admin-usuarios/', views.admin_usuarios_view, name='admin_usuarios'),
    path('admin-canchas/', views.admin_canchas_view, name='admin_canchas'),
    path('admin-horarios/', views.admin_horarios_view, name='admin_horarios'),
    path('admin-puntos/', views.admin_config_puntos_view, name='admin_config_puntos'),
    path('reportes/', views.reportes_view, name='reportes'),

    # Exportación de reportes (PDF/Excel)
    path('reportes/pdf/', views.exportar_pdf_view, name='exportar_pdf'),
    path('reportes/excel/', views.exportar_excel_view, name='exportar_excel'),
]
