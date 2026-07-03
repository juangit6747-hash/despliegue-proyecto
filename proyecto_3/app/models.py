from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime


class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('activo',   'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    nombre        = models.CharField(max_length=150)
    documento     = models.CharField(max_length=10, blank=True, default='')
    telefono      = models.CharField(max_length=20)
    email         = models.EmailField(max_length=100)
    direccion     = models.CharField(max_length=200, blank=True, default='')
    estado        = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo', db_index=True)
    fechaRegistro = models.DateField(default=datetime.now)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name        = 'cliente'
        verbose_name_plural = 'clientes'
        db_table            = 'cliente'


class Marca(models.Model):
    idMarca     = models.AutoField(primary_key=True, db_column='idMarca')
    nombreMarca = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.nombreMarca

    class Meta:
        verbose_name        = 'marca'
        verbose_name_plural = 'marcas'
        db_table            = 'marca'


class TipoProductos(models.Model):
    idTipo      = models.AutoField(primary_key=True, db_column='idTipo')
    nombre_tipo = models.CharField(max_length=100, db_column='nombre', db_index=True)
    descripcion = models.TextField(db_column='descripcion', blank=True, default='')

    def __str__(self):
        return self.nombre_tipo

    class Meta:
        verbose_name        = 'tipo_producto'
        verbose_name_plural = 'tipos_productos'
        db_table            = 'tipoproducto'


class UnidadMedida(models.Model):
    """Renombrada a PascalCase. El db_table no cambia, la BD sigue igual."""
    idUnidad      = models.AutoField(primary_key=True, db_column='idUnidad')
    nombre_unidad = models.CharField(max_length=100, db_column='nombreUnidad', db_index=True)
    abreviatura   = models.CharField(max_length=10, db_column='abreviatura', blank=True, default='-')

    def __str__(self):
        return self.nombre_unidad

    class Meta:
        verbose_name        = 'unidad_medida'
        verbose_name_plural = 'unidades_medida'
        db_table            = 'unidadmedida'


# Alias de compatibilidad para que las vistas/forms existentes no rompan
unidad_medida = UnidadMedida


class Producto(models.Model):
    idProducto    = models.AutoField(primary_key=True, db_column='idProducto')
    idTipo        = models.ForeignKey(TipoProductos, on_delete=models.CASCADE, db_column='idTipo')
    idMarca       = models.ForeignKey(Marca,         on_delete=models.CASCADE, db_column='idMarca')
    idUnidad      = models.ForeignKey(UnidadMedida,  on_delete=models.CASCADE, db_column='idUnidad')
    nombre        = models.CharField(max_length=255)
    precio        = models.DecimalField(max_digits=10, decimal_places=2)
    stock         = models.IntegerField(default=0)
    # ── Campo nuevo: código de barras EAN/UPC ─────────────────────
    codigo_barras = models.CharField(
        max_length=50,
        blank=True,
        default='',
        db_index=True,
        verbose_name='Código de barras',
    )
    # ── Campo nuevo: fecha de vencimiento (para alertas reutilizables) ──
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Fecha de vencimiento',
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name        = 'producto'
        verbose_name_plural = 'productos'
        db_table            = 'producto'
        unique_together     = [('nombre', 'idMarca', 'idTipo')]


class Proveedor(models.Model):
    id            = models.AutoField(primary_key=True, db_column='id')
    nombre        = models.CharField(max_length=150)
    telefono      = models.CharField(max_length=20)
    email         = models.EmailField(max_length=100)
    envio         = models.IntegerField(default=0)
    fechaRegistro = models.DateField(default=datetime.now)
    productos     = models.ManyToManyField(
        'Producto',
        blank=True,
        related_name='proveedores',
        db_table='proveedor_producto',
        verbose_name='Productos que suministra',
    )
    observaciones = models.TextField(blank=True, default='', verbose_name='Observaciones')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name        = 'proveedor'
        verbose_name_plural = 'proveedores'
        db_table            = 'proveedor'


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('Completada', 'Completada'),
        ('Pendiente',  'Pendiente'),
    ]
    cliente = models.CharField(max_length=100)
    fecha   = models.DateTimeField(auto_now_add=True)
    total   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado  = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"

    class Meta:
        verbose_name        = 'venta'
        verbose_name_plural = 'ventas'
        db_table            = 'venta'
        ordering            = ['-fecha']


class DetalleVenta(models.Model):
    venta           = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto        = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, db_column='producto_id')
    producto_nombre = models.CharField(max_length=255)
    precio          = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad        = models.IntegerField(default=1)

    @property
    def subtotal(self):
        return self.precio * self.cantidad

    @property
    def cantidad_devuelta(self):
        return self.devoluciones.aggregate(total=Sum('cantidad'))['total'] or 0

    @property
    def cantidad_disponible_devolucion(self):
        return self.cantidad - self.cantidad_devuelta

    def __str__(self):
        return f"{self.producto_nombre} x{self.cantidad}"

    class Meta:
        db_table = 'detalle_venta'


