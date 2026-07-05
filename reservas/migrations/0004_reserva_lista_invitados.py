

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0003_alter_reserva_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='lista_invitados',
            field=models.TextField(blank=True, help_text='Lista de nombres de los acompañantes (ej. Juan, Pedro, Luis)', null=True),
        ),
    ]
