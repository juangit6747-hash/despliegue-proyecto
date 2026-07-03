"""
Sistema de notificaciones — El Despecho
Cubre: stock, compras, ventas, clientes, proveedores y resumen diario.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from app.models import NotificacionEmail


# ══════════════════════════════════════════════════════
# NÚCLEO
# ══════════════════════════════════════════════════════

def _crear_notif(usuario, asunto, mensaje, tipo='info'):
    """Crea la notificación en BD siempre. Devuelve el objeto."""
    return NotificacionEmail.objects.create(
        usuario=usuario,
        asunto=asunto,
        mensaje=mensaje,
        tipo=tipo,
    )


def _enviar_email(notif):
    """Intenta enviar el email asociado a una notificación ya guardada."""
    if not notif.usuario.email:
        return False
    try:
        send_mail(
            subject=notif.asunto,
            message=notif.mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.usuario.email],
            fail_silently=False,
        )
        notif.enviada = True
        notif.fecha_envio = timezone.now()
        notif.save()
        return True
    except Exception as e:
        print(f"[Notif] Error enviando email a {notif.usuario.email}: {e}")
        return False


def enviar_notificacion_email(usuario, asunto, mensaje, tipo='info'):
    """Crea notificación en BD y envía email si el usuario tiene correo."""
    notif = _crear_notif(usuario, asunto, mensaje, tipo)
    _enviar_email(notif)
    return notif


def _notificar_a_todos(asunto, mensaje, tipo='info', excluir=None):
    """
    Crea y envía notificación a todos los usuarios activos.
    excluir: instancia User a omitir (opcional).
    """
    usuarios = User.objects.filter(is_active=True)
    if excluir:
        usuarios = usuarios.exclude(pk=excluir.pk)
    for u in usuarios:
        notif = _crear_notif(u, asunto, mensaje, tipo)
        _enviar_email(notif)


# ══════════════════════════════════════════════════════
# PRODUCTOS / STOCK
# ══════════════════════════════════════════════════════

def notificacion_stock_bajo(producto):
    """Stock ≤ 5 unidades."""
    if producto.stock == 0:
        asunto  = f"❌ AGOTADO: {producto.nombre}"
        mensaje = (
            f"El producto «{producto.nombre}» se ha agotado completamente.\n"
            f"Marca: {producto.idMarca.nombreMarca}\n"
            f"Tipo: {producto.idTipo.nombre_tipo}\n\n"
            f"Reabastece cuanto antes para no perder ventas."
        )
        tipo = 'error'
    else:
        asunto  = f"⚠️ Stock bajo: {producto.nombre} ({producto.stock} uds.)"
        mensaje = (
            f"El producto «{producto.nombre}» tiene stock bajo.\n"
            f"Stock actual: {producto.stock} unidades\n"
            f"Marca: {producto.idMarca.nombreMarca}\n"
            f"Tipo: {producto.idTipo.nombre_tipo}\n\n"
            f"Se recomienda reabastecer pronto."
        )
        tipo = 'alerta'

    _notificar_a_todos(asunto, mensaje, tipo)


def notificacion_producto_creado(producto, usuario):
    """Nuevo producto registrado en el catálogo."""
    asunto  = f"✅ Nuevo producto: {producto.nombre}"
    mensaje = (
        f"Se ha registrado un nuevo producto en el inventario.\n\n"
        f"Nombre:  {producto.nombre}\n"
        f"Precio:  ${producto.precio:,.2f}\n"
        f"Stock:   {producto.stock} unidades\n"
        f"Marca:   {producto.idMarca.nombreMarca}\n"
        f"Tipo:    {producto.idTipo.nombre_tipo}\n"
        f"Unidad:  {producto.idUnidad.nombre_unidad}\n\n"
        f"Registrado por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'success', excluir=usuario)


def notificacion_producto_editado(producto, usuario):
    """Producto modificado."""
    asunto  = f"✏️ Producto actualizado: {producto.nombre}"
    mensaje = (
        f"El producto «{producto.nombre}» ha sido modificado.\n\n"
        f"Estado actual:\n"
        f"Precio: ${producto.precio:,.2f}\n"
        f"Stock:  {producto.stock} unidades\n\n"
        f"Modificado por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'info')


def notificacion_producto_eliminado(nombre_producto, usuario):
    """Producto eliminado del catálogo."""
    asunto  = f"🗑️ Producto eliminado: {nombre_producto}"
    mensaje = (
        f"El producto «{nombre_producto}» ha sido eliminado del inventario.\n\n"
        f"Eliminado por: {usuario.get_full_name() or usuario.username}\n"
        f"Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _notificar_a_todos(asunto, mensaje, 'alerta', excluir=usuario)


# ══════════════════════════════════════════════════════
# COMPRAS
# ══════════════════════════════════════════════════════

def notificacion_compra_creada(compra):
    """Nueva compra registrada."""
    producto_nombre = compra.Producto.nombre if compra.Producto else 'Sin asignar'
    asunto  = f"🛒 Nueva compra #{compra.idCompra}: {producto_nombre}"
    mensaje = (
        f"Se ha registrado una nueva compra.\n\n"
        f"Compra #:    {compra.idCompra}\n"
        f"Proveedor:   {compra.Proveedor.nombre}\n"
        f"Producto:    {producto_nombre}\n"
        f"Cantidad:    {compra.cantidad}\n"
        f"P. Unitario: ${compra.precio_unitario:,.2f}\n"
        f"Total:       ${compra.total:,.2f}\n"
        f"Estado:      {compra.estado}\n"
        f"Fecha:       {compra.fechaCompra.strftime('%d/%m/%Y')}\n\n"
        f"Registrada por: {compra.usuario.get_full_name() or compra.usuario.username if compra.usuario else 'Sistema'}"
    )
    _notificar_a_todos(asunto, mensaje, 'info', excluir=compra.usuario)


def notificacion_compra_completada(compra):
    """Compra marcada como completada — stock sumado."""
    producto_nombre = compra.Producto.nombre if compra.Producto else 'Sin asignar'
    asunto  = f"✅ Compra completada #{compra.idCompra}: {producto_nombre}"
    mensaje = (
        f"La compra #{compra.idCompra} ha sido completada y el stock fue actualizado.\n\n"
        f"Producto:  {producto_nombre}\n"
        f"Cantidad:  +{compra.cantidad} unidades sumadas al stock\n"
        f"Total:     ${compra.total:,.2f}\n"
        f"Proveedor: {compra.Proveedor.nombre}"
    )
    _notificar_a_todos(asunto, mensaje, 'success')


def notificacion_compra_eliminada(compra, usuario):
    """Compra eliminada."""
    producto_nombre = compra.Producto.nombre if compra.Producto else 'Sin asignar'
    asunto  = f"🗑️ Compra #{compra.idCompra} eliminada"
    mensaje = (
        f"La compra #{compra.idCompra} ha sido eliminada.\n\n"
        f"Producto:  {producto_nombre}\n"
        f"Proveedor: {compra.Proveedor.nombre}\n"
        f"Total:     ${compra.total:,.2f}\n\n"
        f"Eliminada por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'alerta', excluir=usuario)


def notificacion_compra_proxima_vencer(compra):
    """Compra próxima a vencer o vencida."""
    producto_nombre = compra.Producto.nombre if compra.Producto else 'Sin asignar'
    dias = (compra.fechaCompra - timezone.now().date()).days
    if dias <= 0:
        asunto  = f"🚨 Compra vencida #{compra.idCompra}: {producto_nombre}"
        mensaje = (
            f"La compra #{compra.idCompra} ha vencido hace {abs(dias)} día(s).\n\n"
            f"Producto:  {producto_nombre}\n"
            f"Proveedor: {compra.Proveedor.nombre}\n"
            f"Fecha:     {compra.fechaCompra.strftime('%d/%m/%Y')}"
        )
        tipo = 'error'
    else:
        asunto  = f"⏰ Compra vence en {dias} día(s): {producto_nombre}"
        mensaje = (
            f"La compra #{compra.idCompra} vence en {dias} día(s).\n\n"
            f"Producto:  {producto_nombre}\n"
            f"Proveedor: {compra.Proveedor.nombre}\n"
            f"Fecha:     {compra.fechaCompra.strftime('%d/%m/%Y')}"
        )
        tipo = 'alerta'
    _notificar_a_todos(asunto, mensaje, tipo)


# ══════════════════════════════════════════════════════
# VENTAS
# ══════════════════════════════════════════════════════

def notificacion_venta_completada(venta):
    """Venta marcada como completada."""
    asunto  = f"💰 Venta completada #{venta.id}: {venta.cliente}"
    mensaje = (
        f"La venta #{venta.id} ha sido completada.\n\n"
        f"Cliente: {venta.cliente}\n"
        f"Total:   ${venta.total:,.2f}\n"
        f"Fecha:   {venta.fecha.strftime('%d/%m/%Y %H:%M')}\n\n"
        f"Productos vendidos:\n"
        + "\n".join(
            f"  • {d.producto_nombre} x{d.cantidad} — ${d.subtotal:,.2f}"
            for d in venta.detalles.all()
        )
    )
    _notificar_a_todos(asunto, mensaje, 'success')


def notificacion_venta_creada(venta, usuario):
    """Nueva venta registrada."""
    asunto  = f"🧾 Nueva venta #{venta.id}: {venta.cliente}"
    mensaje = (
        f"Se ha registrado una nueva venta.\n\n"
        f"Cliente: {venta.cliente}\n"
        f"Total:   ${venta.total:,.2f}\n"
        f"Estado:  {venta.estado}\n"
        f"Fecha:   {venta.fecha.strftime('%d/%m/%Y %H:%M')}\n\n"
        f"Registrada por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'info')


def notificacion_venta_eliminada(venta, usuario):
    """Venta eliminada."""
    asunto  = f"🗑️ Venta #{venta.id} eliminada"
    mensaje = (
        f"La venta #{venta.id} ha sido eliminada y el stock fue restaurado.\n\n"
        f"Cliente: {venta.cliente}\n"
        f"Total:   ${venta.total:,.2f}\n\n"
        f"Eliminada por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'alerta', excluir=usuario)


# ══════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════

def notificacion_cliente_creado(cliente, usuario):
    asunto  = f"👤 Nuevo cliente: {cliente.nombre}"
    mensaje = (
        f"Se ha registrado un nuevo cliente.\n\n"
        f"Nombre:    {cliente.nombre}\n"
        f"Teléfono:  {cliente.telefono}\n"
        f"Email:     {cliente.email}\n"
        f"Dirección: {cliente.direccion or 'No especificada'}\n\n"
        f"Registrado por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'info')


def notificacion_cliente_inactivo(cliente, usuario):
    asunto  = f"⚠️ Cliente desactivado: {cliente.nombre}"
    mensaje = (
        f"El cliente «{cliente.nombre}» ha sido marcado como inactivo.\n\n"
        f"Desactivado por: {usuario.get_full_name() or usuario.username}\n"
        f"Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _notificar_a_todos(asunto, mensaje, 'alerta')


# ══════════════════════════════════════════════════════
# PROVEEDORES
# ══════════════════════════════════════════════════════

def notificacion_proveedor_creado(proveedor, usuario):
    asunto  = f"🏭 Nuevo proveedor: {proveedor.nombre}"
    mensaje = (
        f"Se ha registrado un nuevo proveedor.\n\n"
        f"Nombre:    {proveedor.nombre}\n"
        f"Teléfono:  {proveedor.telefono}\n"
        f"Email:     {proveedor.email}\n\n"
        f"Registrado por: {usuario.get_full_name() or usuario.username}"
    )
    _notificar_a_todos(asunto, mensaje, 'info')


def notificacion_proveedor_eliminado(nombre_proveedor, usuario):
    asunto  = f"🗑️ Proveedor eliminado: {nombre_proveedor}"
    mensaje = (
        f"El proveedor «{nombre_proveedor}» ha sido eliminado del sistema.\n\n"
        f"Eliminado por: {usuario.get_full_name() or usuario.username}\n"
        f"Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _notificar_a_todos(asunto, mensaje, 'alerta', )