# Código de Templates (HTML)

## admin_canchas.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Gestión de Canchas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Gestión de Canchas</h1>

<div class="card">
    <h3>{% if cancha_editar %}Editar Cancha{% else %}Nueva Cancha{% endif %}</h3>

    <form method="post">
        {% csrf_token %}
        {% if cancha_editar %}
            <input type="hidden" name="cancha_id" value="{{ cancha_editar.id }}">
        {% endif %}

        {% for field in form.visible_fields %}
            <div class="form-group">
                <label>{{ field.label }}</label>
                {{ field }}
            </div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">Guardar</button>
        {% if cancha_editar %}
            <a href="{% url 'admin_canchas' %}" class="btn btn-outline">Cancelar Edición</a>
        {% endif %}
    </form>
</div>

<div class="card">
    <h3>Canchas Registradas</h3>
    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Deporte</th>
                <th>Ubicación</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for c in canchas %}
            <tr>
                <td>{{ c.nombre }}</td>
                <td>{{ c.get_tipo_deporte_display }}</td>
                <td>{{ c.ubicacion }}</td>
                <td><span class="badge badge-{{ c.estado }}">{{ c.get_estado_display }}</span></td>
                <td>
                    <a href="?editar={{ c.id }}" class="btn btn-outline">Editar</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## admin_config_puntos.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Configuración de Puntos{% endblock %}

{% block contenido %}
<h1 class="page-title">Configuración de Puntos</h1>

<div class="card">
    <h2>Editar Reglas de Puntos</h2>

    {% if form.non_field_errors %}
        {% for error in form.non_field_errors %}
            <div class="alert" style="background: rgba(231,76,60,0.15); border-left: 4px solid #e74c3c; color: #e74c3c;">
                {{ error }}
            </div>
        {% endfor %}
    {% endif %}

    {% if form.errors %}
        <div class="alert" style="background: rgba(231,76,60,0.15); border-left: 4px solid #e74c3c; color: #e74c3c;">
            Por favor corrige los errores indicados.
        </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        {% for field in form.visible_fields %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                {% if field.errors %}
                    {% for error in field.errors %}
                        <small style="color: #e74c3c;">{{ error }}</small>
                    {% endfor %}
                {% endif %}
                {% if field.help_text %}
                    <small style="color: rgba(255,255,255,0.5);">{{ field.help_text }}</small>
                {% endif %}
            </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary">Guardar Configuración</button>
    </form>
</div>

{% if config %}
<div class="card" style="margin-top: 2rem;">
    <h2>Configuración Actual</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{{ config.puntos_por_asistencia }}</div>
            <div class="stat-label">Puntos por Asistencia</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ config.minimo_canje }}</div>
            <div class="stat-label">Mínimo para Canje</div>
        </div>
    </div>
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
        <strong style="color: rgba(255,255,255,0.7);">Beneficio del Canje:</strong>
        <p style="margin-top: 0.5rem;">{{ config.descripcion_beneficio }}</p>
    </div>
