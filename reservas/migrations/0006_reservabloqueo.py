
from django.db import migrations, models
import django.db.models.deletion


def crear_bloqueos_reservas_activas(apps, schema_editor):
    Reserva = apps.get_model('reservas', 'Reserva')
    ReservaBloqueo = apps.get_model('reservas', 'ReservaBloqueo')
    db_alias = schema_editor.connection.alias
    vistos = set()

    reservas = (
        Reserva.objects.using(db_alias)
        .filter(estado__in=['confirmada', 'asistida'])
        .order_by('fecha_creacion', 'id')
    )

    for reserva in reservas:
        clave = (
            reserva.cancha_id,
            reserva.fecha,
            reserva.hora_inicio,
            reserva.hora_fin,
        )
        if clave in vistos:
            continue
        vistos.add(clave)
        ReservaBloqueo.objects.using(db_alias).create(
            cancha_id=reserva.cancha_id,
            fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
            reserva_id=reserva.id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0005_configuracionpuntos_alter_usuario_rol_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservaBloqueo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('cancha', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bloqueos_reserva', to='reservas.cancha')),
                ('reserva', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bloqueo', to='reservas.reserva')),
            ],
            options={
                'verbose_name': 'Bloqueo de Reserva',
                'verbose_name_plural': 'Bloqueos de Reserva',
                'db_table': 'reserva_bloqueo',
            },
        ),
        migrations.AddConstraint(
            model_name='reservabloqueo',
            constraint=models.UniqueConstraint(fields=('cancha', 'fecha', 'hora_inicio', 'hora_fin'), name='unique_bloqueo_franja_reserva'),
        ),
        migrations.RunPython(crear_bloqueos_reservas_activas, migrations.RunPython.noop),
    ]