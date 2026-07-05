

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='reserva',
            name='unique_reserva_cancha_horario',
        ),
    ]
