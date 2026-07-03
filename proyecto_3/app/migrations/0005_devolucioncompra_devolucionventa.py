import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_producto_fecha_vencimiento'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevolucionCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('motivo', models.CharField(choices=[('vencido', 'Producto vencido'), ('danado', 'Producto dañado'), ('otro', 'Otro motivo')], default='vencido', max_length=20)),
                ('observaciones', models.TextField(blank=True, default='')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devoluciones', to='app.compra')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones_compra', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'devolución de compra',
                'verbose_name_plural': 'devoluciones de compra',
                'db_table': 'devolucion_compra',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DevolucionVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('motivo', models.CharField(choices=[('vencido', 'Producto vencido'), ('danado', 'Producto dañado'), ('arrepentimiento', 'Cliente se arrepintió'), ('otro', 'Otro motivo')], default='vencido', max_length=20)),
                ('observaciones', models.TextField(blank=True, default='')),
                ('restablecer_stock', models.BooleanField(default=False, verbose_name='¿Vuelve al inventario?')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('detalle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devoluciones', to='app.detalleventa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones_venta', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'devolución de venta',
                'verbose_name_plural': 'devoluciones de venta',
                'db_table': 'devolucion_venta',
                'ordering': ['-fecha'],
            },
        ),
    ]
