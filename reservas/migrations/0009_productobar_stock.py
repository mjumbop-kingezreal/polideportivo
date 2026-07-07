from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0008_productobar_alter_configuracionpuntos_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productobar',
            name='stock',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Cantidad disponible. Si se deja vacio, el producto no tendra limite de stock.',
                null=True,
            ),
        ),
    ]