class Compra(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente',  'Pendiente'),
        ('Completada', 'Completada'),
    ]
    idCompra        = models.AutoField(primary_key=True, db_column='id')
    fechaCompra     = models.DateField(default=datetime.now, db_column='fecha')
    estado          = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Pendiente')
    cantidad        = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario         = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        related_name='compras',
        verbose_name='Usuario',
    )
    Producto  = models.ForeignKey(Producto,  on_delete=models.SET_NULL, null=True, blank=True, db_column='Producto_id')
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE,              db_column='Proveedor_id')

    @property
    def total(self):
        return self.cantidad * self.precio_unitario

    @property
    def cantidad_devuelta(self):
        return self.devoluciones.aggregate(total=Sum('cantidad'))['total'] or 0

    @property
    def cantidad_disponible_devolucion(self):
        return self.cantidad - self.cantidad_devuelta

    def __str__(self):
        return f"Compra #{self.idCompra}"

    class Meta:
        db_table            = 'compra'
        verbose_name        = 'compra'
        verbose_name_plural = 'compras'
        ordering            = ['-fechaCompra']


class Pedidos(models.Model):
    usuario      = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        verbose_name='Usuario',
    )
    id_cliente   = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateField()
    estado_pedido = models.CharField(max_length=150)
    total        = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido {self.id}"

    class Meta:
        verbose_name        = 'pedido'
        verbose_name_plural = 'pedidos'
        db_table            = 'pedidos'
        ordering            = ['-fecha_pedido']


class Reporte(models.Model):
    idCompra  = models.ForeignKey(Compra,  on_delete=models.CASCADE, db_column='idCompra',  null=True, blank=True)
    idPedido  = models.ForeignKey(Pedidos, on_delete=models.CASCADE, db_column='idPedido',  null=True, blank=True)
    idVenta   = models.ForeignKey(Venta,   on_delete=models.CASCADE, db_column='idVenta',   null=True, blank=True)
    usuario   = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id',
        verbose_name='Usuario',
    )
    fechaReporte = models.DateTimeField()
    descripcion  = models.TextField()

    def __str__(self):
        return f"Reporte {self.id}"

    class Meta:
        verbose_name        = 'reporte'
        verbose_name_plural = 'reportes'
        db_table            = 'reporte'


class NotificacionEmail(models.Model):
    TIPO_CHOICES = [
        ('alerta',  'Alerta'),
        ('info',    'Información'),
        ('error',   'Error'),
        ('success', 'Éxito'),
    ]
    usuario        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones_email')
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES, default='info')
    asunto         = models.CharField(max_length=255)
    mensaje        = models.TextField()
    leida          = models.BooleanField(default=False)
    enviada        = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio    = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.asunto} - {self.usuario.username}"

    class Meta:
        verbose_name        = 'notificación email'
        verbose_name_plural = 'notificaciones email'
        db_table            = 'notificacion_email'
        ordering            = ['-fecha_creacion']

# ══════════════════════════════════════════════════════
# DEVOLUCIONES
# ══════════════════════════════════════════════════════

class DevolucionCompra(models.Model):
    """
    Devolución parcial o total de una compra a un proveedor.
    Ej: se compraron 10 yogures y 3 llegaron vencidos/dañados.
    """
    MOTIVO_CHOICES = [
        ('vencido', 'Producto vencido'),
        ('danado',  'Producto dañado'),
        ('otro',    'Otro motivo'),
    ]
    compra        = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='devoluciones')
    cantidad      = models.PositiveIntegerField()
    motivo        = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='vencido')
    observaciones = models.TextField(blank=True, default='')
    fecha         = models.DateTimeField(auto_now_add=True)
    usuario       = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='devoluciones_compra', verbose_name='Usuario',
    )

    def __str__(self):
        return f"Devolución compra #{self.compra_id} — {self.cantidad} uds."

    class Meta:
        verbose_name        = 'devolución de compra'
        verbose_name_plural  = 'devoluciones de compra'
        db_table             = 'devolucion_compra'
        ordering              = ['-fecha']


class DevolucionVenta(models.Model):
    """
    Devolución parcial o total de un producto vendido a un cliente.
    Ej: se vendieron 5 yogures y el cliente devuelve 2 porque vencieron.
    Si el motivo es 'vencido' o 'danado', NO se repone el stock (se descarta).
    Para cualquier otro motivo, el producto vuelve a estar disponible.
    """
    MOTIVO_CHOICES = [
        ('vencido',         'Producto vencido'),
        ('danado',          'Producto dañado'),
        ('arrepentimiento', 'Cliente se arrepintió'),
        ('otro',            'Otro motivo'),
    ]
    detalle           = models.ForeignKey(DetalleVenta, on_delete=models.CASCADE, related_name='devoluciones')
    cantidad          = models.PositiveIntegerField()
    motivo            = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='vencido')
    observaciones     = models.TextField(blank=True, default='')
    restablecer_stock = models.BooleanField(default=False, verbose_name='¿Vuelve al inventario?')
    fecha             = models.DateTimeField(auto_now_add=True)
    usuario           = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='devoluciones_venta', verbose_name='Usuario',
    )

    def __str__(self):
        return f"Devolución venta #{self.detalle.venta_id} — {self.cantidad} uds."

    class Meta:
        verbose_name        = 'devolución de venta'
        verbose_name_plural  = 'devoluciones de venta'
        db_table             = 'devolucion_venta'
        ordering              = ['-fecha']
