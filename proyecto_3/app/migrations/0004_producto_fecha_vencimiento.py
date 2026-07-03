from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_proveedor_observaciones'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='fecha_vencimiento',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='Fecha de vencimiento'),
        ),
    ]
