from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0006_reservabloqueo'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancha',
            name='capacidad_jugadores_max',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cancha',
            name='capacidad_jugadores_min',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cancha',
            name='tipo_personalizado',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='cancha',
            name='tipo_deporte',
            field=models.CharField(choices=[('futbol', 'Futbol'), ('baloncesto', 'Baloncesto'), ('voleibol', 'Voleibol'), ('tenis', 'Tenis'), ('otro', 'Otro')], max_length=20),
        ),
    ]