</div>
{% endif %}
{% endblock %}
`

## admin_horarios.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Gestión de Horarios - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Gestión de Horarios</h1>

<div class="card">
    <h3>{% if horario_editar %}Editar Horario{% else %}Nuevo Horario{% endif %}</h3>

    <form method="post">
        {% csrf_token %}
        {% if horario_editar %}
            <input type="hidden" name="horario_id" value="{{ horario_editar.id }}">
        {% endif %}

        {% for field in form.visible_fields %}
            <div class="form-group">
                <label>{{ field.label }}</label>
                {{ field }}
            </div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">Guardar</button>
        {% if horario_editar %}
            <a href="{% url 'admin_horarios' %}" class="btn btn-outline">Cancelar</a>
        {% endif %}
    </form>
</div>

<div class="card">
    <h3>Horarios Registrados</h3>
    <table>
        <thead>
            <tr>
                <th>Cancha</th>
                <th>Día</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Activo</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for h in horarios %}
            <tr>
                <td>{{ h.cancha.nombre }}</td>
                <td>{{ h.get_dia_semana_display }}</td>
                <td>{{ h.hora_inicio }}</td>
                <td>{{ h.hora_fin }}</td>
                <td>{% if h.activo %}✅{% else %}❌{% endif %}</td>
                <td>
                    <a href="?editar={{ h.id }}" class="btn btn-outline">Editar</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## admin_usuarios.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Gestión de Usuarios - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Gestión de Usuarios</h1>

<div class="card" style="padding: 1.5rem;">
    <table class="table">
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Teléfono</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for u in usuarios %}
            <tr>
                <td>{{ u.nombre }}</td>
                <td>{{ u.correo }}</td>
                <td>{{ u.telefono|default:"-" }}</td>
                <td>
                    <form method="post" style="display:inline-flex; gap:0.5rem;">
                        {% csrf_token %}
                        <input type="hidden" name="accion" value="cambiar_rol">
                        <input type="hidden" name="usuario_id" value="{{ u.id }}">
                        <select name="rol" class="form-control" style="width: auto; padding: 0.2rem;" onchange="this.form.submit()" {% if u.id == request.usuario.id %}disabled{% endif %}>
                            <option value="usuario" {% if u.rol == 'usuario' %}selected{% endif %}>Usuario</option>
                            <option value="recepcionista" {% if u.rol == 'recepcionista' %}selected{% endif %}>Recepcionista</option>
                            <option value="administrador" {% if u.rol == 'administrador' %}selected{% endif %}>Admin</option>
                        </select>
                    </form>
                </td>
                <td><span class="badge badge-{{ u.estado }}">{{ u.get_estado_display }}</span></td>
                <td>
                    <form method="post" style="display:inline;">
                        {% csrf_token %}
                        <input type="hidden" name="accion" value="toggle_estado">
                        <input type="hidden" name="usuario_id" value="{{ u.id }}">
                        {% if u.id == request.usuario.id %}
                            <button type="button" class="btn btn-outline" disabled>Tú</button>
                        {% else %}
                            <button type="submit" class="btn btn-primary" onclick="return confirm('¿Cambiar estado de este usuario?');">
                                {% if u.estado == 'activo' %}Desactivar{% else %}Activar{% endif %}
                            </button>
                        {% endif %}
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## base.html

`html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titulo %}Polideportivo{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
        }

        /* ─── Navegación ─── */
        .navbar {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-brand {
            font-size: 1.4rem;
            font-weight: 700;
            color: #7c4dff;
            text-decoration: none;
        }

        .navbar-links { display: flex; gap: 1rem; align-items: center; }

        .navbar-links a {
            color: #b0b0b0;
            text-decoration: none;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            transition: all 0.3s;
            font-size: 0.9rem;
        }

        .navbar-links a:hover {
            color: #fff;
            background: rgba(124,77,255,0.2);
        }

        .navbar-links a.active {
            color: #7c4dff;
            background: rgba(124,77,255,0.15);
        }

        .navbar-user {
            color: #aaa;
            font-size: 0.85rem;
        }

        /* ─── Contenido ─── */
        .container {
            max-width: 1100px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }

        .page-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: #fff;
        }

        /* ─── Cards ─── */
        .card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(8px);
        }

        .card h3 {
            color: #b388ff;
            margin-bottom: 0.8rem;
        }

        /* ─── Formularios ─── */
        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.3rem;
            color: #ccc;
            font-size: 0.9rem;
        }

        .form-control {
            width: 100%;
            padding: 0.6rem 0.8rem;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 8px;
            color: #fff;
            font-size: 0.95rem;
            transition: border 0.3s;
        }

        .form-control:focus {
            outline: none;
            border-color: #7c4dff;
            box-shadow: 0 0 0 3px rgba(124,77,255,0.2);
        }

        select.form-control { cursor: pointer; }
        select.form-control option { background: #24243e; color: #fff; }

        .form-check-input { width: 18px; height: 18px; cursor: pointer; }

        /* ─── Botones ─── */
        .btn {
            display: inline-block;
            padding: 0.55rem 1.2rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-primary {
            background: linear-gradient(135deg, #7c4dff, #536dfe);
            color: #fff;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(124,77,255,0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #ff5252, #ff1744);
            color: #fff;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,23,68,0.4);
        }

        .btn-success {
            background: linear-gradient(135deg, #69f0ae, #00e676);
            color: #1a1a2e;
        }

        .btn-outline {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.2);
            color: #ccc;
        }

        .btn-outline:hover {
            background: rgba(255,255,255,0.08);
            color: #fff;
        }

        /* ─── Tablas ─── */
        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 0.7rem 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        th {
            color: #b388ff;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }

        tr:hover { background: rgba(255,255,255,0.04); }

        /* ─── Alertas / Mensajes ─── */
        .alert {
            padding: 0.8rem 1.2rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }

        .alert-success {
            background: rgba(105,240,174,0.15);
            border: 1px solid rgba(105,240,174,0.3);
            color: #69f0ae;
        }

        .alert-error {
            background: rgba(255,82,82,0.15);
            border: 1px solid rgba(255,82,82,0.3);
            color: #ff5252;
        }

        .alert-warning {
            background: rgba(255,234,0,0.1);
            border: 1px solid rgba(255,234,0,0.3);
            color: #ffea00;
        }

        .alert-info {
            background: rgba(64,196,255,0.1);
            border: 1px solid rgba(64,196,255,0.3);
            color: #40c4ff;
        }

        /* ─── Badges ─── */
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-confirmada { background: rgba(105,240,174,0.2); color: #69f0ae; }
        .badge-cancelada { background: rgba(255,82,82,0.2); color: #ff5252; }
        .badge-no_asistida { background: rgba(255,234,0,0.2); color: #ffea00; }
        .badge-asistida { background: rgba(64,196,255,0.2); color: #40c4ff; }
        .badge-disponible { background: rgba(105,240,174,0.2); color: #69f0ae; }
        .badge-mantenimiento { background: rgba(255,234,0,0.2); color: #ffea00; }
        .badge-fuera_servicio { background: rgba(255,82,82,0.2); color: #ff5252; }

        /* ─── Stats ─── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
        }

        .stat-card .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #7c4dff;
        }

        .stat-card .stat-label {
            color: #aaa;
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }

        /* ─── Filtros ─── */
        .filters {
            display: flex;
            gap: 1rem;
            align-items: end;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }

        .filters .form-group { margin-bottom: 0; min-width: 180px; }

        /* ─── Grid de canchas ─── */
        .canchas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.2rem;
        }

        /* ─── QR resultado ─── */
        .qr-resultado {
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-top: 1rem;
        }

        .qr-valido {
            background: rgba(105,240,174,0.1);
            border: 2px solid rgba(105,240,174,0.3);
        }

        .qr-invalido {
            background: rgba(255,82,82,0.1);
            border: 2px solid rgba(255,82,82,0.3);
        }

        /* ─── Login box ─── */
        .auth-container {
            max-width: 420px;
            margin: 5rem auto;
        }

        .auth-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 2.5rem;
            backdrop-filter: blur(12px);
        }

        .auth-card h2 {
            text-align: center;
            color: #fff;
            margin-bottom: 1.5rem;
            font-size: 1.6rem;
        }

        .auth-footer {
            text-align: center;
            margin-top: 1.2rem;
            color: #888;
            font-size: 0.9rem;
        }

        .auth-footer a { color: #7c4dff; text-decoration: none; }
        .auth-footer a:hover { text-decoration: underline; }

        /* ─── Responsive ─── */
        @media (max-width: 768px) {
            .navbar { flex-direction: column; gap: 0.5rem; }
            .filters { flex-direction: column; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    {% if usuario %}
    <nav class="navbar">
        <a href="{% url 'lista_canchas' %}" class="navbar-brand">🏟️ Polideportivo</a>
        <div class="navbar-links">
            <a href="{% url 'lista_canchas' %}">Canchas</a>
            <a href="{% url 'disponibilidad' %}">Disponibilidad</a>
            <a href="{% url 'crear_reserva' %}">Reservar</a>
            <a href="{% url 'mis_reservas' %}">Mis Reservas</a>
            <a href="{% url 'canjear_puntos' %}">Canjear Puntos</a>

            {% if usuario.rol == 'recepcionista' or usuario.rol == 'administrador' %}
                <a href="{% url 'validar_qr' %}">Validar QR</a>
                <a href="{% url 'calendario_reservas' %}">Calendario</a>
                <a href="{% url 'historial_reservas' %}">Historial</a>
                <a href="{% url 'crear_reserva_recepcion' %}">Reserva Recepción</a>
            {% endif %}

            {% if usuario.rol == 'administrador' %}
                <a href="{% url 'admin_usuarios' %}">Usuarios</a>
                <a href="{% url 'admin_canchas' %}">Admin Canchas</a>
                <a href="{% url 'admin_horarios' %}">Admin Horarios</a>
                <a href="{% url 'admin_config_puntos' %}">Config Puntos</a>
                <a href="{% url 'reportes' %}">Reportes</a>
            {% endif %}

            {% if usuario.rol == 'municipio' %}
                <a href="{% url 'reportes' %}">Reportes</a>
                <a href="{% url 'admin_config_puntos' %}">Config Puntos</a>
            {% endif %}

            <a href="{% url 'perfil' %}">Perfil</a>
            <span class="navbar-user">{{ usuario.nombre }} ({{ usuario.get_rol_display }})</span>
            <a href="{% url 'logout' %}">Salir</a>
        </div>
    </nav>
    {% endif %}

    <div class="container">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}

        {% block contenido %}{% endblock %}
    </div>
</body>
</html>
`

## calendario.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Calendario de Reservas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Calendario de Reservas</h1>

<form method="get" class="filters">
    <div class="form-group">
        <label>Fecha</label>
        <input type="date" name="fecha" class="form-control" value="{{ fecha_str }}">
    </div>
    <div class="form-group">
        <label>Vista</label>
        <select name="vista" class="form-control">
            <option value="diaria" {% if vista == 'diaria' %}selected{% endif %}>Diaria</option>
            <option value="semanal" {% if vista == 'semanal' %}selected{% endif %}>Semanal</option>
        </select>
    </div>
    <button type="submit" class="btn btn-outline">Filtrar</button>
</form>

{% if vista == 'semanal' %}
<!-- ─── Vista Semanal ─── -->
<div class="card" style="padding: 1.5rem;">
    <h3 style="margin-bottom: 1rem;">Semana: {{ lunes|date:"d/m" }} — {{ domingo|date:"d/m/Y" }}</h3>
    {% for dia in dias_semana %}
    <div style="margin-bottom: 1.5rem;">
        <h4 style="color: #b388ff; margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.3rem;">
            {{ dia|date:"l d/m/Y" }}
        </h4>
        <table class="table">
            <thead>
                <tr>
                    <th>Hora</th>
                    <th>Cancha</th>
                    <th>Cliente</th>
                    <th>Estado</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
                {% for r in reservas %}
                    {% if r.fecha == dia %}
                    <tr>
                        <td>{{ r.hora_inicio|time:"H:i" }} - {{ r.hora_fin|time:"H:i" }}</td>
                        <td>{{ r.cancha.nombre }} ({{ r.cancha.get_tipo_deporte_display }})</td>
                        <td>{{ r.usuario.nombre }}</td>
                        <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
                        <td>
                            {% if r.estado == 'confirmada' %}
                                <a href="{% url 'marcar_no_asistida' r.id %}" class="btn btn-outline" style="color: red; padding: 0.3rem 0.5rem;" onclick="return confirm('¿Marcar como inasistencia?');">Falta</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endif %}
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endfor %}
</div>

{% else %}
<!-- ─── Vista Diaria ─── -->
<div class="card" style="padding: 1.5rem;">
    <table class="table">
        <thead>
            <tr>
                <th>Hora</th>
                <th>Cancha</th>
                <th>Cliente</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for r in reservas %}
            <tr>
                <td>{{ r.hora_inicio|time:"H:i" }} - {{ r.hora_fin|time:"H:i" }}</td>
                <td>{{ r.cancha.nombre }} ({{ r.cancha.get_tipo_deporte_display }})</td>
                <td>{{ r.usuario.nombre }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
                <td>
                    {% if r.estado == 'confirmada' %}
                        <a href="{% url 'marcar_no_asistida' r.id %}" class="btn btn-outline" style="color: red; padding: 0.3rem 0.5rem;" onclick="return confirm('¿Marcar como inasistencia?');">Falta</a>
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" style="text-align:center; padding: 2rem;">No hay reservas registradas para esta fecha.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}
{% endblock %}
`

## canjear_puntos.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Canjear Puntos{% endblock %}

{% block contenido %}
<h1 class="page-title">Canjear Puntos</h1>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">{{ usuario.puntos_acumulados }}</div>
        <div class="stat-label">Puntos Disponibles</div>
    </div>
</div>

<div class="card" style="margin-top: 2rem;">
    <h2>Canjear mis puntos</h2>

    {% if form.non_field_errors %}
        {% for error in form.non_field_errors %}
            <div class="alert" style="background: rgba(231,76,60,0.15); border-left: 4px solid #e74c3c; color: #e74c3c;">
                {{ error }}
            </div>
        {% endfor %}
    {% endif %}

    {% if form.errors %}
        <div class="alert" style="background: rgba(231,76,60,0.15); border-left: 4px solid #e74c3c; color: #e74c3c;">
            Por favor corrige los errores indicados.
        </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        {% for field in form.visible_fields %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                {{ field }}
                {% if field.errors %}
                    {% for error in field.errors %}
                        <small style="color: #e74c3c;">{{ error }}</small>
                    {% endfor %}
                {% endif %}
                {% if field.help_text %}
                    <small style="color: rgba(255,255,255,0.5);">{{ field.help_text }}</small>
                {% endif %}
            </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary">Canjear Puntos</button>
    </form>
</div>

{% if historial %}
<div class="card" style="margin-top: 2rem;">
    <h2>Historial de Puntos Reciente</h2>
    <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <th style="padding: 0.75rem; text-align: left; color: rgba(255,255,255,0.7);">Fecha</th>
                    <th style="padding: 0.75rem; text-align: left; color: rgba(255,255,255,0.7);">Tipo</th>
                    <th style="padding: 0.75rem; text-align: center; color: rgba(255,255,255,0.7);">Puntos</th>
                    <th style="padding: 0.75rem; text-align: left; color: rgba(255,255,255,0.7);">Descripción</th>
                </tr>
            </thead>
            <tbody>
                {% for item in historial %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 0.75rem;">{{ item.fecha|date:"d/m/Y H:i" }}</td>
                    <td style="padding: 0.75rem;">
                        <span class="badge">{{ item.get_tipo_movimiento_display }}</span>
                    </td>
                    <td style="padding: 0.75rem; text-align: center; font-weight: 600;">
                        {% if item.puntos > 0 %}
                            <span style="color: #2ecc71;">+{{ item.puntos }}</span>
                        {% else %}
                            <span style="color: #e74c3c;">{{ item.puntos }}</span>
                        {% endif %}
                    </td>
                    <td style="padding: 0.75rem; color: rgba(255,255,255,0.7);">{{ item.descripcion }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}

<div style="margin-top: 2rem; text-align: center;">
    <a href="{% url 'perfil' %}" class="btn btn-outline">← Volver al Perfil</a>
</div>
{% endblock %}
`

## crear_reserva.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Crear Reserva - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Nueva Reserva</h1>

<div class="card" style="max-width: 600px;">
    {% if form.errors %}
        <div class="alert alert-error">
            {% for error in form.non_field_errors %}
                <div>{{ error }}</div>
            {% endfor %}
        </div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <div class="form-group">
            <label>Cancha</label>
            {{ form.cancha }}
        </div>
        <div class="form-group">
            <label>Fecha</label>
            {{ form.fecha }}
        </div>
        <div class="form-group">
            <label>Hora Inicio</label>
            {{ form.hora_inicio }}
        </div>
        <div class="form-group">
            <label>Hora Fin</label>
            {{ form.hora_fin }}
        </div>
        <div class="form-group">
            <label>Observación</label>
            {{ form.observacion }}
        </div>
        <button type="submit" class="btn btn-primary">Confirmar Reserva</button>
        <a href="{% url 'disponibilidad' %}" class="btn btn-outline">Cancelar</a>
    </form>
</div>
{% endblock %}
`

## crear_reserva_recepcion.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Nueva Reserva (Recepción) - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Nueva Reserva (Recepción)</h1>

<div class="card" style="max-width: 600px; margin: 0 auto; padding: 2rem;">
    {% if form.errors %}
        <div class="alert alert-error">Por favor, corrige los errores del formulario.</div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <div class="form-group">
            <label>Usuario (Cliente)</label>
            {{ form.usuario }}
        </div>
        <div class="form-group">
            <label>Cancha</label>
            {{ form.cancha }}
        </div>
        <div class="form-group">
            <label>Fecha</label>
            {{ form.fecha }}
        </div>
        <div style="display:flex; gap:1rem;">
            <div class="form-group" style="flex:1;">
                <label>Hora Inicio</label>
                {{ form.hora_inicio }}
            </div>
            <div class="form-group" style="flex:1;">
                <label>Hora Fin</label>
                {{ form.hora_fin }}
            </div>
        </div>
        <div class="form-group">
            <label>Lista de Invitados</label>
            {{ form.lista_invitados }}
        </div>
        <div class="form-group">
            <label>Observaciones</label>
            {{ form.observacion }}
        </div>
        
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Confirmar Reserva</button>
    </form>
</div>
{% endblock %}
`

## disponibilidad.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Disponibilidad - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Consultar Disponibilidad</h1>

<div class="card">
    <form method="get" class="filters">
        <div class="form-group">
            <label>Cancha</label>
            <select name="cancha" class="form-control">
                <option value="">Seleccionar...</option>
                {% for c in canchas %}
                    <option value="{{ c.id }}" {% if cancha_sel and cancha_sel.id == c.id %}selected{% endif %}>
                        {{ c.nombre }} ({{ c.get_tipo_deporte_display }})
                    </option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label>Fecha</label>
            <input type="date" name="fecha" class="form-control" value="{{ fecha }}">
        </div>
        <button type="submit" class="btn btn-primary">Buscar</button>
    </form>
</div>

{% if cancha_sel and horarios %}
<div class="card">
    <h3>Horarios de {{ cancha_sel.nombre }} — {{ fecha }}</h3>
    <table>
        <thead>
            <tr>
                <th>Hora Inicio</th>
                <th>Hora Fin</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for h in horarios %}
            <tr>
                <td>{{ h.hora_inicio }}</td>
                <td>{{ h.hora_fin }}</td>
                <td>
                    {% if h.hora_inicio|stringformat:"s" in reservas_existentes_str %}
                        <span class="badge badge-cancelada">Ocupado</span>
                    {% else %}
                        <span class="badge badge-confirmada">Libre</span>
                    {% endif %}
                </td>
                <td>
                    <a href="{% url 'crear_reserva' %}?cancha={{ cancha_sel.id }}&fecha={{ fecha }}&hora_inicio={{ h.hora_inicio|time:'H:i' }}&hora_fin={{ h.hora_fin|time:'H:i' }}"
                       class="btn btn-primary">
                        Reservar
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% elif cancha_sel %}
<div class="card">
    <p style="color:#888;">No hay horarios disponibles para esta cancha en la fecha seleccionada.</p>
</div>
{% endif %}
{% endblock %}
`

## historial_reservas.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Historial - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Historial de Reservas</h1>

<form method="get" class="filters">
    <div class="form-group">
        <label>Buscar por Usuario</label>
        <input type="text" name="q" class="form-control" placeholder="Nombre o correo..." value="{{ busqueda }}">
    </div>
    <div class="form-group">
        <label>Fecha</label>
        <input type="date" name="fecha" class="form-control" value="{{ fecha }}">
    </div>
    <button type="submit" class="btn btn-outline">Filtrar</button>
</form>

<div class="card" style="padding: 1.5rem;">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Usuario</th>
                <th>Cancha</th>
                <th>Fecha</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            {% for r in reservas %}
            <tr>
                <td>#{{ r.id }}</td>
                <td>{{ r.usuario.nombre }}</td>
                <td>{{ r.cancha.nombre }}</td>
                <td>{{ r.fecha|date:"d/m/Y" }} {{ r.hora_inicio|time:"H:i" }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" style="text-align:center; padding: 2rem;">No se encontraron registros.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## lista_canchas.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Canchas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Canchas Disponibles</h1>

<form method="get" class="filters">
    <div class="form-group">
        <label>Deporte</label>
        <select name="tipo" class="form-control">
            <option value="">Todos</option>
            {% for value, label in tipos %}
                <option value="{{ value }}" {% if filtro_tipo == value %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="form-group">
        <label>Estado</label>
        <select name="estado" class="form-control">
            <option value="">Todos</option>
            {% for value, label in estados %}
                <option value="{{ value }}" {% if filtro_estado == value %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
        </select>
    </div>
    <button type="submit" class="btn btn-outline">Filtrar</button>
</form>

<div class="canchas-grid">
    {% for cancha in canchas %}
    <div class="card">
        <h3>{{ cancha.nombre }}</h3>
        <p>🏅 {{ cancha.get_tipo_deporte_display }}</p>
        <p>📍 {{ cancha.ubicacion }}</p>
        <p><span class="badge badge-{{ cancha.estado }}">{{ cancha.get_estado_display }}</span></p>
        {% if cancha.descripcion %}
            <p style="color:#999; font-size:0.85rem; margin-top:0.5rem;">{{ cancha.descripcion }}</p>
        {% endif %}
        {% if cancha.estado == 'disponible' %}
            <a href="{% url 'disponibilidad' %}?cancha={{ cancha.id }}" class="btn btn-primary" style="margin-top:0.8rem;">
                Ver Disponibilidad
            </a>
        {% endif %}
    </div>
    {% empty %}
    <p style="color:#888;">No se encontraron canchas.</p>
    {% endfor %}
</div>
{% endblock %}
`

## login.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Iniciar Sesión - Polideportivo{% endblock %}

{% block contenido %}
<div class="auth-container">
    <div class="auth-card">
        <h2>🏟️ Polideportivo</h2>

        {% if form.errors %}
            <div class="alert alert-error">
                {% for error in form.non_field_errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label>Correo electrónico</label>
                {{ form.correo }}
            </div>
            <div class="form-group">
                <label>Contraseña</label>
                {{ form.password }}
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%; margin-top:0.5rem;">
                Iniciar Sesión
            </button>
        </form>

        <div class="auth-footer">
            ¿No tienes cuenta? <a href="{% url 'registro' %}">Regístrate aquí</a>
        </div>
    </div>
</div>
{% endblock %}
`

## mis_reservas.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Mis Reservas - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Mis Reservas</h1>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Cancha</th>
                <th>Fecha</th>
                <th>Horario</th>
                <th>Estado</th>
                <th>QR</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
            {% for r in reservas %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.cancha.nombre }}</td>
                <td>{{ r.fecha }}</td>
                <td>{{ r.hora_inicio }} - {{ r.hora_fin }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
                <td style="font-size:0.75rem; color:#7c4dff;">{{ r.codigo_qr|truncatechars:12 }}</td>
                <td>
                    {% if r.estado == 'confirmada' %}
                        <a href="{% url 'cancelar_reserva' r.id %}"
                           class="btn btn-danger"
                           onclick="return confirm('¿Cancelar esta reserva?');">
                            Cancelar
                        </a>
                    {% else %}
                        —
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" style="color:#888; text-align:center;">No tienes reservas.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## perfil.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Perfil - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Mi Perfil</h1>

<div class="card" style="max-width: 600px; margin: 0 auto; padding: 2rem;">
    <h2>{{ usuario.nombre }}</h2>
    <p><strong>Correo:</strong> {{ usuario.correo }}</p>
    <p><strong>Teléfono:</strong> {{ usuario.telefono|default:"No registrado" }}</p>
    <p><strong>Rol:</strong> {{ usuario.get_rol_display }}</p>
    <p><strong>Puntos Wow:</strong> <span class="badge badge-confirmada">{{ usuario.puntos_acumulados }}</span></p>

    <h3 style="margin-top: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">Editar Datos</h3>
    {% if form.errors %}
        <div class="alert alert-error">Por favor revisa los errores.</div>
    {% endif %}
    <form method="post">
        {% csrf_token %}
        {% for field in form.visible_fields %}
        <div class="form-group">
            <label>{{ field.label }}</label>
            {{ field }}
        </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
    </form>
</div>
{% endblock %}
`

## registro.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Registro - Polideportivo{% endblock %}

{% block contenido %}
<div class="auth-container">
    <div class="auth-card">
        <h2>Crear Cuenta</h2>

        {% if form.errors %}
            <div class="alert alert-error">
                {% for field, errors in form.errors.items %}
                    {% for error in errors %}
                        <div>{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <form method="post">
            {% csrf_token %}
            {% for field in form.visible_fields %}
                <div class="form-group">
                    <label>{{ field.label }}</label>
                    {{ field }}
                </div>
            {% endfor %}
            <button type="submit" class="btn btn-primary" style="width:100%; margin-top:0.5rem;">
                Registrarse
            </button>
        </form>

        <div class="auth-footer">
            ¿Ya tienes cuenta? <a href="{% url 'login' %}">Inicia sesión</a>
        </div>
    </div>
</div>
{% endblock %}
`

## reportes.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Reportes - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Reportes y Estadísticas</h1>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">{{ total_reservas }}</div>
        <div class="stat-label">Total Reservas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_confirmadas }}</div>
        <div class="stat-label">Confirmadas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_canceladas }}</div>
        <div class="stat-label">Canceladas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ reservas_no_asistidas }}</div>
        <div class="stat-label">No Asistidas</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_usuarios }}</div>
        <div class="stat-label">Usuarios</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_canchas }}</div>
        <div class="stat-label">Canchas</div>
    </div>
</div>

<div class="card">
    <h3>Últimas Reservas</h3>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Usuario</th>
                <th>Cancha</th>
                <th>Fecha</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            {% for r in ultimas_reservas %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.usuario.nombre }}</td>
                <td>{{ r.cancha.nombre }}</td>
                <td>{{ r.fecha }}</td>
                <td><span class="badge badge-{{ r.estado }}">{{ r.get_estado_display }}</span></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>Historial de Puntos</h3>
    <table>
        <thead>
            <tr>
                <th>Usuario</th>
                <th>Puntos</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Descripción</th>
            </tr>
        </thead>
        <tbody>
            {% for p in historial_puntos %}
            <tr>
                <td>{{ p.usuario.nombre }}</td>
                <td>{{ p.puntos }}</td>
                <td>{{ p.get_tipo_movimiento_display }}</td>
                <td>{{ p.fecha|date:"d/m/Y H:i" }}</td>
                <td>{{ p.descripcion }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
`

## validar_qr.html

`html
{% extends 'reservas/base.html' %}

{% block titulo %}Validar QR - Polideportivo{% endblock %}

{% block contenido %}
<h1 class="page-title">Validar Código QR</h1>

<div class="card" style="max-width: 500px;">
    <form method="post">
        {% csrf_token %}
        <div class="form-group">
            <label>Código QR</label>
            {{ form.codigo_qr }}
        </div>
        <button type="submit" class="btn btn-primary">Verificar</button>
    </form>
</div>

{% if resultado %}
<div class="qr-resultado {% if resultado.valido %}qr-valido{% else %}qr-invalido{% endif %}">
    <h3 style="margin-bottom:0.5rem;">
        {% if resultado.valido %}✅{% else %}❌{% endif %}
        {{ resultado.mensaje }}
    </h3>

    {% if resultado.reserva %}
    <table style="margin-top:1rem; text-align:left;">
        <tr><th>Usuario</th><td>{{ resultado.reserva.usuario.nombre }}</td></tr>
        <tr><th>Cancha</th><td>{{ resultado.reserva.cancha.nombre }}</td></tr>
        <tr><th>Fecha</th><td>{{ resultado.reserva.fecha }}</td></tr>
        <tr><th>Horario</th><td>{{ resultado.reserva.hora_inicio }} - {{ resultado.reserva.hora_fin }}</td></tr>
    </table>
    {% endif %}
</div>
{% endif %}
{% endblock %}
`

