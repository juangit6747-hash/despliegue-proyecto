from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_proveedor_productos'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='observaciones',
            field=models.TextField(blank=True, default='', verbose_name='Observaciones'),
        ),
    ]
