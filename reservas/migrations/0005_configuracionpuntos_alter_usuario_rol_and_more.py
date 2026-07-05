

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0004_reserva_lista_invitados'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionPuntos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntos_por_asistencia', models.IntegerField(default=10, help_text='Puntos otorgados al usuario por cada asistencia confirmada.')),
                ('minimo_canje', models.IntegerField(default=50, help_text='Cantidad mínima de puntos requerida para realizar un canje.')),
                ('descripcion_beneficio', models.TextField(default='Canjea tus puntos por bebidas en el bar, minutos adicionales de uso o prioridad en torneos.', help_text='Descripción de los beneficios disponibles al canjear puntos.')),
            ],
            options={
                'verbose_name': 'Configuración de Puntos',
                'verbose_name_plural': 'Configuración de Puntos',
                'db_table': 'configuracion_puntos',
            },
        ),
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(choices=[('usuario', 'Usuario'), ('recepcionista', 'Recepcionista'), ('administrador', 'Administrador'), ('municipio', 'Municipio')], default='usuario', max_length=20),
        ),
    ]
